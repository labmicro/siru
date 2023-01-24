#!/gpiousr/bin/env python3
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

import os, glob, subprocess, yaml
from asyncio.subprocess import PIPE
from mako.template import Template
from siru import gpio, preat


class ATE:
    def __init__(self, **kwargs) -> None:
        self.name = kwargs.get("name", "")
        self.board = kwargs.get("board", "")
        self._server = preat.Preat(**kwargs.get("server"))
        self.ruwaq = ""

        self._digital_outputs = gpio.List(
            self._server, gpio.Output, kwargs.get("digital_outputs", [])
        )
        self._digital_inputs = gpio.List(
            self._server, gpio.Input, kwargs.get("digital_inputs", [])
        )

    @property
    def digital_outputs(self) -> gpio.List:
        return self._digital_outputs

    @property
    def digital_inputs(self) -> gpio.List:
        return self._digital_inputs

    def __getattr__(self, name):
        result = getattr(self._server, name, None)
        if result == None:
            result = getattr(self._digital_inputs, name, None)
        if result == None:
            result = getattr(self._digital_outputs, name, None)
        if result == None:
            raise AttributeError(
                f"{self.__class__.__name__} object has no attribute {name}"
            )
        return result

    def render(self, template: str) -> str:
        return Template(template).render(
            digital_outputs=self.digital_outputs,
            digital_inputs=self.digital_inputs,
        )

    def generate_config(self, ruwaq: str = None):
        templates = f"{self.ruwaq}/module/template"
        destination = f"{self.ruwaq}/config/{self.name}"
        sources = glob.glob(templates + "/**/*.[c,h]", recursive=True)
        for source in sources:
            with open(source) as file:
                output = self.render(file.read())
            filename = source.replace(templates, destination)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as file:
                file.write(output)
        return destination
