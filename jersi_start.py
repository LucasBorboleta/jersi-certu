#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""jersi_start.py installs and starts a GUI for the JERSI boardgame."""


_COPYRIGHT_AND_LICENSE = """
JERSI-CERTU implements a GUI and a rule engine for the JERSI boardgame.

Copyright (C) 2019 Lucas Borboleta (lucas.borboleta@free.fr).

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses>.
"""


import glob
import os
import subprocess
import sys


_product_home = os.path.abspath(os.path.dirname(__file__))
os.chdir(_product_home)

_jersi_gui_executable = os.path.join(_product_home, "jersi_certu", "jersi_gui.py")
_venv_home = os.path.join(_product_home, ".env")


print()
print("Checking virtual environment ...")
if not os.path.isdir(_venv_home):
    print()
    print("Creating virtual environment ...")
    subprocess.run(args=[sys.executable, "-m", "venv", ".env"], shell=False, check=True)
    print("Creating virtual environment done")
    install_dependencies = True
    
else:
    install_dependencies = False
print("Checking virtual environment done")
    

if os.name == 'nt':
    _python_executable = os.path.join(_venv_home, "Scripts", "python.exe")

elif os.name == 'posix':
    _python_executable = os.path.join(_venv_home, "bin", "python")
    
else:
    _python_executable = glob.glob(os.path.join(_venv_home, "*/python*"))[0]
    

if install_dependencies:
    print()
    print("Installing dependencies ...")
    subprocess.run(args=[_python_executable, "-m", "pip", "install", "-r", "requirements.txt"], shell=False, check=True)
    print("Installing dependencies done")


print()
print("jersi_gui ...")
subprocess.run(args=[_python_executable, _jersi_gui_executable], shell=False, check=True)
print()
print("jersi_gui done")



