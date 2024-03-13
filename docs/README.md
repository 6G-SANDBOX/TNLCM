[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white&labelColor=3776AB)](https://www.python.org/downloads/release/python-3122/)
[![Flask](https://img.shields.io/badge/Flask-3.0.2+-brightgreen?style=for-the-badge&logo=flask&logoColor=white&labelColor=000000)](https://flask.palletsprojects.com/en/3.0.x/)

# TRIAL NETWORK LIFECYCLE MANAGER (TNLCM)

## Start TNLCM

Create python environment and install libraries. The environment must be created inside the TNLCM project

* Windows

        # Create environment
        python -m venv venv

        # Activate environment
        ./venv/Scripts/activate.ps1

        # Install libraries
        pip install -r requirements.txt

* Ubuntu

        # Create environment
        python3 -m venv venv

        # Activate environment
        source venv/bin/activate
        
        # Install libraries
        pip install -r requirements.txt

With the environment activated, start TNLCM

    python app.py