# Builds Windows exe.
pyinstaller --icon=icon.ico --onefile --add-data ".venv\Lib\site-packages\playwright\driver\package\.local-browsers;playwright\driver\package\.local-browsers" --splash splash.png --name Skraepper_0.9.0-beta.1.exe  main_gui.pyw