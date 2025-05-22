#!/bin/bash

source ./.venv/bin/activate

pre-commit install

pre-commit run -a
