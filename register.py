#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
import types
from typing import Callable
import inspect


class MultiMethod:
    def __init__(self, key: str):
        self.method_name: str = key
        self.methods: dict[str, Callable] = {}

    def __set_name__(self, owner, name):
        self.method_name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return types.MethodType(self, instance)

    def __call__(self, *args, **kwargs):
        parm_types = tuple(type(arg) for arg in args[1:])
        # method, _ = self.methods[parm_types]
        method = self.methods[parm_types]
        return method(*args, **kwargs)

    def register(self, value: Callable):
        sig = inspect.signature(value)
        parm_types = []
        parm_defaults = []
        for name, val in sig.parameters.items():
            if name == "self":
                continue
            if val.annotation is inspect._empty:
                raise TypeError(f"{name}: must be annotated")
            parm_types.append(val.annotation)
            parm_defaults.append(val.default)

        # self.methods[tuple(parm_types)] = (value, parm_defaults)
        self.methods[tuple(parm_types)] = value
        if len(parm_defaults):
            n = len(parm_defaults) - parm_defaults.count(inspect._empty)
            # self.methods[tuple(parm_types[:-n])] = (value, parm_defaults)
            self.methods[tuple(parm_types[:-n])] = value


class MultiDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if (key.startswith("__") and key.endswith("__")) or not callable(value):
            super().__setitem__(key, value)
            return
        if key not in self:
            super().__setitem__(key, value)
            return
        mm = self[key]
        if isinstance(mm, MultiMethod):
            mm.register(value)
            super().__setitem__(key, mm)
            return
        else:
            mm = MultiMethod(key)
            mm.register(self[key])
            mm.register(value)
            super().__setitem__(key, mm)
            return


class MultiMeta(type):
    def __prepare__(clsname, bases, **kwargs):
        return MultiDict()


class Math(metaclass=MultiMeta):
    def add(self, x: int, y: int):
        print("adding integers")
        return x + y

    def add(self, x: str, y: str):  # noqa: F811
        print("concatenating strings")
        return f"{x}_{y}"

    def factor(self, val: float, factor: float = 10.0):
        print(f"multiplying {val} by {factor}")
        return val * factor


if __name__ == "__main__":
    m = Math()
    m.add(10, 12)
    m.add("one", "two")
    m.factor(1.2, 10)
    m.factor(1.2)
