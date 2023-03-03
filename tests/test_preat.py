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
from pytest_mock import MockerFixture
from siru.preat import Preat, Parameter, Result

EXECUTE_OUTPUT_SINGLE_PARAM = b"\x07\x01\x01\x10\x01\xb5\xa3"
EXECUTE_ASSERT = b"\x11\x00\x54\x33\x00\x00\x00\x64\x00\x00\x13\x88\x11\x01\x00\xCD\x2C"
EXECUTE_INPUT_SINGLE_PARAM = b"\x07\x01\x51\x10\x03\xB1\xFA"

ACK_NO_ERROR = b"\x05\x00\x00\xa1\xb5"
NACK_CRC_ERROR = b"\x07\x00\x11\x10\x01\xcc\x08"
NACK_METHOD_ERROR = b"\x07\x00\x11\x10\x02\x6e\xe2"
NACK_PARAMETERS_ERROR = b"\x07\x00\x11\x10\x03\xbf\x97"
NACK_TIMEOUT_ERROR = b"\x07\x00\x11\x10\x05\x2b\x36"


class FakeInput:
    def __init__(self, preat: Preat, input: int) -> None:
        self.preat = preat
        self.input = input

    def is_set(self, *args, **kwargs) -> Result:
        return self.preat.execute(
            0x015, [Parameter(Parameter.Type.UINT8, self.input)], *args, **kwargs
        )


class FakeOutput:
    def __init__(self, preat: Preat, output: int) -> None:
        self.preat = preat
        self.output = output

    def set(self, *args, **kwargs) -> Result:
        return self.preat.execute(
            0x010, [Parameter(Parameter.Type.UINT8, self.output)], *args, **kwargs
        )


@pytest.fixture(autouse=True)
def mock_serial_port_init(mocker):
    mocker.init = mocker.patch.object(Serial, "__init__", return_value=None)
    mocker.write = mocker.patch.object(Serial, "write", return_value=None)
    mocker.read = mocker.patch.object(Serial, "read")
    mocker.timeout = mocker.patch.object(Serial, "timeout")


def test_execute_command(mocker: MockerFixture):
    mocker.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:]]

    preat = Preat("/dev/tty.USB")
    result = preat.execute(0x010, [Parameter(Parameter.Type.UINT8, 0x01)])

    mocker.init.assert_called_once_with(port="/dev/tty.USB", baudrate=115200)
    mocker.write.assert_called_once_with(EXECUTE_OUTPUT_SINGLE_PARAM)
    assert result == Result.NO_ERROR


def test_crc_error_on_command(mocker: MockerFixture):
    mocker.read.side_effect = [NACK_CRC_ERROR[:1], NACK_CRC_ERROR[1:]]

    preat = Preat("/dev/tty.USB")
    result = preat.execute(0x010, [Parameter(Parameter.Type.UINT8, 0x01)])

    assert result == Result.CRC_ERROR


def test_method_not_implemented(mocker: MockerFixture):
    mocker.read.side_effect = [NACK_METHOD_ERROR[:1], NACK_METHOD_ERROR[1:]]

    preat = Preat("/dev/tty.USB")
    result = preat.execute(0x010, [Parameter(Parameter.Type.UINT8, 0x01)])

    assert result == Result.METHOD_ERROR


def test_error_in_parameters(mocker: MockerFixture):
    mocker.read.side_effect = [NACK_PARAMETERS_ERROR[:1], NACK_PARAMETERS_ERROR[1:]]

    preat = Preat("/dev/tty.USB")
    result = preat.execute(0x010, [Parameter(Parameter.Type.UINT8, 0x01)])

    assert result == Result.PARAMETERS_ERROR


def test_crc_error_on_response(mocker: MockerFixture):
    mocker.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:3]]

    preat = Preat("/dev/tty.USB")
    result = preat.execute(0x010, [Parameter(Parameter.Type.UINT8, 0x01)])

    assert result == Result.RESPONSE_CRC_ERROR


def test_timeout_on_response(mocker: MockerFixture):
    mocker.read.return_value = None

    preat = Preat("/dev/tty.USB")
    result = preat.execute(0x010, [Parameter(Parameter.Type.UINT8, 0x01)])

    assert result == Result.RESPONSE_TIMEOUT


def test_execute_assert_single_condition(mocker: MockerFixture):
    mocker.read.side_effect = [
        ACK_NO_ERROR[:1],
        ACK_NO_ERROR[1:],
        ACK_NO_ERROR[:1],
        ACK_NO_ERROR[1:],
        ACK_NO_ERROR[:1],
        ACK_NO_ERROR[1:],
    ]

    preat = Preat("/dev/tty.USB")
    input = FakeInput(preat, 0x03)
    output = FakeOutput(preat, 0x01)
    result = preat.wait(100, 5000, [input.is_set], output.set)

    mocker.write.assert_any_call(EXECUTE_ASSERT)
    mocker.write.assert_any_call(EXECUTE_INPUT_SINGLE_PARAM)
    mocker.write.assert_any_call(EXECUTE_OUTPUT_SINGLE_PARAM)
    assert result == Result.NO_ERROR


def test_execute_assert_timeout(mocker: MockerFixture):
    mocker.read.side_effect = [
        ACK_NO_ERROR[:1],
        ACK_NO_ERROR[1:],
        ACK_NO_ERROR[:1],
        ACK_NO_ERROR[1:],
        NACK_TIMEOUT_ERROR[:1],
        NACK_TIMEOUT_ERROR[1:],
    ]

    preat = Preat("/dev/tty.USB")
    input = FakeInput(preat, 0x03)
    output = FakeOutput(preat, 0x01)
    result = preat.wait(100, 5000, [input.is_set], output.set)

    mocker.write.assert_any_call(EXECUTE_ASSERT)
    mocker.write.assert_any_call(EXECUTE_INPUT_SINGLE_PARAM)
    mocker.write.assert_any_call(EXECUTE_OUTPUT_SINGLE_PARAM)
    assert result == Result.TIMEOUT_ERROR


def test_execute_assert_error_input(mocker: MockerFixture):
    mocker.read.side_effect = [
        ACK_NO_ERROR[:1],
        ACK_NO_ERROR[1:],
        NACK_METHOD_ERROR[:1],
        NACK_METHOD_ERROR[1:],
    ]

    preat = Preat("/dev/tty.USB")
    input = FakeInput(preat, 0x03)
    output = FakeOutput(preat, 0x01)
    result = preat.wait(100, 5000, [input.is_set], output.set)

    mocker.write.assert_any_call(EXECUTE_ASSERT)
    mocker.write.assert_any_call(EXECUTE_INPUT_SINGLE_PARAM)
    assert result == Result.METHOD_ERROR


def test_execute_assert_error_definition(mocker: MockerFixture):
    mocker.read.side_effect = [
        NACK_PARAMETERS_ERROR[:1],
        NACK_PARAMETERS_ERROR[1:],
    ]

    preat = Preat("/dev/tty.USB")
    input = FakeInput(preat, 0x03)
    output = FakeOutput(preat, 0x01)
    result = preat.wait(100, 5000, [input.is_set], output.set)

    mocker.write.assert_any_call(EXECUTE_ASSERT)
    assert result == Result.PARAMETERS_ERROR


def test_change_port_before_open(mocker: MockerFixture):
    preat = Preat("/dev/tty.USB")
    assert preat.url == "/dev/tty.USB"
    preat.url = "/dev/tty.USB_DEVICE"
    assert preat.url == "/dev/tty.USB_DEVICE"

    mocker.read.return_value = None
    result = preat.execute(0x010, [Parameter(Parameter.Type.UINT8, 0x01)])
    mocker.init.assert_called_once_with(port="/dev/tty.USB_DEVICE", baudrate=115200)
    assert result == Result.RESPONSE_TIMEOUT


def test_change_port_after_open(mocker: MockerFixture):
    preat = Preat("/dev/tty.USB")
    assert preat.url == "/dev/tty.USB"

    mocker.read.return_value = None
    result = preat.execute(0x010, [Parameter(Parameter.Type.UINT8, 0x01)])
    mocker.init.assert_called_once_with(port="/dev/tty.USB", baudrate=115200)
    assert result == Result.RESPONSE_TIMEOUT

    preat.url = "/dev/tty.USB_DEVICE"
    assert preat.url == "/dev/tty.USB_DEVICE"

    mocker.init.reset_mock()
    mocker.read.return_value = None
    result = preat.execute(0x010, [Parameter(Parameter.Type.UINT8, 0x01)])
    mocker.init.assert_called_once_with(port="/dev/tty.USB_DEVICE", baudrate=115200)
    assert result == Result.RESPONSE_TIMEOUT
