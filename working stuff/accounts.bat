@ECHO off
chcp 65001 >nul
    echo ======================= сброс пароля =======================
    net accounts | findstr /c:"Maximum password age (days):"
    set /p "choice=Сбросить пароль = [1]; Пропустить ENTER. = "
    if '%choice%' == '1' powershell -Command "Start-Process -FilePath 'cmd' -Verb RunAs -ArgumentList '/c chcp 65001 >nul && net accounts /maxpwage:unlimited && pause'"