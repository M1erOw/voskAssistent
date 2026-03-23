@echo off

IF NOT EXIST venv (
    python -m venv venv
)

call venv/Scripts/activate

pip install -r requirements.txt -q

python main.py & CALL CALL

exit /b