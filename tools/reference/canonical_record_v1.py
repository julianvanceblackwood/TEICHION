#!/usr/bin/env python3
"""
Independent reference encoder for TEICHION Canonical Seal Record V1.

This module defines deterministic serialization and strict structural
validation only.

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


def _decode_single_byte_hex(name: str, value: object) -> int:
    if not isinstance(value, str):
        raise CanonicalRecordError(f"{name} must be a hexadecimal string")

    try:
        decoded = bytes.fromhex(value)
    except ValueError as exc:
        raise CanonicalRecordError(f"{name} is not valid hexadecimal") from exc

    if len(decoded) != 1:
        raise CanonicalRecordError(f"{name} must encode exactly one byte")

    return decoded[0]


def _payload_from_vector(vector: dict[str, Any]) -> bytes:
    has_hex = "payload_hex" in vector
    has_repeat = "payload_repeat" in vector

    if has_hex == has_repeat:
        raise CanonicalRecordError(
            "vector must define exactly one of payload_hex or payload_repeat"
        )

    if has_hex:
        payload_hex = vector["payload_hex"]

        if not isinstance(payload_hex, str):
            raise CanonicalRecordError("payload_hex must be a string")

        try:
            return bytes.fromhex(payload_hex)
        except ValueError as exc:
            raise CanonicalRecordError("payload_hex is invalid") from exc

    repeat = vector["payload_repeat"]

    if not isinstance(repeat, dict):
        raise CanonicalRecordError("payload_repeat must be an object")

    byte_value = _decode_single_byte_hex(
        "payload_repeat.byte_hex",
        repeat.get("byte_hex"),
    )
    count = _require_uint(
        "payload_repeat.count",
        repeat.get("count"),
        _U32_MAX,
    )

    return bytes([byte_value]) * count


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

    encoded = RECEIPT_DOMAIN + header + previous_seal_bytes + seal_bytes

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


def _encode_positive_vector(vector: dict[str, Any]) -> bytes:
    payload = _payload_from_vector(vector)

    payload_length = _require_uint(
        "payload_length",
        vector.get("payload_length"),
        _U32_MAX,
    )

    if payload_length != len(payload):
        raise CanonicalRecordError(
            f"payload_length says {payload_length}, actual payload is "
            f"{len(payload)} bytes"
        )

    previous_seal_hex = vector.get("previous_seal_hex")

    if not isinstance(previous_seal_hex, str):
        raise CanonicalRecordError("previous_seal_hex must be a string")

    try:
        previous_seal = bytes.fromhex(previous_seal_hex)
    except ValueError as exc:
        raise CanonicalRecordError("previous_seal_hex is invalid") from exc

    return encode_record(
        epoch=_require_uint("epoch", vector.get("epoch"), _U64_MAX),
        sequence=_require_uint("sequence", vector.get("sequence"), _U64_MAX),
        payload=payload,
        previous_seal=previous_seal,
    )


def _mutate_from_negative_vector(
    vector: dict[str, Any],
    positive_by_id: dict[str, bytes],
) -> bytes:
    base_id = vector.get("base")

    if not isinstance(base_id, str) or base_id not in positive_by_id:
        raise CanonicalRecordError("negative vector references unknown base")

    mutated = bytearray(positive_by_id[base_id])
    operation = vector.get("operation")

    if operation == "xor_byte":
        offset = _require_uint("offset", vector.get("offset"), _U32_MAX)
        xor_value = _require_uint("xor", vector.get("xor"), 0xFF)

        if offset >= len(mutated):
            raise CanonicalRecordError("xor_byte offset is outside base vector")

        mutated[offset] ^= xor_value
        return bytes(mutated)

    if operation == "set_byte":
        offset = _require_uint("offset", vector.get("offset"), _U32_MAX)
        value = _require_uint("value", vector.get("value"), 0xFF)

        if offset >= len(mutated):
            raise CanonicalRecordError("set_byte offset is outside base vector")

        mutated[offset] = value
        return bytes(mutated)

    if operation == "truncate":
        count = _require_uint("count", vector.get("count"), _U32_MAX)

        if count == 0 or count > len(mutated):
            raise CanonicalRecordError("truncate count must remove existing bytes")

        return bytes(mutated[:-count])

    if operation == "append_hex":
        suffix_hex = vector.get("hex")

        if not isinstance(suffix_hex, str):
            raise CanonicalRecordError("append_hex requires string field hex")

        try:
            suffix = bytes.fromhex(suffix_hex)
        except ValueError as exc:
            raise CanonicalRecordError("append_hex contains invalid hex") from exc

        if not suffix:
            raise CanonicalRecordError("append_hex must append at least one byte")

        return bytes(mutated) + suffix

    raise CanonicalRecordError(f"unsupported negative operation: {operation!r}")


def _negative_vector_rejects(
    vector: dict[str, Any],
    positive_by_id: dict[str, bytes],
) -> bool:
    operation = vector.get("operation")

    try:
        if operation == "encode_payload_repeat":
            byte_value = _decode_single_byte_hex("byte_hex", vector.get("byte_hex"))
            count = _require_uint("count", vector.get("count"), _U32_MAX)

            previous_seal_hex = vector.get("previous_seal_hex")

            if not isinstance(previous_seal_hex, str):
                raise CanonicalRecordError(
                    "previous_seal_hex must be a string"
                )

            encode_record(
                epoch=_require_uint("epoch", vector.get("epoch"), _U64_MAX),
                sequence=_require_uint(
                    "sequence",
                    vector.get("sequence"),
                    _U64_MAX,
                ),
                payload=bytes([byte_value]) * count,
                previous_seal=bytes.fromhex(previous_seal_hex),
            )
        else:
            mutated = _mutate_from_negative_vector(vector, positive_by_id)
            decode_record(mutated)

    except (CanonicalRecordError, ValueError):
        return True

    return False


def verify_vector_document(document: dict[str, Any]) -> list[str]:
    """
    Verify positive and negative fixtures from a loaded vector document.

    Returns a list of human-readable errors. An empty list means every
    positive fixture reproduced exactly and every negative fixture rejected.
    """

    errors: list[str] = []

    vectors = document.get("positive_vectors")

    if not isinstance(vectors, list):
        return ["positive_vectors must be a list"]

    positive_by_id: dict[str, bytes] = {}
    fingerprints_by_id: dict[str, str] = {}
    relation_checks: list[tuple[str, dict[str, Any]]] = []

    for vector in vectors:
        if not isinstance(vector, dict):
            errors.append("positive vector must be an object")
            continue

        vector_id = str(vector.get("id", "<unnamed>"))

        if vector_id in positive_by_id:
            errors.append(f"{vector_id}: duplicate vector id")
            continue

        try:
            encoded = _encode_positive_vector(vector)

            expected_hex = vector.get("canonical_hex")

            if expected_hex is not None:
                if not isinstance(expected_hex, str):
                    raise CanonicalRecordError("canonical_hex must be a string")

                if encoded.hex() != expected_hex.lower():
                    errors.append(f"{vector_id}: canonical_hex mismatch")

            expected_length = _require_uint(
                "canonical_length",
                vector.get("canonical_length"),
                _U32_MAX,
            )

            if len(encoded) != expected_length:
                errors.append(
                    f"{vector_id}: canonical_length mismatch "
                    f"(expected {expected_length}, got {len(encoded)})"
                )

            expected_fingerprint = vector.get("sha256_fixture_fingerprint")

            if not isinstance(expected_fingerprint, str):
                raise CanonicalRecordError(
                    "sha256_fixture_fingerprint must be a string"
                )

            actual_fingerprint = fixture_fingerprint(encoded)

            if actual_fingerprint != expected_fingerprint.lower():
                errors.append(f"{vector_id}: fixture fingerprint mismatch")

            decoded = decode_record(encoded)

            if decoded.encode() != encoded:
                errors.append(f"{vector_id}: decode/encode round trip mismatch")

            positive_by_id[vector_id] = encoded
            fingerprints_by_id[vector_id] = actual_fingerprint

            relation = vector.get("relation")

            if relation is not None:
                if not isinstance(relation, dict):
                    raise CanonicalRecordError("relation must be an object")
                relation_checks.append((vector_id, relation))

        except (KeyError, TypeError, ValueError, CanonicalRecordError) as exc:
            errors.append(f"{vector_id}: {exc}")

    for vector_id, relation in relation_checks:
        base_id = relation.get("base")

        if not isinstance(base_id, str) or base_id not in positive_by_id:
            errors.append(f"{vector_id}: relation references unknown base")
            continue

        if positive_by_id[vector_id] == positive_by_id[base_id]:
            errors.append(f"{vector_id}: mutation did not alter canonical bytes")

        if fingerprints_by_id[vector_id] == fingerprints_by_id[base_id]:
            errors.append(
                f"{vector_id}: mutation did not alter fixture fingerprint"
            )

    negative_vectors = document.get("negative_vectors")

    if not isinstance(negative_vectors, list):
        errors.append("negative_vectors must be a list")
        return errors

    for vector in negative_vectors:
        if not isinstance(vector, dict):
            errors.append("negative vector must be an object")
            continue

        vector_id = str(vector.get("id", "<unnamed-negative>"))

        if vector.get("expected") != "REJECT":
            errors.append(f"{vector_id}: expected must be REJECT")
            continue

        if vector.get("consumes_committed_sequence") is not False:
            errors.append(
                f"{vector_id}: rejected input must not consume committed sequence"
            )
            continue

        try:
            if not _negative_vector_rejects(vector, positive_by_id):
                errors.append(f"{vector_id}: negative vector was accepted")
        except (KeyError, TypeError, ValueError, CanonicalRecordError) as exc:
            errors.append(f"{vector_id}: malformed vector definition: {exc}")

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

    positive_count = len(document.get("positive_vectors", []))
    negative_count = len(document.get("negative_vectors", []))

    print(
        "PASS: "
        f"{positive_count} positive + {negative_count} negative "
        "canonical V1 vectors verified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
