@ECHO off
chcp 65001 >nul
terminal\wt.exe -d . cmd /c "START /MAX cmd /c ".\tester-new.bat""
