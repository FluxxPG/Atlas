$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$env:PYTHONPATH = "$root\apps\api"
python "$root\apps\api\run_server.py"
