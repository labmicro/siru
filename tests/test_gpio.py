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
from siru.remote import Preat, Result
from siru.remote.gpio import Output

OUTPUT_SET_ONE = b"\x07\x01\x01\x10\x01\xb5\xa3"
OUTPUT_CLEAR_TWO = b"\x07\x01\x11\x10\x02\xd3\x15"

ACK_NO_ERROR = b"\x05\x00\x00\xa1\xb5"


@pytest.fixture(autouse=True)
def mock_serial_port_init(mocker):
    mocker.init = mocker.patch.object(Serial, "__init__", return_value=None)
    mocker.write = mocker.patch.object(Serial, "write", return_value=None)
    mocker.read = mocker.patch.object(Serial, "read")


def test_output_set_one(mocker: MockerFixture):
    mocker.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:]]

    preat = Preat(port="/dev/tty.USB")
    output = Output(preat, 0x01)
    result = output.set()

    mocker.write.assert_called_once_with(OUTPUT_SET_ONE)
    assert result == Result.NO_ERROR


def test_output_clear_two(mocker: MockerFixture):
    mocker.read.side_effect = [ACK_NO_ERROR[:1], ACK_NO_ERROR[1:]]

    preat = Preat(port="/dev/tty.USB")
    output = Output(preat, 0x02)
    result = output.clear()

    mocker.write.assert_called_once_with(OUTPUT_CLEAR_TWO)
    assert result == Result.NO_ERROR
