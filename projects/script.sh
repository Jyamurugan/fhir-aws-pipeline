#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <folder_name>"
    exit 1
fi

FOLDER=$1

cd "$FOLDER" || { echo "Folder not found: $FOLDER"; exit 1; }

uv export --frozen --no-dev --no-editable -o requirements.txt
uv pip install \
     --no-installer-metadata \
     --no-compile-bytecode \
     --python-platform x86_64-manylinux2014 \
     --python 3.12 \
     --target packages \
     -r requirements.txt

cd packages
zip -r ../package.zip .
cd ..

zip -r package.zip app