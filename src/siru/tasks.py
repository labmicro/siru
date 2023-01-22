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

import os, subprocess
from typing import Dict, Tuple, List, Union
from mako.template import Template
from pathlib import Path


class Project:
    def __init__(self, **kwargs) -> None:
        self.name = kwargs.get("name", "")
        self.path = kwargs.get("path", ".")
        self.binary = kwargs.get("binary", "project.elf")


class Job:
    COMMAND = ""
    TEMPLATE = ""

    def __init__(self, project: Project, environ: Dict, **kwargs) -> None:
        self._project = project
        self._environ = environ
        self._on_execute = None
        self.command = kwargs.get("command", self.COMMAND)
        self.template = kwargs.get("template", self.TEMPLATE)
        self.verbose = kwargs.get("verbose", False)

    @property
    def project(self) -> Project:
        return self._project

    @property
    def environ(self) -> Dict:
        return self._environ

    @property
    def on_execute(self) -> Union[callable, None]:
        return self._on_execute

    @on_execute.setter
    def on_execute(self, calback: Union[callable, None]):
        if callable(calback):
            self._on_execute = calback
        else:
            self._on_execute = None

    def abspath(self, filename: str) -> str:
        path = Path(self.project.path, Template(filename).render(job=self))
        return str(path.resolve().absolute())

    def relpath(self, filename: str) -> str:
        path = Path(self.project.path, Template(filename).render(job=self))
        return str(path.relative_to(self.project.path))

    def render(self) -> str:
        first_pass = Template(self.template).render(job=self)
        return Template(first_pass).render(job=self)

    def log_start_process(self, command: str):
        if self.verbose:
            process = self.__class__.__name__
            header = f"=== Inicio del proceso {process} ---" + 60 * "-"
            print(f"{header:80}\n{command}")

    def log_end_process(self, result: Tuple):
        if self.verbose:
            process = self.__class__.__name__
            header = f"=== Salida del proceso {process} ---" + 60 * "-"
            print(f"{header:80}\n{result[0]}")
            header = f"=== Errores del proceso {process} --" + 60 * "-"
            print(f"{header:80}\n{result[1]}")

    def open_process(self):
        if self.on_execute:
            self.on_execute(self)
        command = self.render()
        self.log_start_process(command)
        return subprocess.Popen(
            command,
            cwd=self.abspath(self.project.path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            text=True,
            shell=True,
            env=self.environ,
        )


class Builder(Job):
    COMMAND = "make"
    TEMPLATE = "${job.command} ${job.action}"

    def __init__(self, project: Project, environ: Dict, **kwargs) -> None:
        super().__init__(project=project, environ=environ, **kwargs)
        self._action = ""
        self.clean = kwargs.get("clean", "clean")
        self.build = kwargs.get("build", "all")

    @property
    def action(self) -> str:
        return self._action


class Monitor(Job):
    COMMAND = "openocd"
    TEMPLATE = '${job.command} -f ${job.config} -c "gdb_port ${job.port}"'

    def __init__(self, project: Project, environ: Dict, **kwargs) -> None:
        super().__init__(project=project, environ=environ, **kwargs)
        self.config = kwargs.get("config", "")
        self.port = int(kwargs.get("port", "3333"))


class Debugger(Job):
    COMMAND = "gdb"
    TEMPLATE = '${job.command} -f ${job.binary} -ex "${job.execute}"'

    def __init__(self, project: Project, environ: Dict, **kwargs) -> None:
        super().__init__(project=project, environ=environ, **kwargs)
        self.binary = kwargs.get("binary", "${job.relpath(job.project.binary)}")
        self.execute = kwargs.get("execute", "")


class Flasher(Job):
    COMMAND = "openocd"
    TEMPLATE = "${job.command} -f ${job.config}"

    def __init__(self, project: Project, environ: Dict, **kwargs) -> None:
        super().__init__(project=project, environ=environ, **kwargs)
        self.config = kwargs.get("config", "")


class Tasks:
    def __init__(self, **kwargs) -> None:
        config = kwargs.get("project", {})
        self._project = Project(**config)

        self._environ = os.environ.copy()
        self._environ.update(kwargs.get("environ", {}))

        config = kwargs.get("builder", {})
        self._builder = Builder(self.project, self.environ, **config)

        config = kwargs.get("monitor", {})
        self._monitor = Monitor(self.project, self.environ, **config)

        config = kwargs.get("debugger", {})
        self._debugger = Debugger(self.project, self.environ, **config)
        self._debugger.monitor = self._monitor

        config = kwargs.get("flasher", {})
        self._flasher = Flasher(self.project, self.environ, **config)

        self.verbose = kwargs.get("verbose", False)

    @property
    def project(self) -> Project:
        return self._project

    @property
    def environ(self) -> Dict:
        return self._environ

    @property
    def builder(self) -> Builder:
        return self._builder

    @property
    def monitor(self) -> Monitor:
        return self._monitor

    @property
    def debugger(self) -> Debugger:
        return self._debugger

    @property
    def verbose(self) -> bool:
        return self._verbose

    @verbose.setter
    def verbose(self, value: bool):
        self._verbose = value
        self.builder.verbose = value
        self.monitor.verbose = value
        self.debugger.verbose = value
        self.flasher.verbose = value

    @property
    def flasher(self) -> Flasher:
        return self._flasher

    def clean(self) -> bool:
        self.builder._action = self.builder.clean

        builder = self.builder.open_process()
        result = builder.communicate()
        self.builder.log_end_process(result)

        return builder.returncode == 0

    def build(self) -> bool:
        self.builder._action = self.builder.build

        builder = self.builder.open_process()
        result = builder.communicate()
        self.builder.log_end_process(result)

        return builder.returncode == 0

    def debug(self, commands: List):
        monitor = self.monitor.open_process()

        debugger = self.debugger.open_process()
        result = debugger.communicate("\n".join(commands))
        self.debugger.log_end_process(result)

        result = monitor.communicate()
        self.monitor.log_end_process(result)
        monitor.kill()

        return debugger.returncode == 0

    def write(self):
        commands = [
            "load",
            "monitor reset run",
        ]
        return self.debug(commands)

    def restart(self):
        commands = [
            "monitor reset run",
        ]
        return self.debug(commands)

    def flash(self):
        flasher = self.flasher.open_process()
        result = flasher.communicate()
        self.flasher.log_end_process(result)

        return flasher.returncode == 0
