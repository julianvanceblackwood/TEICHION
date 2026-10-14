#!/usr/bin/env python3
"""
Independent SHA-256 compression reference primitives for TEICHION.

This module begins with the 32-bit logical functions required by SHA-256.
It does not yet implement message scheduling, compression rounds, padding,
streaming, HMAC, or TEICHION record integration.
"""

from __future__ import annotations


WORD_BITS = 32
WORD_MASK = (1 << WORD_BITS) - 1


def u32(value: int) -> int:
    return value & WORD_MASK


def _require_shift_count(count: int) -> None:
    if isinstance(count, bool) or not isinstance(count, int):
        raise TypeError("shift count must be an integer")

    if not 0 <= count < WORD_BITS:
        raise ValueError("shift count must be in range 0..31")


def rotr32(value: int, count: int) -> int:
    _require_shift_count(count)

    value = u32(value)

    if count == 0:
        return value

    return u32(
        (value >> count)
        | (value << (WORD_BITS - count))
    )


def shr32(value: int, count: int) -> int:
    _require_shift_count(count)

    return u32(value) >> count


def ch(x: int, y: int, z: int) -> int:
    x = u32(x)
    y = u32(y)
    z = u32(z)

    return u32(
        (x & y)
        ^ ((~x) & z)
    )


def maj(x: int, y: int, z: int) -> int:
    x = u32(x)
    y = u32(y)
    z = u32(z)

    return u32(
        (x & y)
        ^ (x & z)
        ^ (y & z)
    )


def big_sigma0(x: int) -> int:
    return u32(
        rotr32(x, 2)
        ^ rotr32(x, 13)
        ^ rotr32(x, 22)
    )


def big_sigma1(x: int) -> int:
    return u32(
        rotr32(x, 6)
        ^ rotr32(x, 11)
        ^ rotr32(x, 25)
    )


def small_sigma0(x: int) -> int:
    return u32(
        rotr32(x, 7)
        ^ rotr32(x, 18)
        ^ shr32(x, 3)
    )


def small_sigma1(x: int) -> int:
    return u32(
        rotr32(x, 17)
        ^ rotr32(x, 19)
        ^ shr32(x, 10)
    )