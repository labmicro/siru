#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##################################################################################################
# Copyright (c) 2022-2023, Laboratorio de Microprocesadores
# Facultad de Ciencias Exactas y Tecnología, Universidad Nacional de Tucumán
# https://www.microprocesadores.unt.edu.ar/
#
# Copyright (c) 2022-2023, Esteban Volentini <evolentini@herrera.unt.edu.ar>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
# OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023, Esteban Volentini <evolentini@herrera.unt.edu.ar>
##################################################################################################

from typing import Dict, List, Type
from .preat import Preat, Parameter, Result


class GPIO:
    def __init__(
        self, server: Preat, index: int, name: str = "", gpio_bit: str = ""
    ) -> None:
        self._server = server
        self._index = index
        self._name = name
        self._gpio_bit = gpio_bit

    @property
    def server(self) -> Preat:
        return self._server

    @property
    def name(self) -> str:
        return self._name

    @property
    def index(self) -> str:
        return self._index

    @property
    def gpio_bit(self) -> str:
        return self._gpio_bit

    @property
    def map(self) -> Dict:
        return {
            "name": self._name,
            "index": self._index,
            "gpio_bit": self._gpio_bit,
        }


class Output(GPIO):
    def set(self, *args, **kwargs) -> Result:
        return self.server.execute(
            0x010, [Parameter(Parameter.Type.UINT8, self.index)], *args, **kwargs
        )

    def clear(self, *args, **kwargs) -> Result:
        return self.server.execute(
            0x011, [Parameter(Parameter.Type.UINT8, self.index)], *args, **kwargs
        )

    def toogle(self, *args, **kwargs) -> Result:
        return self.server.execute(
            0x012, [Parameter(Parameter.Type.UINT8, self.index)], *args, **kwargs
        )


class Input(GPIO):
    def has_rising(self, *args, **kwargs) -> Result:
        return self.server.execute(
            0x013, [Parameter(Parameter.Type.UINT8, self.index)], *args, **kwargs
        )

    def has_falling(self, *args, **kwargs) -> Result:
        return self.server.execute(
            0x014, [Parameter(Parameter.Type.UINT8, self.index)], *args, **kwargs
        )

    def has_changed(self, *args, **kwargs) -> Result:
        return self.server.execute(
            0x015, [Parameter(Parameter.Type.UINT8, self.index)], *args, **kwargs
        )


class List:
    TEMPLATE_INIT_CODE = "        gpio_list[{index}] = {gpio_bit};"

    def __init__(self, server: Preat, type: Type[GPIO], config: List[dict]) -> None:
        index = 0
        self._list = []
        for entry in config:
            self._list.append(
                type(
                    server=server,
                    name=entry["name"],
                    index=int(entry.get("index", index)),
                    gpio_bit=entry.get("gpio_bit", ""),
                )
            )
            index = index + 1

    @property
    def list(self) -> List[GPIO]:
        return self._list

    @property
    def count(self) -> int:
        return len(self._list)

    @property
    def init_code(self) -> str:
        result = ""
        for item in self._list:
            result = result + "\n" if result else ""
            result = result + self.TEMPLATE_INIT_CODE.format(**item.map)
        return result

    def __getattr__(self, name):
        results = list(filter(lambda item: item.name == name, self._list))
        if len(results) != 1:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{name}'"
            )
        return results[0]
