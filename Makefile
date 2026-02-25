SHELL := /bin/bash

ifeq ($(OS),Windows_NT)
PYTHON ?= python
VENV_PY := .venv/Scripts/python
else
PYTHON ?= python3
VENV_PY := .venv/bin/python
endif

.PHONY: install test lint build-win build-mac

install:
	@if [ ! -d .venv ]; then $(PYTHON) -m venv .venv; fi
	@$(VENV_PY) -m pip install --upgrade pip
	@$(VENV_PY) -m pip install -r requirements.txt

test:
	@$(VENV_PY) -m pytest -q

lint:
	@$(VENV_PY) -m compileall -q main.py utils web excel tests

build-win:
ifeq ($(OS),Windows_NT)
	@cmd.exe /c build\\windows\\build_windows.bat
else
	@echo "build-win solo disponible en Windows"
endif

build-mac:
	@chmod +x build/mac/build_mac.sh
	@./build/mac/build_mac.sh
