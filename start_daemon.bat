@echo off
chcp 65001 >nul
cd /d %~dp0

echo ================================================
echo  2027 수시 경쟁률 자동 수집 시작 (10분 간격)
echo  이 창을 끄면 수집이 멈춥니다. 켜 두세요.
echo ================================================
echo.

pip install --quiet beautifulsoup4 openpyxl

python auto_fetch_competition.py --daemon 10

pause
