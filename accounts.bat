@ECHO off
chcp 65001 >nul
    echo ======================= сброс пароля =======================
    set /p "choice=Сбросить пароль = [1]; Проверить сброс = [2]. = "
    if '%choice%' == '1' powershell -Command "Start-Process -FilePath 'cmd' -Verb RunAs -ArgumentList '/c net accounts /maxpwage:unlimited && pause'" 
    if '%choice%' == '2' net accounts
pause