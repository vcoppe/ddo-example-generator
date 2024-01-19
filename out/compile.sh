#!/bin/bash

latexmk -pdfxelatex --shell-escape -g -pvc $1 < /dev/null
