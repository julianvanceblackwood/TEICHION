#!/usr/bin/env python3
"""
Independent reference encoder for TEICHION Canonical Seal Record V1.

This module defines deterministic serialization only.

It does NOT:
- compute a TEICHION cryptographic seal;
- implement HMAC-SHA-256;
- manage device keys;
- establish trusted epoch persistence;
- prove hardware authenticity.

Its purpose is to provide an implementation independent from future RTL so
byte-level interoperability can be checked before cryptographic integration.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SEAL_DOMAIN = b"TEICHION-SEAL-V1"
RECEIPT_DOMAIN = b"TEICHION-RCPT-V1"

FORMAT_VERSION = 0x01
RECORD_KIND_EVIDENCE = 0x01
ALGORITHM_ID_HMAC_SHA256 = 0x01
FLAGS_V1 = 0x00

SEAL_SIZE = 32
FIXED_PREFIX_SIZE = 72
RECEIPT_SIZE = 104
GEN1_MAX_PAYLOAD = 4096

_U64_MAX = (1 << 64) - 1
_U32_MAX = (1 << 32) - 1

_HEADER = struct.Struct(">BBBBQQI")


class CanonicalRecordError(ValueError):
    """Raised when a value cannot be represented as a valid V1 record."""


@dataclass(frozen=True)
class CanonicalRecordV1:
    epoch: int
    sequence: int
    payload: bytes
    previous_seal: bytes

    def encode(self) -> bytes:
        return encode_record(
            epoch=self.epoch,
            sequence=self.sequence,
            payload=self.payload,
            previous_seal=self.previous_seal,
        )


@dataclass(frozen=True)
class ReceiptV1:
    epoch: int
    sequence: int
    payload_length: int
    previous_seal: bytes
    seal: bytes

    def encode(self) -> bytes:
        return encode_receipt(
            epoch=self.epoch,
            sequence=self.sequence,
            payload_length=self.payload_length,
            previous_seal=self.previous_seal,
            seal=self.seal,
        )


def _require_uint(name: str, value: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise CanonicalRecordError(f"{name} must be an integer")

    if not 0 <= value <= maximum:
        raise CanonicalRecordError(
            f"{name} must be in range 0..{maximum}, got {value}"
        )

    return value


def _require_bytes(name: str, value: bytes | bytearray | memoryview) -> bytes:
    if not isinstance(value, (bytes, bytearray, memoryview)):
        raise CanonicalRecordError(f"{name} must be bytes-like")

    return bytes(value)


def _require_exact_bytes(
    name: str,
    value: bytes | bytearray | memoryview,
    expected_length: int,
) -> bytes:
    result = _require_bytes(name, value)

    if len(result) != expected_length:
        raise CanonicalRecordError(
            f"{name} must be exactly {expected_length} bytes, got {len(result)}"
        )

    return result


def encode_record(
    *,
    epoch: int,
    sequence: int,
    payload: bytes | bytearray | memoryview,
    previous_seal: bytes | bytearray | memoryview,
) -> bytes:
    """
    Encode one canonical V1 seal record.

    Hardware-owned fields:
        epoch
        sequence
        previous_seal

    Upstream-supplied field:
        payload

    This function accepts all fields explicitly because it is a reference
    serializer, not the hardware trust boundary. Production host software
    must not be permitted to authoritatively choose hardware-owned values.
    """

    epoch = _require_uint("epoch", epoch, _U64_MAX)
    sequence = _require_uint("sequence", sequence, _U64_MAX)

    payload_bytes = _require_bytes("payload", payload)

    if len(payload_bytes) > GEN1_MAX_PAYLOAD:
        raise CanonicalRecordError(
            f"payload exceeds GEN1_MAX_PAYLOAD={GEN1_MAX_PAYLOAD}: "
            f"{len(payload_bytes)} bytes"
        )

    if len(payload_bytes) > _U32_MAX:
        raise CanonicalRecordError("payload cannot be represented by u32 length")

    previous_seal_bytes = _require_exact_bytes(
        "previous_seal",
        previous_seal,
        SEAL_SIZE,
    )

    header = _HEADER.pack(
        FORMAT_VERSION,
        RECORD_KIND_EVIDENCE,
        ALGORITHM_ID_HMAC_SHA256,
        FLAGS_V1,
        epoch,
        sequence,
        len(payload_bytes),
    )

    encoded = SEAL_DOMAIN + header + previous_seal_bytes + payload_bytes

    expected_length = FIXED_PREFIX_SIZE + len(payload_bytes)

    if len(encoded) != expected_length:
        raise AssertionError(
            f"internal encoding length error: "
            f"expected {expected_length}, got {len(encoded)}"
        )

    return encoded


def decode_record(encoded: bytes | bytearray | memoryview) -> CanonicalRecordV1:
    """
    Decode and strictly validate one canonical V1 record.

    There is no normalization path: unsupported constants, reserved flags,
    length mismatches, oversized payloads, truncation, or trailing bytes are
    rejected.
    """

    data = _require_bytes("encoded", encoded)

    if len(data) < FIXED_PREFIX_SIZE:
        raise CanonicalRecordError(
            f"record is truncated: minimum {FIXED_PREFIX_SIZE} bytes required"
        )

    if data[:16] != SEAL_DOMAIN:
        raise CanonicalRecordError("unsupported seal-record domain")

    (
        format_version,
        record_kind,
        algorithm_id,
        flags,
        epoch,
        sequence,
        payload_length,
    ) = _HEADER.unpack(data[16:40])

    if format_version != FORMAT_VERSION:
        raise CanonicalRecordError(
            f"unsupported format_version: 0x{format_version:02x}"
        )

    if record_kind != RECORD_KIND_EVIDENCE:
        raise CanonicalRecordError(
            f"unsupported record_kind: 0x{record_kind:02x}"
        )

    if algorithm_id != ALGORITHM_ID_HMAC_SHA256:
        raise CanonicalRecordError(
            f"unsupported algorithm_id: 0x{algorithm_id:02x}"
        )

    if flags != FLAGS_V1:
        raise CanonicalRecordError(f"reserved V1 flags are non-zero: 0x{flags:02x}")

    if payload_length > GEN1_MAX_PAYLOAD:
        raise CanonicalRecordError(
            f"payload_length exceeds GEN1_MAX_PAYLOAD={GEN1_MAX_PAYLOAD}"
        )

    expected_length = FIXED_PREFIX_SIZE + payload_length

    if len(data) != expected_length:
        raise CanonicalRecordError(
            f"length mismatch: expected {expected_length}, got {len(data)}"
        )

    previous_seal = data[40:72]
    payload = data[72:]

    return CanonicalRecordV1(
        epoch=epoch,
        sequence=sequence,
        payload=payload,
        previous_seal=previous_seal,
    )


def encode_receipt(
    *,
    epoch: int,
    sequence: int,
    payload_length: int,
    previous_seal: bytes | bytearray | memoryview,
    seal: bytes | bytearray | memoryview,
) -> bytes:
    """
    Encode the proposed V1 verifier-facing receipt.

    The receipt is not itself a public-verification proof. Under the target
    HMAC design, verification authority still depends on the future key model.
    """

    epoch = _require_uint("epoch", epoch, _U64_MAX)
    sequence = _require_uint("sequence", sequence, _U64_MAX)
    payload_length = _require_uint("payload_length", payload_length, _U32_MAX)

    if payload_length > GEN1_MAX_PAYLOAD:
        raise CanonicalRecordError(
            f"payload_length exceeds GEN1_MAX_PAYLOAD={GEN1_MAX_PAYLOAD}"
        )

    previous_seal_bytes = _require_exact_bytes(
        "previous_seal",
        previous_seal,
        SEAL_SIZE,
    )
    seal_bytes = _require_exact_bytes("seal", seal, SEAL_SIZE)

    header = _HEADER.pack(
        FORMAT_VERSION,
        RECORD_KIND_EVIDENCE,
        ALGORITHM_ID_HMAC_SHA256,
        FLAGS_V1,
        epoch,
        sequence,
        payload_length,
    )

    encoded = (
        RECEIPT_DOMAIN
        + header
        + previous_seal_bytes
        + seal_bytes
    )

    if len(encoded) != RECEIPT_SIZE:
        raise AssertionError(
            f"internal receipt length error: expected {RECEIPT_SIZE}, "
            f"got {len(encoded)}"
        )

    return encoded


def fixture_fingerprint(encoded: bytes | bytearray | memoryview) -> str:
    """
    Return SHA-256 used only as a deterministic fixture fingerprint.

    This value is NOT a TEICHION seal.
    """

    data = _require_bytes("encoded", encoded)
    return hashlib.sha256(data).hexdigest()


def verify_vector_document(document: dict[str, Any]) -> list[str]:
    """
    Verify positive serialization fixtures from a loaded vector document.

    Returns a list of human-readable errors. An empty list means every
    positive fixture matched exactly.
    """

    errors: list[str] = []

    vectors = document.get("positive_vectors")

    if not isinstance(vectors, list):
        return ["positive_vectors must be a list"]

    for vector in vectors:
        vector_id = str(vector.get("id", "<unnamed>"))

        try:
            payload = bytes.fromhex(str(vector["payload_hex"]))
            previous_seal = bytes.fromhex(str(vector["previous_seal_hex"]))

            encoded = encode_record(
                epoch=int(vector["epoch"]),
                sequence=int(vector["sequence"]),
                payload=payload,
                previous_seal=previous_seal,
            )

            expected_hex = str(vector["canonical_hex"]).lower()
            expected_length = int(vector["canonical_length"])
            expected_fingerprint = str(
                vector["sha256_fixture_fingerprint"]
            ).lower()

            if encoded.hex() != expected_hex:
                errors.append(f"{vector_id}: canonical_hex mismatch")

            if len(encoded) != expected_length:
                errors.append(
                    f"{vector_id}: canonical_length mismatch "
                    f"(expected {expected_length}, got {len(encoded)})"
                )

            actual_fingerprint = fixture_fingerprint(encoded)

            if actual_fingerprint != expected_fingerprint:
                errors.append(
                    f"{vector_id}: fixture fingerprint mismatch"
                )

            decoded = decode_record(encoded)

            if decoded.encode() != encoded:
                errors.append(f"{vector_id}: decode/encode round trip mismatch")

        except (KeyError, TypeError, ValueError, CanonicalRecordError) as exc:
            errors.append(f"{vector_id}: {exc}")

    return errors


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)

    if not isinstance(document, dict):
        raise CanonicalRecordError("vector document root must be an object")

    return document


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify TEICHION Canonical Seal Record V1 fixtures."
    )
    parser.add_argument(
        "--vectors",
        type=Path,
        default=Path("test_vectors/canonical_seal_record_v1.json"),
        help="path to the V1 JSON vector document",
    )

    args = parser.parse_args()

    document = _load_json(args.vectors)
    errors = verify_vector_document(document)

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    vector_count = len(document.get("positive_vectors", []))
    print(
        "PASS: "
        f"{vector_count} canonical V1 serialization vectors reproduced exactly"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
