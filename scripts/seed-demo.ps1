$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$env:PYTHONPATH = "$root\apps\api"
python apps/api/scripts/seed_demo_data.py

