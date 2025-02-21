# Builds Windows exe.
param (
    [Parameter(Mandatory=$true)]  # Makes the parameter mandatory
    [string]$exe_name
)
pyinstaller --icon=icon.ico --onefile --add-data ".venv\Lib\site-packages\playwright\driver\package\.local-browsers;playwright\driver\package\.local-browsers" --splash splash.png --name $exe_name main_gui.pyw