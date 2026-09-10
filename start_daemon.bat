@echo off
chcp 65001 >nul
cd /d %~dp0

echo ================================================
echo  2027 수시 경쟁률 자동 수집 시작 (10분 간격)
echo  이 창을 끄면 수집이 멈춥니다. 켜 두세요.
echo ================================================
echo.

echo [1/3] 최신 코드/데이터 받아오는 중...
for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%b
git fetch origin %BRANCH%
git merge -X ours --no-edit origin/%BRANCH%

echo [2/3] 필요한 패키지 확인 중...
pip install --quiet beautifulsoup4 openpyxl

echo [3/3] 수집 시작!
echo.
python auto_fetch_competition.py --daemon 10

pause
