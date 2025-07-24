import subprocess
import os

def run(command, shell=True, wait=True):
    if wait:
        subprocess.run(command, shell=shell)
    else:
        subprocess.Popen(command, shell=shell)

print("=" * 30)
print("HARDWARE INFO")
print("=" * 30)

run("wmic csproduct get IdentifyingNumber,Name")
run('systeminfo | findstr /c:"Total Physical Memory"')
run("wmic cpu get name")
run("wmic diskdrive get name,model,size")
run("wmic path win32_videocontroller get name")
run("wmic path win32_VideoController get CurrentHorizontalResolution,CurrentVerticalResolution")

choice = input("Нужно ли запустить HWiNFO(для подробной информации)? [1 - нет(по-умолчанию), 2 - да]: ")
if choice.strip() == '2':
    run("start HWiNFO64\\HWiNFO64.exe")

input("Нажмите Enter для проверки стерео...")
run("speaker_test.mp4")

input("Нажмите Enter для проверки камеры...")
run("start Camera.exe")

input("Нажмите Enter для проверки SSD...")
run("start CrystalDiskInfo\\DiskInfo64.exe")

input("Нажмите Enter для удаления логов CrystalDisk...")
run('rd /s /q "CrystalDiskInfo\\Smart"')

input("Нажмите Enter для проверки батареи...")
run("start gBatteryInfoView.exe")

input("Нажмите Enter для проверки экрана...")
run("start IsMyLcdOK_x64.exe")

input("Нажмите Enter для проверки клавиатуры...")
run("start Keyboard.exe")

input("Нажмите Enter для проверки микрофона...")
run("start Sound")

input("Нажмите Enter для проверки параметров входа (диспетчер устройств)...")
run("devmgmt.msc")

run("call accounts.bat")

touch_choice = input("Нужно ли проверить тачскрин? [1 - нет(по-умолчанию), 2 - да]: ")
if touch_choice.strip() == '2':
    run("start IsMyTouchScreenOK_x64.exe")

print("!!! НЕ ЗАБУДЬ ПРОВЕРИТЬ КНОПКИ ТАЧПАДА И САМ ТАЧПАД !!!")

print("=" * 60)
print("ТЕСТ ОКОНЧЕН")
print("=" * 60)
input("Нажмите Enter для выхода...")
