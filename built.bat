@echo off
pyinstaller --onefile --windowed --name EmailTemplate --upx-dir=upx-3.96-win64 --add-data "templates.db;." main.py