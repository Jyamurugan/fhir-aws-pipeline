param (
    [string]$folder
)

if (-not $folder) {
    Write-Host "Usage: .\script.ps1 <folder_name>"
    exit 1
}

if (-not (Test-Path -Path $folder -PathType Container)) {
    Write-Host "Folder not found: $folder"
    exit 1
}

Set-Location -Path $folder

uv export --frozen --no-dev --no-editable -o requirements.txt
uv pip install `
    --no-installer-metadata `
    --no-compile-bytecode `
    --python-platform x86_64-manylinux2014 `
    --python 3.12 `
    --target packages `
    -r requirements.txt

Set-Location -Path packages
Compress-Archive -Path * -DestinationPath ..\package.zip
Set-Location -Path ..

Compress-Archive -Path app -DestinationPath package.zip -Update

Set-Location -Path ..
