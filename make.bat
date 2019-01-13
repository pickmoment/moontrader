@echo off
if "%1" == "env" ( goto env )
if "%1" == "in" ( goto in )
if "%1" == "install" ( goto install )
if "%1" == "out" ( goto out )
if "%1" == "test" ( goto test )
goto :eof

:env
virtualenv .env
echo "VirtualENV Setup Complete!!! Now run: make in"
goto :eof

:in
.env\Scripts\activate.bat
goto :eof

:install
pip install -r requirements-dev.txt
python setup.py develop
goto :eof

:out
.env\Scripts\deactivate.bat
goto :eof

:test
python -m pytest -v --cov=todo --cov-report=term --cov-report=html:coverage-report tests/
goto :eof