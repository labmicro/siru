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


import pytest, yaml, os
from pathlib import Path
from siru.tasks import Tasks, Project, Job
from unittest.mock import MagicMock

CONFIG_FILE_CONTENT = """
---
tasks:
    project:
        name: demo-project
        path: /home/test/project
        binary: ./build/bin/project.elf

    environ:
        MUJU: ${job.environ["HOME"]}/muju
        TASK_TEST: Updated Value

    builder:
        command: /usr/bin/make
        template: ${job.command} ${job.action} MUJU=${job.environ["MUJU"]}

    monitor:
        command: /usr/bin/openocd
        config: ${job.abspath("openocd/config.file")}
        port: 8888
        template: ${job.command} -c "gdb_port ${job.port}" -f ${job.config}

    debugger:
        command: arm-none-eabi-gdb
        execute: target extended-remote localhost:${job.monitor.port}
        template: ${job.command} ${job.abspath(job.project.binary)} --ex "${job.execute}"


    flasher:
        command: make
        config: ${project_path}/openocd/config.file
        template: ${flasher.command} extended-remote localhost:${monitor.port}

...
"""


@pytest.fixture()
def config_file(tmp_path_factory):
    config_file = tmp_path_factory.mktemp("ate") / "ate-test.yaml"
    with open(config_file, "w") as file:
        file.write(CONFIG_FILE_CONTENT)
    return config_file


@pytest.fixture()
def mock_print(mocker):
    mocker.print = mocker.patch("builtins.print")
    return mocker


@pytest.fixture()
def mock_open(mocker):
    mocker.open = mocker.patch("siru.tasks.subprocess.Popen")
    return mocker


def local_path(path) -> str:
    return str(Path(path).resolve())


def test_assert_job_abspath():
    job = Job(project=Project(path="/home/test"), environ={})
    assert job.abspath("../file.txt") == local_path("/home/file.txt")


def test_assert_job_relpath():
    job = Job(project=Project(path="/home/test"), environ={})
    assert job.relpath("/home/test/folder/file.txt") == "folder/file.txt"


def test_assert_job_render():
    job = Job(
        project=Project(path="/home/test"),
        environ={"BIN": "/usr/bin/"},
        command='${job.environ["BIN"]}make',
        template="${job.command}",
    )
    assert job.render() == local_path("/usr/bin/make")


def test_assert_job_logger(mock_print):
    job = Job(project=Project(), environ={}, verbose=True)
    job.log_start_process("start text")
    assert mock_print.print.called_once()
    assert "start text" in mock_print.print.call_args.args[0]

    mock_print.print.reset_mock()
    job.log_end_process(("output text", "error text"))
    assert mock_print.print.call_count == 2
    assert "output text" in mock_print.print.call_args_list[0].args[0]
    assert "error text" in mock_print.print.call_args_list[1].args[0]


def test_init_default_values():
    os.environ["TASK_TEST"] = "Original Value"

    tasks = Tasks()
    assert tasks.project.name == ""
    assert tasks.project.path == "."
    assert tasks.project.binary == "project.elf"

    assert tasks.environ.get("TASK_TEST") == "Original Value"

    assert tasks.builder.command == "make"
    assert tasks.builder.clean == "clean"
    assert tasks.builder.build == "all"
    assert tasks.builder.template == "${job.command} ${job.action}"

    assert tasks.monitor.command == "openocd"
    assert tasks.monitor.config == ""
    assert tasks.monitor.port == 3333
    assert (
        tasks.monitor.template
        == '${job.command} -f ${job.config} -c "gdb_port ${job.port}"'
    )

    assert tasks.debugger.command == "gdb"
    assert tasks.debugger.execute == ""
    assert (
        tasks.debugger.template
        == '${job.command} -f ${job.binary} -ex "${job.execute}"'
    )

    assert tasks.flasher.command == "openocd"
    assert tasks.flasher.config == ""
    assert tasks.flasher.template == "${job.command} -f ${job.config}"


def test_init_from_file(config_file):
    os.environ["TASK_TEST"] = "Original Value"
    os.environ["HOME"] = "/home/test"

    with open(config_file) as file:
        config = yaml.load(file, Loader=yaml.SafeLoader)

    tasks = Tasks(**config["tasks"])
    assert tasks.project.name == "demo-project"
    assert tasks.project.path == "/home/test/project"
    assert tasks.project.binary == "./build/bin/project.elf"

    assert tasks.environ.get("MUJU") == '${job.environ["HOME"]}/muju'
    assert tasks.environ.get("TASK_TEST") == "Updated Value"

    assert (
        tasks.builder.template
        == '${job.command} ${job.action} MUJU=${job.environ["MUJU"]}'
    )
    assert tasks.builder.render() == "/usr/bin/make  MUJU=/home/test/muju"

    assert (
        tasks.monitor.render()
        == '/usr/bin/openocd -c "gdb_port 8888" -f '
        + local_path("/home/test/project/openocd/config.file")
    )

    assert (
        tasks.debugger.render()
        == "arm-none-eabi-gdb "
        + local_path("/home/test/project/build/bin/project.elf")
        + ' --ex "target extended-remote localhost:8888"'
    )

    assert (
        tasks.flasher.template
        == "${flasher.command} extended-remote localhost:${monitor.port}"
    )


def test_task_set_verbose():
    tasks = Tasks(verbose=True)
    assert tasks.verbose == True
    assert tasks.builder.verbose == True
    assert tasks.monitor.verbose == True
    assert tasks.debugger.verbose == True
    assert tasks.flasher.verbose == True


def test_tasks__builder_prebuild_called(mock_open):
    tasks = Tasks(project={"path": "/home/test"})
    callback_mock = MagicMock()
    tasks.builder.on_execute = callback_mock
    tasks.build()
    assert callback_mock.called
    assert callback_mock.call_args.args[0] == tasks.builder


def test_tasks_builder_build(mock_open):
    tasks = Tasks(project={"path": "/home/test"})
    tasks.build()
    call = mock_open.open.call_args
    assert call.args[0] == "make all"
    assert str(call.kwargs["cwd"]) == local_path("/home/test")


def test_tasks_builder_clean(mock_open):
    tasks = Tasks(project={"path": "/home/test"})
    tasks.clean()
    call = mock_open.open.call_args
    assert call.args[0] == "make clean"
    assert str(call.kwargs["cwd"]) == local_path("/home/test")


def test_tasks_builder_debugger_write(mock_open):
    tasks = Tasks(
        project={"path": "/home/test"},
        monitor={"config": "config.cfg"},
        debugger={"execute": "target remote"},
    )
    tasks.write()
    assert mock_open.open.call_count == 2

    call = mock_open.open.call_args_list[0]
    assert call.args[0] == 'openocd -f config.cfg -c "gdb_port 3333"'
    assert str(call.kwargs["cwd"]) == local_path("/home/test")

    call = mock_open.open.call_args_list[1]
    assert call.args[0] == 'gdb -f project.elf -ex "target remote"'
    assert str(call.kwargs["cwd"]) == local_path("/home/test")


def test_tasks_flasher(mock_open):
    tasks = Tasks(
        project={"path": "/home/test"},
        flasher={"config": "config.cfg"},
    )
    tasks.flash()
    call = mock_open.open.call_args
    assert call.args[0] == "openocd -f config.cfg"
    assert str(call.kwargs["cwd"]) == local_path("/home/test")
