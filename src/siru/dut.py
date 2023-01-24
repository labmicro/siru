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


import yaml
from yamlinclude import YamlIncludeConstructor
from pathlib import Path
from collections import namedtuple
from typing import Union

from siru import gpio, ate, tasks

Connection = namedtuple("Connection", ["name", "ate_pin"])


class DUT:
    def __init__(self, **kwargs) -> None:
        if "yaml" in kwargs:
            filename = kwargs.get("yaml")
            YamlIncludeConstructor.add_to_loader_class(
                loader_class=yaml.FullLoader, base_dir=Path(filename).parent
            )
            with open(filename) as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
        else:
            config = kwargs

        self.name = config.get("name", "")
        self._ate = ate.ATE(**config.get("ate"))

        self._digital_inputs = []
        for input in config.get("digital_inputs", []):
            self._digital_inputs.append(Connection(input["name"], input["ate_output"]))

        self._digital_outputs = []
        for input in config.get("digital_outputs", []):
            self._digital_outputs.append(Connection(input["name"], input["ate_input"]))

        self._tasks = tasks.Tasks(**config.get("tasks"))

    @property
    def ate(self) -> ate.ATE:
        return self._ate

    def __get_ate_output(self, name: str) -> Union[gpio.Output, None]:
        results = list(filter(lambda item: item.name == name, self._digital_inputs))
        return getattr(self._ate, results[0].ate_pin, None) if len(results) else None

    def __get_ate_input(self, name: str) -> Union[gpio.Input, None]:
        results = list(filter(lambda item: item.name == name, self._digital_outputs))
        return getattr(self._ate, results[0].ate_pin, None) if len(results) else None

    def __getattr__(self, name):
        result = getattr(self._tasks, name, None)
        if result == None:
            result = self.__get_ate_input(name)
        if result == None:
            result = self.__get_ate_output(name)
        if result == None:
            raise AttributeError(
                f"{self.__class__.__name__} object has no attribute {name}"
            )
        return result
