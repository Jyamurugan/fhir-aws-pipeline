# FHIR Bundle Processor

This project is designed to process FHIR bundles using AWS services.

## Setup Instructions

### 1. Create and Activate Virtual Environment

#### Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate
```
### 2. Package the Virtual Environment and Add main.py

To package the virtual environment's site-packages into a zip file and include `main.py` in the package, follow these steps:

```powershell
# Navigate to the directory containing the virtual environment
cd venv\Lib\site-packages

# Package the site-packages directory into a zip file
Compress-Archive -Path * -DestinationPath ..\..\..\packages\package.zip

# Move back to the project root directory
cd ..\..\..\

# Add main.py to the package
Compress-Archive -Path main.py -Update -DestinationPath packages\package.zip
```
