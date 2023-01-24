/************************************************************************************************
Copyright (c) 2022-2023, Laboratorio de Microprocesadores
Facultad de Ciencias Exactas y Tecnología, Universidad Nacional de Tucumán
https://www.microprocesadores.unt.edu.ar/

Copyright (c) 2022-2023, Esteban Volentini <evolentini@herrera.unt.edu.ar>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES
OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

SPDX-License-Identifier: MIT
*************************************************************************************************/

/** @file
 ** @brief Template for user settings implementation
 **
 ** @addtogroup ruwaq ruwaq
 ** @brief Firmware for Remote Board to Excecution of Automated Tests
 ** @{ */

/* === Headers files inclusions =============================================================== */

#include "config.h"

/* === Macros definitions ====================================================================== */

/* === Private data type declarations ========================================================== */

/* === Private variable declarations =========================================================== */

/* === Private function declarations =========================================================== */

/* === Public variable definitions ============================================================= */

/* === Private variable definitions ============================================================ */

/* === Private function implementation ========================================================= */

bool GpioInputsListInit(hal_gpio_bit_t gpio_list[], uint8_t count) {
    bool result = (count == GPIO_INPUTS_COUNT);

    if (result) {
        /* clang-format off */
        gpio_list[0] = HAL_GPIO_D4;
        gpio_list[1] = HAL_GPIO_D5;
        gpio_list[2] = HAL_GPIO_D6;
        gpio_list[3] = HAL_GPIO_D7;
        /* clang-format on */
    }
    return result;
}

bool GpioOutputsListInit(hal_gpio_bit_t gpio_list[], uint8_t count) {
    bool result = (count == GPIO_OUTPUTS_COUNT);

    if (result) {
        /* clang-format off */
        gpio_list[0] = HAL_GPIO_A1;
        gpio_list[1] = HAL_GPIO_A2;
        gpio_list[2] = HAL_GPIO_A3;
        gpio_list[3] = HAL_GPIO_B1;
        gpio_list[4] = HAL_GPIO_B2;
        gpio_list[5] = HAL_GPIO_B3;
        /* clang-format on */
    }
    return result;
}

/* === End of documentation ==================================================================== */

/** @} End of module definition for doxygen */
