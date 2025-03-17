param (
    [string]$folderPath
)

# Navigate to the provided folder path
Set-Location -Path $folderPath

# Install the required packages
pip install -r requirements.txt --platform manylinux2014_x86_64 --only-binary=:all: --target dist

# Copy main.py to the 'dist' folder
Copy-Item -Path "main.py" -Destination "dist"

# Change directory to 'dist'
Set-Location -Path "dist"

# Remove the existing package.zip if it exists
if (Test-Path -Path "package.zip") {
    Remove-Item -Path "package.zip" -Force
}

# Create a zip package of the contents, excluding package.zip
7z a -tzip package.zip *

# Extract the folder name from the provided path
$folderName = Split-Path -Leaf $folderPath

# Upload the zip package to the specified S3 bucket
aws s3 cp package.zip "s3://970279879940-fhir-pipeline-source/projects/$folderName/"

# Navigate back to the root directory
Set-Location -Path "..\.."