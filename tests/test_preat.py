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
from siru.remote import Preat, Parameter, Result

EXECUTE_SINGLE_PARAM = b"\x07\x01\x01\x10\x01\xb5\xa3"

ACK_NO_ERROR = b"\x05\x00\x00\xa1\xb5"
NACK_CRC_ERROR = b"\x07\x00\x11\x10\x01\xcc\x08"
NACK_METHOD_ERROR = b"\x07\x00\x11\x10\x02\x6e\xe2"
NACK_PARAMETERS_ERROR = b"\x07\x00\x11\x10\x03\xbf\x97"


@pytest.fixture(autouse=True)
def mock_serial_port_init(mocker):
    mocker.init = mocker.patch.object(Serial, "__init__", return_value=None)
    mocker.write = mocker.patch.object(Serial, "write", return_value=None)
    mocker.read = mocker.patch.object(Serial, "read")


def test_open_port(mocker: MockerFixture):
    preat = Preat(port="/dev/tty.USB")
    mocker.init.assert_called_once_with(port="/dev/tty.USB", baudrate=115200, timeout=1)


def test_execute_command(mocker: MockerFixture):
    mocker.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:]]

    preat = Preat(port="/dev/tty.USB")
    result = preat.excecute(0x010, [Parameter(Parameter.Type.UINT8, 0x01)])

    mocker.write.assert_called_once_with(EXECUTE_SINGLE_PARAM)
    assert result == Result.NO_ERROR


def test_crc_error_on_command(mocker: MockerFixture):
    mocker.read.side_effect = [NACK_CRC_ERROR[:1], NACK_CRC_ERROR[1:]]

    preat = Preat(port="/dev/tty.USB")
    result = preat.excecute(0x010, [Parameter(Parameter.Type.UINT8, 0x01)])

    assert result == Result.CRC_ERROR


def test_method_not_implemented(mocker: MockerFixture):
    mocker.read.side_effect = [NACK_METHOD_ERROR[:1], NACK_METHOD_ERROR[1:]]

    preat = Preat(port="/dev/tty.USB")
    result = preat.excecute(0x010, [Parameter(Parameter.Type.UINT8, 0x01)])

    assert result == Result.METHOD_ERROR


def test_error_in_parameters(mocker: MockerFixture):
    mocker.read.side_effect = [NACK_PARAMETERS_ERROR[:1], NACK_PARAMETERS_ERROR[1:]]

    preat = Preat(port="/dev/tty.USB")
    result = preat.excecute(0x010, [Parameter(Parameter.Type.UINT8, 0x01)])

    assert result == Result.PARAMETERS_ERROR


def test_crc_error_on_response(mocker: MockerFixture):
    mocker.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:3]]

    preat = Preat(port="/dev/tty.USB")
    result = preat.excecute(0x010, [Parameter(Parameter.Type.UINT8, 0x01)])

    assert result == Result.RESPONSE_CRC_ERROR


def test_timeout_on_response(mocker: MockerFixture):
    mocker.read.return_value = None

    preat = Preat(port="/dev/tty.USB")
    result = preat.excecute(0x010, [Parameter(Parameter.Type.UINT8, 0x01)])

    assert result == Result.RESPONSE_TIMEOUT
