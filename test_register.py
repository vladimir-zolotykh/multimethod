import types
import pytest
from register import MultiMethod, MultiDict, MultiMeta, Math


def test_multimethod_registers_functions():
    mm = MultiMethod("test")

    def func(self, x: int, y: int):
        return x + y

    mm.register(func)

    assert (int, int) in mm.methods
    assert mm.methods[(int, int)][0] is func


def test_multimethod_dispatches_by_argument_types():
    mm = MultiMethod("test")

    class Dummy:
        pass

    def int_func(self, x: int, y: int):
        return x + y

    def str_func(self, x: str, y: str):
        return f"{x}:{y}"

    mm.register(int_func)
    mm.register(str_func)

    obj = Dummy()

    assert mm(obj, 2, 3) == 5
    assert mm(obj, "a", "b") == "a:b"


def test_multimethod_raises_keyerror_for_unknown_signature():
    mm = MultiMethod("test")

    def func(self, x: int):
        return x

    mm.register(func)

    with pytest.raises(KeyError):
        mm(object(), "abc")


def test_multidict_stores_non_callable_values():
    md = MultiDict()

    md["x"] = 10

    assert md["x"] == 10


def test_multidict_stores_dunder_names_without_wrapping():
    md = MultiDict()

    value = lambda: None

    md["__init__"] = value

    assert md["__init__"] is value
    assert not isinstance(md["__init__"], MultiMethod)


def test_multidict_creates_multimethod_on_second_assignment():
    md = MultiDict()

    def func1(self, x: int):
        return x

    def func2(self, x: str):
        return x

    md["method"] = func1
    md["method"] = func2

    assert isinstance(md["method"], MultiMethod)

    mm = md["method"]

    assert (int,) in mm.methods
    assert (str,) in mm.methods


def test_multimeta_prepare_returns_multidict():
    namespace = MultiMeta.__prepare__("Test", ())

    assert isinstance(namespace, MultiDict)


def test_math_add_ints(capsys):
    m = Math()

    result = m.add(10, 12)

    captured = capsys.readouterr()

    assert result == 22
    assert "adding integers" in captured.out


def test_math_add_strings(capsys):
    m = Math()

    result = m.add("one", "two")

    captured = capsys.readouterr()

    assert result == "one_two"
    assert "concatenating strings" in captured.out


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        ((1, 2), 3),
        (("a", "b"), "a_b"),
    ],
)
def test_math_add_parametrized(args, expected):
    m = Math()

    assert m.add(*args) == expected


def test_math_add_invalid_signature():
    m = Math()

    with pytest.raises(KeyError):
        m.add(1.5, 2.5)


def test_descriptor_access_from_class_returns_multimethod():
    assert isinstance(Math.__dict__["add"], MultiMethod)


def test_descriptor_access_from_instance_returns_bound_method():
    m = Math()

    method = m.add

    assert isinstance(method, types.MethodType)
    assert method.__self__ is m
