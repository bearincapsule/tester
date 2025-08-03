@ECHO off
chcp 65001 >nul
START /MAX terminal\wt.exe -d . cmd /c ".\tester-new.bat"
