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
from serial import Serial
from siru.preat import Preat, Result
from siru.gpio import List, Output, Input


@pytest.fixture
def serial_port(mocker):
    serial_port.init = mocker.patch.object(Serial, "__init__", return_value=None)
    serial_port.write = mocker.patch.object(Serial, "write", return_value=None)
    serial_port.read = mocker.patch.object(Serial, "read")
    serial_port.timeout = mocker.patch.object(Serial, "timeout")
    return serial_port


OUTPUT_SET_ONE = b"\x07\x01\x01\x10\x01\xb5\xa3"
OUTPUT_CLEAR_TWO = b"\x07\x01\x11\x10\x02\xd3\x15"
OUTPUT_TOGGLE_ZERO = b"\x07\x01\x21\x10\x00\x3d\x1b"

INPUT_RISING_ZERO = b"\x07\x01\x31\x10\x00\xf9\x47"
INPUT_FALLING_UNO = b"\x07\x01\x41\x10\x01\x06\x39"
INPUT_CHANGED_TWO = b"\x07\x01\x51\x10\x02\x60\x8f"

ACK_NO_ERROR = b"\x05\x00\x00\xa1\xb5"


@pytest.fixture
def outputs_list():
    return List(
        Preat("/dev/tty.USB"),
        Output,
        [
            {"name": "led_red", "gpio_bit": "HAL_GPIO_1"},
            {"name": "led_green", "gpio_bit": "HAL_GPIO_2"},
            {"name": "led_blue", "gpio_bit": "HAL_GPIO_3"},
        ],
    )


OUTPUT_INIT_CODE = """
        gpio_list[0] = HAL_GPIO_1;
        gpio_list[1] = HAL_GPIO_2;
        gpio_list[2] = HAL_GPIO_3;
"""


def test_list_outputs_build(outputs_list):
    assert outputs_list.count == 3

    assert outputs_list.list[0].name == "led_red"
    assert outputs_list.list[0].index == 0
    assert outputs_list.list[0].gpio_bit == "HAL_GPIO_1"

    assert outputs_list.list[1].name == "led_green"
    assert outputs_list.list[1].index == 1
    assert outputs_list.list[1].gpio_bit == "HAL_GPIO_2"

    assert outputs_list.list[2].name == "led_blue"
    assert outputs_list.list[2].index == 2
    assert outputs_list.list[2].gpio_bit == "HAL_GPIO_3"


def test_list_outputs_init_code(outputs_list):
    assert outputs_list.init_code.strip() == OUTPUT_INIT_CODE.strip()


def test_list_outputs_names_as_atributes(outputs_list):
    assert outputs_list.led_red.index == 0
    assert outputs_list.led_red.gpio_bit == "HAL_GPIO_1"
    assert outputs_list.led_green.index == 1
    assert outputs_list.led_green.gpio_bit == "HAL_GPIO_2"
    assert outputs_list.led_blue.index == 2
    assert outputs_list.led_blue.gpio_bit == "HAL_GPIO_3"


def test_output_set_one(serial_port, outputs_list):
    serial_port.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:]]
    result = outputs_list.list[1].set()
    serial_port.write.assert_called_once_with(OUTPUT_SET_ONE)
    assert result == Result.NO_ERROR


def test_output_set_led_gree(serial_port, outputs_list):
    serial_port.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:]]
    result = outputs_list.led_green.set()
    serial_port.write.assert_called_once_with(OUTPUT_SET_ONE)
    assert result == Result.NO_ERROR


def test_output_clear_two(serial_port, outputs_list):
    serial_port.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:]]
    result = outputs_list.list[2].clear()
    serial_port.write.assert_called_once_with(OUTPUT_CLEAR_TWO)
    assert result == Result.NO_ERROR


def test_output_clear_led_blue(serial_port, outputs_list):
    serial_port.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:]]
    result = outputs_list.led_blue.clear()
    serial_port.write.assert_called_once_with(OUTPUT_CLEAR_TWO)
    assert result == Result.NO_ERROR


def test_output_toggle_zero(serial_port, outputs_list):
    serial_port.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:]]
    result = outputs_list.list[0].toogle()
    serial_port.write.assert_called_once_with(OUTPUT_TOGGLE_ZERO)
    assert result == Result.NO_ERROR


def test_output_toggle_led_red(serial_port, outputs_list):
    serial_port.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:]]
    result = outputs_list.led_red.toogle()
    serial_port.write.assert_called_once_with(OUTPUT_TOGGLE_ZERO)
    assert result == Result.NO_ERROR


@pytest.fixture
def inputs_list():
    return List(
        Preat("/dev/tty.USB"),
        Input,
        [
            {"name": "key_up", "gpio_bit": "HAL_GPIO_11"},
            {"name": "key_down", "gpio_bit": "HAL_GPIO_12"},
            {"name": "key_left", "gpio_bit": "HAL_GPIO_13"},
            {"name": "key_rigth", "gpio_bit": "HAL_GPIO_14"},
        ],
    )


INPUT_INIT_CODE = """
        gpio_list[0] = HAL_GPIO_11;
        gpio_list[1] = HAL_GPIO_12;
        gpio_list[2] = HAL_GPIO_13;
        gpio_list[3] = HAL_GPIO_14;
"""


def test_list_outputs_build(inputs_list):
    assert inputs_list.count == 4

    assert inputs_list.list[0].name == "key_up"
    assert inputs_list.list[0].index == 0
    assert inputs_list.list[0].gpio_bit == "HAL_GPIO_11"

    assert inputs_list.list[1].name == "key_down"
    assert inputs_list.list[1].index == 1
    assert inputs_list.list[1].gpio_bit == "HAL_GPIO_12"

    assert inputs_list.list[2].name == "key_left"
    assert inputs_list.list[2].index == 2
    assert inputs_list.list[2].gpio_bit == "HAL_GPIO_13"

    assert inputs_list.list[3].name == "key_rigth"
    assert inputs_list.list[3].index == 3
    assert inputs_list.list[3].gpio_bit == "HAL_GPIO_14"


def test_list_inputs_names_as_atributes(inputs_list):
    assert inputs_list.key_up.index == 0
    assert inputs_list.key_up.gpio_bit == "HAL_GPIO_11"
    assert inputs_list.key_down.index == 1
    assert inputs_list.key_down.gpio_bit == "HAL_GPIO_12"
    assert inputs_list.key_left.index == 2
    assert inputs_list.key_left.gpio_bit == "HAL_GPIO_13"
    assert inputs_list.key_rigth.index == 3
    assert inputs_list.key_rigth.gpio_bit == "HAL_GPIO_14"


def test_list_outputs_init_code(inputs_list):
    assert inputs_list.init_code.strip() == INPUT_INIT_CODE.strip()


def test_input_rissing_zero(serial_port, inputs_list):
    serial_port.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:]]
    result = inputs_list.list[0].has_rising()
    serial_port.write.assert_called_once_with(INPUT_RISING_ZERO)
    assert result == Result.NO_ERROR


def test_input_rissing_key_up(serial_port, inputs_list):
    serial_port.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:]]
    result = inputs_list.key_up.has_rising()
    serial_port.write.assert_called_once_with(INPUT_RISING_ZERO)
    assert result == Result.NO_ERROR


def test_input_falling_one(serial_port, inputs_list):
    serial_port.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:]]
    result = inputs_list.list[1].has_falling()
    serial_port.write.assert_called_once_with(INPUT_FALLING_UNO)
    assert result == Result.NO_ERROR


def test_input_rissing_key_down(serial_port, inputs_list):
    serial_port.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:]]
    result = inputs_list.key_down.has_falling()
    serial_port.write.assert_called_once_with(INPUT_FALLING_UNO)
    assert result == Result.NO_ERROR


def test_input_changed_two(serial_port, inputs_list):
    serial_port.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:]]
    result = inputs_list.list[2].has_changed()
    serial_port.write.assert_called_once_with(INPUT_CHANGED_TWO)
    assert result == Result.NO_ERROR


def test_input_rissing_key_left(serial_port, inputs_list):
    serial_port.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:]]
    result = inputs_list.key_left.has_changed()
    serial_port.write.assert_called_once_with(INPUT_CHANGED_TWO)
    assert result == Result.NO_ERROR
