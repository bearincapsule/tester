@ECHO off
chcp 65001 >nul
START /MAX tools\terminal\wt.exe -d . cmd /c "main-script.bat"
