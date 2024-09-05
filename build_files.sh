#!/bin/bash

# Exit script on error
set -e

# Define virtual environment and requirements file
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"

# Create a virtual environment
python -m venv $VENV_DIR

# Activate the virtual environment
source $VENV_DIR/bin/activate  # For Windows: $VENV_DIR\Scripts\activate

# Upgrade pip to the latest version
pip install --upgrade pip

# Install the dependencies
pip install -r $REQUIREMENTS_FILE

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate

# Additional build steps (if any)
# ...

# Deactivate the virtual environment
deactivate
