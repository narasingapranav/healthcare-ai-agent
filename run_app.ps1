$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    Write-Error 'Virtual environment not found at .venv. Create it first with: D:/Python/python.exe -m venv .venv'
}

& $venvPython -m streamlit run app.py
