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

import pytest
from siru.dut import DUT
from tests.utils import DATA_DIR, load_config
from typing import Callable

CONFIG_FILE = "dut_test.yaml"

CONFIG_DICT = load_config("dut_test.yaml")


def test_init_from_arguments():
    dut = DUT(**CONFIG_DICT)
    assert dut.name == "dut-test"
    assert dut.ate.name == "ate-test"


def test_init_from_config_file():
    config_file = DATA_DIR / CONFIG_FILE
    dut = DUT(yaml=config_file)
    assert dut.name == "dut-test"
    assert dut.ate.name == "ate-test"


def test_access_atributes_digital_inputs():
    config_file = DATA_DIR / CONFIG_FILE
    dut = DUT(yaml=config_file)
    assert isinstance(dut.key_left.set, Callable)
    assert isinstance(dut.key_up.clear, Callable)
    assert isinstance(dut.key_rigth.toogle, Callable)
    assert getattr(dut, "key_none", None) == None


def test_access_atributes_digital_outputs():
    dut = DUT(**CONFIG_DICT)
    assert isinstance(dut.led_rgb_red.has_rising, Callable)
    assert isinstance(dut.led_rgb_green.has_falling, Callable)
    assert isinstance(dut.led_rgb_blue.has_changed, Callable)
    assert getattr(dut, "led_none", None) == None


def test_access_tasks():
    dut = DUT(**CONFIG_DICT)
    assert isinstance(dut.build, Callable)
    assert isinstance(dut.clean, Callable)


def test_undefined_property_raise_exception():
    dut = DUT(**CONFIG_DICT)
    with pytest.raises(AttributeError) as exc_info:
        dummy = dut.led_none.name
    assert str(exc_info.value) == "DUT object has no attribute led_none"
