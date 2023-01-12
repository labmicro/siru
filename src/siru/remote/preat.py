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

from enum import Enum
from crc import Calculator, Configuration
from struct import pack
from serial import Serial


class Result(Enum):
    NO_ERROR = 0x00
    CRC_ERROR = 0x01
    METHOD_ERROR = 0x02
    PARAMETERS_ERROR = 0x03
    TOO_EARLY_ERROR = 0x04
    TIMEOUT_ERROR = 0x05
    UNDEFINED_ERROR = 0x06
    REDEFINED_ERROR = 0x07
    GENERIC_ERROR = 0xFF
    RESPONSE_TIMEOUT = 0x0100
    RESPONSE_CRC_ERROR = 0x0101


class Parameter:
    class Type(Enum):
        UNDEFINED = 0x00
        UINT8 = 0x01
        UINT16 = 0x02
        UINT32 = 0x03
        BLOB = 0x07
        BINARY = 0x80

    def __init__(self, type: Type, value: any) -> None:
        self._type = type
        self._value = value

    @property
    def type(self) -> Type:
        return self._type

    @property
    def value(self) -> any:
        return self._value

    def encode(self) -> bytes:
        frame = b""
        if self.type == self.Type.UINT8:
            frame = pack(">BB", 16 * self.type.value, self.value)
        elif self.type == self.Type.UINT16:
            frame = pack(">BH", 16 * self.type.value, self.value)
        elif self.type == self.Type.UINT32:
            frame = pack(">BI", 16 * self.type.value, self.value)
        return frame

    def merge(self, frame: bytes) -> bytes:
        new = self.encode()
        header = pack(">B", frame[0] + (new[0] >> 4))
        return header + frame[1:] + new[1:]


class Preat:
    def __init__(self, port: str) -> None:
        self.crc = Calculator(
            Configuration(
                width=16,
                polynomial=0xD175,
                init_value=0x0000,
                final_xor_value=0x0000,
                reverse_input=False,
                reverse_output=False,
            ),
            optimized=True,
        )
        self.port = Serial(
            port=port,
            baudrate=115200,
            timeout=1,
        )

    def encode(self, function, parameters):
        frame = pack(">H", 16 * function + len(parameters))

        for index in range(0, len(parameters), 2):
            if index + 1 < len(parameters):
                block = parameters[index].encode()
                frame = frame + parameters[index + 1].merge(block)
            else:
                frame = frame + parameters[index].encode()

        frame = pack(">B", len(frame) + 3) + frame
        frame = frame + pack(">H", self.crc.checksum(frame))
        return frame

    def excecute(self, function, parameters) -> Result:
        frame = self.encode(function, parameters)
        print(f"M->S: {frame.hex(' ')}")
        self.port.write(frame)
        response = self.port.read(1)

        if response:
            response = response + self.port.read(response[0])
            if self.crc.verify(response, 0x0000):
                error = Result.NO_ERROR if response[2] == 0x00 else Result(response[4])
            else:
                error = Result.RESPONSE_CRC_ERROR
            print(f"S->M: {response.hex(' ')} (Status: {Result(error).name})")
        else:
            error = Result.RESPONSE_TIMEOUT
            print(f"S->M: (No response)")

        return error
