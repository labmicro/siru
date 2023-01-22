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
from siru.ate import ATE
from typing import Callable

CONFIG_FILE_CONTENT = """
---
name: ate-edu-ciaa-nxp
board: edu-ciaa-nxp

server:
  url: /dev/tty.USB

digital_outputs:
  - name: led_rgb_r
    gpio_bit: HAL_GPIO5_0
  - name: led_rgb_g
    gpio_bit: HAL_GPIO5_1
  - name: led_rgb_b
    gpio_bit: HAL_GPIO5_2
  - name: led_1
    gpio_bit: HAL_GPIO0_14
  - name: led_2
    gpio_bit: HAL_GPIO1_11
  - name: led_3
    gpio_bit: HAL_GPIO1_12

digital_inputs:
  - name: tec_1
    gpio_bit: HAL_GPIO0_4
  - name: tec_2
    gpio_bit: HAL_GPIO0_8
  - name: tec_3
    gpio_bit: HAL_GPIO0_9
  - name: tec_4
    gpio_bit: HAL_GPIO1_9
...
"""

OUTPUT_INIT_CODE = """
        gpio_list[0] = HAL_GPIO5_0;
        gpio_list[1] = HAL_GPIO5_1;
        gpio_list[2] = HAL_GPIO5_2;
        gpio_list[3] = HAL_GPIO0_14;
        gpio_list[4] = HAL_GPIO1_11;
        gpio_list[5] = HAL_GPIO1_12;
"""

INPUT_INIT_CODE = """
        gpio_list[0] = HAL_GPIO0_4;
        gpio_list[1] = HAL_GPIO0_8;
        gpio_list[2] = HAL_GPIO0_9;
        gpio_list[3] = HAL_GPIO1_9;
"""

TEST_TEMPLATE_CONTENT = """
#define GPIO_INPUTS_COUNT  ${digital_inputs.count}

#define GPIO_OUTPUTS_COUNT ${digital_outputs.count}

bool GpioInputsListInit(hal_gpio_bit_t gpio_list[], uint8_t count) {
    bool result = (count == GPIO_INPUTS_COUNT);

    if (result) {
${digital_inputs.init_code}
    }
    return result;
}

bool GpioOutputsListInit(hal_gpio_bit_t gpio_list[], uint8_t count) {
    bool result = (count == GPIO_OUTPUTS_COUNT);

    if (result) {
${digital_outputs.init_code}
    }
    return result;
}
"""

TEMPLATE_EXPECTED_RESULT = """
#define GPIO_INPUTS_COUNT  4

#define GPIO_OUTPUTS_COUNT 6

bool GpioInputsListInit(hal_gpio_bit_t gpio_list[], uint8_t count) {
    bool result = (count == GPIO_INPUTS_COUNT);

    if (result) {
        gpio_list[0] = HAL_GPIO0_4;
        gpio_list[1] = HAL_GPIO0_8;
        gpio_list[2] = HAL_GPIO0_9;
        gpio_list[3] = HAL_GPIO1_9;
    }
    return result;
}

bool GpioOutputsListInit(hal_gpio_bit_t gpio_list[], uint8_t count) {
    bool result = (count == GPIO_OUTPUTS_COUNT);

    if (result) {
        gpio_list[0] = HAL_GPIO5_0;
        gpio_list[1] = HAL_GPIO5_1;
        gpio_list[2] = HAL_GPIO5_2;
        gpio_list[3] = HAL_GPIO0_14;
        gpio_list[4] = HAL_GPIO1_11;
        gpio_list[5] = HAL_GPIO1_12;
    }
    return result;
}
"""


@pytest.fixture(autouse=True)
def config_file(tmp_path_factory):
    config_file = tmp_path_factory.mktemp("ate") / "ate-test.yaml"
    with open(config_file, "w") as file:
        file.write(CONFIG_FILE_CONTENT)
    return config_file


def test_load_from_file(config_file):
    ate = ATE(config_file)
    assert ate.name == "ate-edu-ciaa-nxp"
    assert ate.board == "edu-ciaa-nxp"

    assert ate.digital_outputs.count == 6

    assert ate.digital_outputs.list[0].name == "led_rgb_r"
    assert ate.digital_outputs.list[1].index == 1
    assert ate.digital_outputs.list[2].gpio_bit == "HAL_GPIO5_2"

    assert ate.digital_outputs.init_code.strip() == OUTPUT_INIT_CODE.strip()

    assert ate.digital_inputs.count == 4
    assert ate.digital_inputs.list[1].name == "tec_2"
    assert ate.digital_inputs.list[2].index == 2
    assert ate.digital_inputs.list[3].gpio_bit == "HAL_GPIO1_9"

    assert ate.digital_inputs.init_code.strip() == INPUT_INIT_CODE.strip()

    assert ate.render(TEST_TEMPLATE_CONTENT) == TEMPLATE_EXPECTED_RESULT


def test_access_atributes_server(config_file):
    ate = ATE(config_file)
    assert isinstance(ate.wait, Callable)
    assert isinstance(ate.execute, Callable)


def test_access_atributes_digital_outputs(config_file):
    ate = ATE(config_file)
    assert ate.led_rgb_r.gpio_bit == "HAL_GPIO5_0"
    assert ate.led_2.gpio_bit == "HAL_GPIO1_11"


def test_access_atributes_digital_inputs(config_file):
    ate = ATE(config_file)
    assert ate.tec_2.gpio_bit == "HAL_GPIO0_8"
    assert ate.tec_4.gpio_bit == "HAL_GPIO1_9"
