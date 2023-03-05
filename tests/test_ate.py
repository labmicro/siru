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

import pytest, shutil, filecmp
from siru.ate import ATE
from typing import Callable
from tests.utils import DATA_DIR, load_config
from pathlib import Path

CONFIG = load_config("ate_test.yaml")


@pytest.fixture()
def ruwaq_path(tmp_path_factory):
    ruwaq_path = tmp_path_factory.mktemp("ruwaq")
    return ruwaq_path


def test_init_from_arguments():
    ate = ATE(**CONFIG)

    assert ate.name == "ate-test"
    assert ate.board == "board-test"

    assert ate.digital_outputs.count == 6

    assert ate.digital_outputs.list[0].name == "output_red"
    assert ate.digital_outputs.list[1].index == 1
    assert ate.digital_outputs.list[2].gpio_bit == "HAL_GPIO_A3"

    assert ate.digital_inputs.count == 4
    assert ate.digital_inputs.list[1].name == "input_violet"
    assert ate.digital_inputs.list[2].index == 2
    assert ate.digital_inputs.list[3].gpio_bit == "HAL_GPIO_D7"


def test_access_atributes_server():
    ate = ATE(**CONFIG)
    assert isinstance(ate.wait, Callable)
    assert isinstance(ate.execute, Callable)


def test_access_atributes_digital_outputs():
    ate = ATE(**CONFIG)
    assert ate.output_gray.gpio_bit == "HAL_GPIO_B1"
    assert ate.output_yellow.gpio_bit == "HAL_GPIO_B3"


def test_access_atributes_digital_inputs():
    ate = ATE(**CONFIG)
    assert ate.input_violet.gpio_bit == "HAL_GPIO_D5"
    assert ate.input_brown.gpio_bit == "HAL_GPIO_D7"


def test_undefined_property_raise_exception():
    ate = ATE(**CONFIG)
    with pytest.raises(AttributeError) as exc_info:
        dummy = ate.input_none.name
    assert str(exc_info.value) == "ATE object has no attribute input_none"


def test_render_config_files(ruwaq_path):
    source = DATA_DIR.parent / "ruwaq" / "template"
    destination = ruwaq_path / "module" / "template"
    shutil.copytree(source, destination)

    ate = ATE(**CONFIG)
    ate.ruwaq = str(ruwaq_path)
    ate.generate_config()
    source = Path(ruwaq_path / "config" / ate.name)
    destination = Path(DATA_DIR.parent / "ruwaq" / "expected")

    assert filecmp.cmp(f"{source}/inc/config.h", f"{destination}/inc/config.h")
    assert filecmp.cmp(f"{source}/src/config.c", f"{destination}/src/config.c")


def test_access_atributes_url_preat_server():
    ate = ATE(**CONFIG)
    assert ate.server.url == "/dev/tty.USB"

    ate.server.url = "/dev/tty.USB_DEVICE"
    assert ate.server.url == "/dev/tty.USB_DEVICE"
