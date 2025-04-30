@ECHO off
chcp 65001 >nul
title tester

ECHO ============================

ECHO HARDWARE INFO

ECHO ============================

wmic csproduct get IdentifyingNumber,Name

systeminfo | findstr /c:"Total Physical Memory"

wmic cpu get name

wmic diskdrive get name,model,size

wmic path win32_videocontroller get name

wmic path win32_VideoController get CurrentHorizontalResolution,CurrentVerticalResolution

    set "choice="
    set /p "choice=Нужно ли запустить HWiNFO(для подробной информации)[1 - нет(по-умолчанию), 2 - да] = "
    if '%choice%' == '2' start HWiNFO64\HWiNFO64.exe
pause
    echo ======================= проверка стерео =======================
    pause
        speaker_test.mp4
pause
    echo ======================= проверка камеры =======================
    pause
        start Camera.exe
pause
    echo ======================= проверка ssd =======================
    pause 
        start CrystalDiskInfo\DiskInfo64.exe
pause
    echo ======================= удаление логов CrystalDisk =======================
        @RD /S /Q "CrystalDiskInfo\Smart"
pause
    echo ======================= проверка батареи =======================
    pause
        start gBatteryInfoView.exe
pause
    echo ======================= проверка экрана =======================
    pause
        start IsMyLcdOK_x64.exe
pause
    echo ======================= проверка клавиатуры =======================
    pause
        start Keyboard.exe
pause
    echo ======================= проверка микрофона через микшер =======================
    pause
        start Sound
pause
    echo ======================= проверка параметров входа через диспетчер устройств =======================
    pause
        devmgmt.msc
pause
    call accounts.bat
pause
    set /p "choice=Нужно ли проверить тачскрин?[1 - нет(по-умолчанию), 2 - да] = "
    if '%choice%' == '2' start IsMyTouchScreenOK_x64.exe
pause
    echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    echo === НЕ ЗАБУДЬ ПРОВЕРИТЬ КНОПКИ ТАЧПАДА И САМ ТАЧПАД!!! ===
    echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
pause
echo ============================================================
echo ======================= тест окончен =======================
echo ============================================================
pause
