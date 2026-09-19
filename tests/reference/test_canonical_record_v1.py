from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.reference.canonical_record_v1 import (
    ALGORITHM_ID_HMAC_SHA256,
    CanonicalRecordError,
    FIXED_PREFIX_SIZE,
    FORMAT_VERSION,
    GEN1_MAX_PAYLOAD,
    RECEIPT_SIZE,
    RECORD_KIND_EVIDENCE,
    SEAL_DOMAIN,
    decode_record,
    encode_receipt,
    encode_record,
    fixture_fingerprint,
    verify_vector_document,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
VECTOR_PATH = REPO_ROOT / "test_vectors" / "canonical_seal_record_v1.json"


class CanonicalSealRecordV1Tests(unittest.TestCase):
    def test_machine_readable_vectors_reproduce_exactly(self) -> None:
        with VECTOR_PATH.open("r", encoding="utf-8") as handle:
            document = json.load(handle)

        errors = verify_vector_document(document)

        self.assertEqual(errors, [])

    def test_genesis_encoding_is_exactly_72_bytes(self) -> None:
        encoded = encode_record(
            epoch=0,
            sequence=0,
            payload=b"",
            previous_seal=bytes(32),
        )

        self.assertEqual(len(encoded), FIXED_PREFIX_SIZE)
        self.assertEqual(encoded[:16], SEAL_DOMAIN)
        self.assertEqual(encoded[16], FORMAT_VERSION)
        self.assertEqual(encoded[17], RECORD_KIND_EVIDENCE)
        self.assertEqual(encoded[18], ALGORITHM_ID_HMAC_SHA256)
        self.assertEqual(encoded[19], 0x00)

    def test_round_trip_preserves_exact_bytes(self) -> None:
        encoded = encode_record(
            epoch=7,
            sequence=42,
            payload=b"evidence-bytes",
            previous_seal=bytes.fromhex("ab" * 32),
        )

        decoded = decode_record(encoded)

        self.assertEqual(decoded.encode(), encoded)

    def test_payload_larger_than_profile_limit_is_rejected(self) -> None:
        with self.assertRaises(CanonicalRecordError):
            encode_record(
                epoch=0,
                sequence=0,
                payload=bytes(GEN1_MAX_PAYLOAD + 1),
                previous_seal=bytes(32),
            )

    def test_previous_seal_must_be_exactly_32_bytes(self) -> None:
        with self.assertRaises(CanonicalRecordError):
            encode_record(
                epoch=0,
                sequence=0,
                payload=b"",
                previous_seal=bytes(31),
            )

    def test_non_integer_epoch_is_rejected(self) -> None:
        with self.assertRaises(CanonicalRecordError):
            encode_record(
                epoch="0",  # type: ignore[arg-type]
                sequence=0,
                payload=b"",
                previous_seal=bytes(32),
            )

    def test_boolean_sequence_is_not_accepted_as_integer(self) -> None:
        with self.assertRaises(CanonicalRecordError):
            encode_record(
                epoch=0,
                sequence=True,
                payload=b"",
                previous_seal=bytes(32),
            )

    def test_unsupported_domain_is_rejected(self) -> None:
        encoded = bytearray(
            encode_record(
                epoch=0,
                sequence=0,
                payload=b"",
                previous_seal=bytes(32),
            )
        )
        encoded[0] ^= 0x01

        with self.assertRaises(CanonicalRecordError):
            decode_record(encoded)

    def test_unsupported_version_is_rejected(self) -> None:
        encoded = bytearray(
            encode_record(
                epoch=0,
                sequence=0,
                payload=b"",
                previous_seal=bytes(32),
            )
        )
        encoded[16] = 0x02

        with self.assertRaises(CanonicalRecordError):
            decode_record(encoded)

    def test_unsupported_record_kind_is_rejected(self) -> None:
        encoded = bytearray(
            encode_record(
                epoch=0,
                sequence=0,
                payload=b"",
                previous_seal=bytes(32),
            )
        )
        encoded[17] = 0xFF

        with self.assertRaises(CanonicalRecordError):
            decode_record(encoded)

    def test_unsupported_algorithm_is_rejected(self) -> None:
        encoded = bytearray(
            encode_record(
                epoch=0,
                sequence=0,
                payload=b"",
                previous_seal=bytes(32),
            )
        )
        encoded[18] = 0xFF

        with self.assertRaises(CanonicalRecordError):
            decode_record(encoded)

    def test_reserved_flags_are_rejected(self) -> None:
        encoded = bytearray(
            encode_record(
                epoch=0,
                sequence=0,
                payload=b"",
                previous_seal=bytes(32),
            )
        )
        encoded[19] = 0x01

        with self.assertRaises(CanonicalRecordError):
            decode_record(encoded)

    def test_truncated_payload_is_rejected(self) -> None:
        encoded = encode_record(
            epoch=0,
            sequence=0,
            payload=b"abc",
            previous_seal=bytes(32),
        )

        with self.assertRaises(CanonicalRecordError):
            decode_record(encoded[:-1])

    def test_trailing_bytes_are_rejected(self) -> None:
        encoded = encode_record(
            epoch=0,
            sequence=0,
            payload=b"abc",
            previous_seal=bytes(32),
        )

        with self.assertRaises(CanonicalRecordError):
            decode_record(encoded + b"\x00")

    def test_fixture_fingerprint_is_not_empty(self) -> None:
        encoded = encode_record(
            epoch=0,
            sequence=0,
            payload=b"",
            previous_seal=bytes(32),
        )

        fingerprint = fixture_fingerprint(encoded)

        self.assertEqual(len(fingerprint), 64)

    def test_receipt_encoding_is_exactly_104_bytes(self) -> None:
        receipt = encode_receipt(
            epoch=0,
            sequence=0,
            payload_length=0,
            previous_seal=bytes(32),
            seal=bytes.fromhex("22" * 32),
        )

        self.assertEqual(len(receipt), RECEIPT_SIZE)


if __name__ == "__main__":
    unittest.main()
