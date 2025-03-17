param (
    [string]$ProjectName
)

function Package-Project {
    param (
        [string]$ProjectName
    )

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory("$ProjectName\venv\Lib\site-packages", "$ProjectName\package.zip")


    Compress-Archive -Path "$ProjectName\main.py" -Update -DestinationPath "$ProjectName\package.zip"
}

# Call the function with the provided parameter
Package-Project -ProjectName $ProjectName