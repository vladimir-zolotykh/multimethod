#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
# test_multimethod_defaults.py

import pytest
from register import Math


# ------------------------------------------------------------
# basic overload tests
# ------------------------------------------------------------


def test_add_ints():
    m = Math()
    assert m.add(2, 3) == 5


def test_add_strings():
    m = Math()
    assert m.add("one", "two") == "one_two"


# ------------------------------------------------------------
# default parameter handling
# ------------------------------------------------------------


def test_factor_with_explicit_default_argument():
    """
    Existing implementation already supports this case because
    both arguments are present.
    """
    m = Math()

    assert m.factor(2.0, 10.0) == 20.0


def test_factor_with_implicit_default_argument():
    """
    This is the important test.

    Current implementation raises KeyError because overload
    lookup uses only runtime argument count/types.
    """
    m = Math()

    assert m.factor(2.0) == 20.0


# ------------------------------------------------------------
# additional overloads to stress default handling
# ------------------------------------------------------------


class ExtendedMath(Math):

    def power(self, x: int, exp: int = 2):
        return x**exp

    def power(self, x: str, exp: int = 2):  # noqa: F811
        return x * exp

    def repeat(self, text: str, n: int = 3, sep: str = ":"):
        return sep.join([text] * n)


# ------------------------------------------------------------
# tests for overloaded methods with defaults
# ------------------------------------------------------------


@pytest.mark.parametrize(
    "args, expected",
    [
        ((3,), 9),
        ((3, 3), 27),
    ],
)
def test_power_int_overload(args, expected):
    m = ExtendedMath()

    assert m.power(*args) == expected


@pytest.mark.parametrize(
    "args, expected",
    [
        (("a",), "aa"),
        (("a", 4), "aaaa"),
    ],
)
def test_power_str_overload(args, expected):
    m = ExtendedMath()

    assert m.power(*args) == expected


@pytest.mark.parametrize(
    "args, expected",
    [
        (("x",), "x:x:x"),
        (("x", 2), "x:x"),
        (("x", 2, "-"), "x-x"),
    ],
)
def test_repeat_defaults(args, expected):
    m = ExtendedMath()

    assert m.repeat(*args) == expected


# ------------------------------------------------------------
# failure cases
# ------------------------------------------------------------


def test_unknown_signature_raises():
    m = Math()

    with pytest.raises(KeyError):
        m.add(1.2, 2.4)


def test_wrong_argument_count_raises():
    m = ExtendedMath()

    with pytest.raises(KeyError):
        m.power()
