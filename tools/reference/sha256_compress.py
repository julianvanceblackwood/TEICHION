#!/usr/bin/env python3
"""
Reference implementations of the SHA-256 word operations used by TEICHION.

The functions in this file keep Python arithmetic within SHA-256's 32-bit
word semantics. They cover masking, rotates, shifts, Choice, Majority, and
the Sigma functions used by the compression algorithm.

Message scheduling and compression rounds are intentionally not implemented
here yet.
"""

from __future__ import annotations


WORD_BITS = 32

# Python integers are unbounded, so the reference model masks values back to
# the 32-bit word width defined by SHA-256.
WORD_MASK = (1 << WORD_BITS) - 1


def u32(value: int) -> int:
    """Return the low 32 bits of value."""
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
    """Logically shift a 32-bit word right by count bits."""
    _require_shift_count(count)

    return u32(value) >> count


def ch(x: int, y: int, z: int) -> int:
    """Return the SHA-256 Choice function for three 32-bit words."""
    x = u32(x)
    y = u32(y)
    z = u32(z)

    return u32(
        (x & y)
        ^ ((~x) & z)
    )


def maj(x: int, y: int, z: int) -> int:
    """Return the SHA-256 Majority function for three 32-bit words."""
    x = u32(x)
    y = u32(y)
    z = u32(z)

    return u32(
        (x & y)
        ^ (x & z)
        ^ (y & z)
    )


def big_sigma0(x: int) -> int:
    """Return the SHA-256 uppercase Sigma-0 function."""
    return u32(
        rotr32(x, 2)
        ^ rotr32(x, 13)
        ^ rotr32(x, 22)
    )


def big_sigma1(x: int) -> int:
    """Return the SHA-256 uppercase Sigma-1 function."""
    return u32(
        rotr32(x, 6)
        ^ rotr32(x, 11)
        ^ rotr32(x, 25)
    )


def small_sigma0(x: int) -> int:
    """Return the SHA-256 lowercase sigma-0 schedule function."""
    return u32(
        rotr32(x, 7)
        ^ rotr32(x, 18)
        ^ shr32(x, 3)
    )


def small_sigma1(x: int) -> int:
    """Return the SHA-256 lowercase sigma-1 schedule function."""
    return u32(
        rotr32(x, 17)
        ^ rotr32(x, 19)
        ^ shr32(x, 10)
    )
