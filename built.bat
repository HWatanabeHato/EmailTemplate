@echo off
pyinstaller --onefile --windowed --name EmailTemplate_V0.3.2 --upx-dir=upx-3.96-win64 --add-data "templates.db;." main.py