#!/bin/bash

source ./.env/bin/activate

pre-commit install

pre-commit run -a

pytest
