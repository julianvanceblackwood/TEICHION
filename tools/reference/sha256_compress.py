#!/usr/bin/env python3
"""
Small software reference for the SHA-256 word operations used by TEICHION.

Python integers do not wrap at 32 bits, so the word width is kept explicit
throughout these helpers. This layer covers masking, rotates, logical shifts,
Choice, Majority, and the Sigma functions.

The message schedule and compression rounds are kept out of this layer for now.
"""

from __future__ import annotations


WORD_BITS = 32

# Python integers do not wrap at 32 bits. Keep each value within the SHA-256
# word width before it is used by the reference operations.
WORD_MASK = (1 << WORD_BITS) - 1


def u32(value: int) -> int:
    """Keep only the low 32 bits of value."""
    return value & WORD_MASK


def _require_shift_count(count: int) -> None:
    if isinstance(count, bool) or not isinstance(count, int):
        raise TypeError("shift count must be an integer")

    if not 0 <= count < WORD_BITS:
        raise ValueError("shift count must be in range 0..31")


def rotr32(value: int, count: int) -> int:
    """Rotate a 32-bit word right by count bits."""
    _require_shift_count(count)

    value = u32(value)

    if count == 0:
        return value

    return u32(
        (value >> count)
        | (value << (WORD_BITS - count))
    )


def shr32(value: int, count: int) -> int:
    """Shift a 32-bit word right and fill from the left with zeros."""
    _require_shift_count(count)

    return u32(value) >> count


def ch(x: int, y: int, z: int) -> int:
    """Apply the SHA-256 Choice function to three 32-bit words."""
    x = u32(x)
    y = u32(y)
    z = u32(z)

    return u32(
        (x & y)
        ^ ((~x) & z)
    )


def maj(x: int, y: int, z: int) -> int:
    """Apply the SHA-256 Majority function to three 32-bit words."""
    x = u32(x)
    y = u32(y)
    z = u32(z)

    return u32(
        (x & y)
        ^ (x & z)
        ^ (y & z)
    )


def big_sigma0(x: int) -> int:
    """Compute the SHA-256 uppercase Sigma-0 function."""
    return u32(
        rotr32(x, 2)
        ^ rotr32(x, 13)
        ^ rotr32(x, 22)
    )


def big_sigma1(x: int) -> int:
    """Compute the SHA-256 uppercase Sigma-1 function."""
    return u32(
        rotr32(x, 6)
        ^ rotr32(x, 11)
        ^ rotr32(x, 25)
    )


def small_sigma0(x: int) -> int:
    """Compute the lowercase sigma-0 function used by the message schedule."""
    return u32(
        rotr32(x, 7)
        ^ rotr32(x, 18)
        ^ shr32(x, 3)
    )


def small_sigma1(x: int) -> int:
    """Compute the lowercase sigma-1 function used by the message schedule."""
    return u32(
        rotr32(x, 17)
        ^ rotr32(x, 19)
        ^ shr32(x, 10)
    )
