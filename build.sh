#!/bin/bash

rm -rf __pycache__ build dist

pyuic5 MainWindow.ui -o MainWindow.py
pyrcc5 res.qrc -o res_rc.py
pyinstaller monitorinfo.py -F
