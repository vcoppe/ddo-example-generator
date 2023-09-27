#!/bin/bash

latexmk --shell-escape -g -pdf -pvc $1 < /dev/null
