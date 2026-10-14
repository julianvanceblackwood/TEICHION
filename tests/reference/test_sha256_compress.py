import unittest

from tools.reference.sha256_compress import (
    big_sigma0,
    big_sigma1,
    ch,
    maj,
    rotr32,
    shr32,
    small_sigma0,
    small_sigma1,
    u32,
)


class Sha256PrimitiveTests(unittest.TestCase):
    def test_u32_keeps_only_low_32_bits(self) -> None:
        self.assertEqual(u32(0x1_0000_0000), 0x00000000)
        self.assertEqual(u32(-1), 0xFFFFFFFF)

    def test_rotate_right_preserves_wrapped_bit(self) -> None:
        self.assertEqual(
            rotr32(0x80000001, 1),
            0xC0000000,
        )

    def test_shift_right_discards_low_bit(self) -> None:
        self.assertEqual(
            shr32(0x80000001, 1),
            0x40000000,
        )

    def test_choice_selects_y_when_x_is_all_ones(self) -> None:
        self.assertEqual(
            ch(0xFFFFFFFF, 0x12345678, 0xA5A5A5A5),
            0x12345678,
        )

    def test_choice_selects_z_when_x_is_zero(self) -> None:
        self.assertEqual(
            ch(0x00000000, 0x12345678, 0xA5A5A5A5),
            0xA5A5A5A5,
        )

    def test_majority_returns_repeated_word(self) -> None:
        self.assertEqual(
            maj(0x89ABCDEF, 0x89ABCDEF, 0x12345678),
            0x89ABCDEF,
        )

    def test_sigma_functions_match_fixed_reference_values(self) -> None:
        value = 0x12345678

        self.assertEqual(big_sigma0(value), 0x66146474)
        self.assertEqual(big_sigma1(value), 0x3561ABDA)
        self.assertEqual(small_sigma0(value), 0xE7FCE6EE)
        self.assertEqual(small_sigma1(value), 0xA1F78649)

    def test_invalid_shift_counts_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            rotr32(0x12345678, 32)

        with self.assertRaises(ValueError):
            shr32(0x12345678, -1)


if __name__ == "__main__":
    unittest.main()
