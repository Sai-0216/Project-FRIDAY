@echo off
setlocal

title FRIDAY

echo ========================================
echo        Starting FRIDAY
echo ========================================
echo.

REM ========================================
REM OLLAMA GPU CONFIGURATION
REM ========================================

set OLLAMA_VULKAN=1
set OLLAMA_IGPU_ENABLE=1

echo [1/4] Starting Ollama...

REM ========================================
REM CHECK WHETHER OLLAMA IS ALREADY RUNNING
REM ========================================

curl -s http://127.0.0.1:11434/api/tags >nul 2>&1

if %errorlevel%==0 (
    echo Ollama is already running.
) else (
    echo Starting Ollama server...

    start "" /B ollama serve

    echo Waiting for Ollama...

    :WAIT_OLLAMA
    timeout /t 1 /nobreak >nul

    curl -s http://127.0.0.1:11434/api/tags >nul 2>&1

    if not %errorlevel%==0 (
        goto WAIT_OLLAMA
    )

    echo Ollama is ready.
)

echo.
echo [2/4] Preloading Qwen...

REM ========================================
REM PRELOAD QWEN
REM ========================================
REM
REM This loads Qwen into GPU memory before
REM FRIDAY starts listening.
REM
REM keep_alive=30m keeps the model loaded.
REM ========================================

curl -s http://127.0.0.1:11434/api/generate ^
    -H "Content-Type: application/json" ^
    -d "{\"model\":\"qwen2.5:1.5b\",\"prompt\":\"Hi\",\"stream\":false,\"keep_alive\":\"30m\",\"options\":{\"num_predict\":1}}" ^
    >nul

if %errorlevel%==0 (
    echo Qwen is loaded and ready.
) else (
    echo WARNING: Could not preload Qwen.
)

echo.
echo [3/4] Starting FRIDAY...

REM ========================================
REM ACTIVATE VIRTUAL ENVIRONMENT
REM ========================================

call .venv\Scripts\activate.bat

REM ========================================
REM START FRIDAY
REM ========================================

python main.py

echo.
echo ========================================
echo        FRIDAY has stopped.
echo ========================================

pause