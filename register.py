#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
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
        return instance.__dict__[self.method_name]

    def __call__(self, *args, **kwargs):
        sig = inspect.signature()

    def register(self, value):
        parm_types = ()
        sig = inspect.signature(value)
        self.methods[parm_types] = value


class MultiDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if (key.startswith("__") and key.endswith("__")) or not callable(value):
            super().__setitem__(key, value)
            return
        if key not in self:
            mm = MultiMethod()
            super().__setitem__(key, mm)
            return
        mm = self[key]
        assert isinstance(mm, MultiMethod)
        mm.register(value)
        super().__setitem__(key, mm)


class MultiMeta(type):
    def __new__(mcls, clsname, bases, clsdict, **kwargs):
        pass

    def __prepare__(clsname, bases, **kwargs):
        return MultiDict()


class MultiBase(metaclass=MultiMeta):
    pass


class Math(metaclass=MultiBase):
    def add(self, x: int, y: int):
        print("adding integers")
        return x + y

    def add(self, x: str, y: str):
        print("concatenating strings")
        return f"{x}_{y}"


if __name__ == "__main__":
    m = Math()
    m.add(10, 12)
    m.add("one", "two")
