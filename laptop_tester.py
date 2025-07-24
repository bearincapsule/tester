#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
import subprocess
import platform
import psutil
import time
import json
import shutil
from datetime import datetime
from pathlib import Path

class LaptopTester:
    def __init__(self):
        self.results = {}
        self.csv_file = "test_results.csv"
        self.start_time = datetime.now()
        self.setup_csv()
        
    def setup_csv(self):
        """Создает CSV файл с заголовками если его нет"""
        if not os.path.exists(self.csv_file):
            headers = [
                'Номер', 'Бренд', 'Модель', 'Серийный номер', 'CPU', 'RAM', 'SSD', 'LTE', 'Touchscreen',
                'Проверил работоспособность:', 'Пароль BIOS:', 'Батарейка CMOS', 'Подключение АКБ:',
                'Разъемы:', 'Звук (левый канал/правый канал):', 'Камера:', 
                'SSD (категория/часы наработки/циклы включения):', 'Циклы АКБ (1):', 'Емкость АКБ (1):',
                'Циклы АКБ (2):', 'Емкость АКБ (2):', 'Цвета:', 'Клавиатура:', 'Микрофон:',
                'Сканер лица/пальца:', 'Драйверы:', 'Сброс срока действия пароля:', 'Тачскрин:',
                'Кнопки трекпада:', 'Сенсор трекпада:', 'Комментарий'
            ]
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
    
    def run_command(self, command, capture_output=True, shell=True, encoding='cp866'):
        """Выполняет команду и возвращает результат"""
        try:
            if capture_output:
                result = subprocess.run(command, shell=shell, capture_output=True, text=True, encoding=encoding)
                return result.stdout.strip()
            else:
                subprocess.run(command, shell=shell)
                return True
        except Exception as e:
            print(f"Ошибка выполнения команды: {e}")
            return None
    
    def ask_user_result(self, test_name, details=""):
        """Спрашивает пользователя о результате теста"""
        print(f"\n{'='*50}")
        print(f"РЕЗУЛЬТАТ ТЕСТА: {test_name}")
        if details:
            print(f"Детали: {details}")
        print(f"{'='*50}")
        
        while True:
            result = input("Тест прошел успешно? [y/n/s] (y-да, n-нет, s-пропустить): ").lower().strip()
            if result in ['y', 'yes', 'да', 'д']:
                return True
            elif result in ['n', 'no', 'нет', 'н']:
                note = input("Опишите проблему (необязательно): ")
                return (False, note) if note else False
            elif result in ['s', 'skip', 'пропустить', 'п']:
                return None
            else:
                print("Пожалуйста, введите y, n или s")
    
    def get_hardware_info(self):
        """Собирает информацию о железе через командную строку"""
        print("\n" + "="*50)
        print("СБОР ИНФОРМАЦИИ О ЖЕЛЕЗЕ")
        print("="*50)
        
        # Серийный номер и модель
        try:
            serial_cmd = "wmic csproduct get IdentifyingNumber /value"
            model_cmd = "wmic csproduct get Name /value"
            
            serial_output = self.run_command(serial_cmd)
            model_output = self.run_command(model_cmd)
            
            # Извлекаем значения из вывода wmic
            serial = "Unknown"
            model = "Unknown"
            
            for line in serial_output.split('\n'):
                if 'IdentifyingNumber=' in line:
                    serial = line.split('=', 1)[1].strip()
                    break
                    
            for line in model_output.split('\n'):
                if 'Name=' in line:
                    model = line.split('=', 1)[1].strip()
                    break
        
            print(f"Серийный номер: {serial}")
            print(f"Модель: {model}")
            
            # CPU через wmic вместо platform.processor()
            cpu_cmd = "wmic cpu get Name /value"
            cpu_output = self.run_command(cpu_cmd)
            cpu_info = "Unknown"
            if cpu_output:
                for line in cpu_output.split('\n'):
                    if 'Name=' in line:
                        cpu_info = line.split('=', 1)[1].strip()
                        break
        
            print(f"Процессор: {cpu_info}")
            
            # RAM через psutil с округлением до известных значений
            ram_gb = psutil.virtual_memory().total / (1024 ** 3)
            # Список известных значений RAM в GB
            known_ram_sizes = [2, 4, 6, 8, 12, 16, 24, 32, 64, 128]
            # Находим ближайшее известное значение
            ram_rounded = min(known_ram_sizes, key=lambda x: abs(x - ram_gb))
            print(f"Память: {ram_rounded} GB")
            
            # Диски через psutil
            disk_info = []
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append(f"{partition.device} {usage.total // (1024**3)}GB")
                except PermissionError:
                    pass
            disk_str = ", ".join(disk_info)
            print(f"Диски: {disk_str}")
            
            # GPU через wmic
            gpu_cmd = "wmic path win32_videocontroller get name /value"
            gpu_output = self.run_command(gpu_cmd)
            gpu = "Unknown"
            for line in gpu_output.split('\n'):
                if 'Name=' in line and line.split('=', 1)[1].strip():
                    gpu = line.split('=', 1)[1].strip()
                    break
            print(f"Видеокарта: {gpu}")
            
            # Разрешение экрана через wmic
            resolution_cmd = "wmic path win32_VideoController get CurrentHorizontalResolution,CurrentVerticalResolution /value"
            resolution_output = self.run_command(resolution_cmd)
            width = height = "Unknown"
            for line in resolution_output.split('\n'):
                if 'CurrentHorizontalResolution=' in line:
                    width = line.split('=', 1)[1].strip()
                elif 'CurrentVerticalResolution=' in line:
                    height = line.split('=', 1)[1].strip()
            
            resolution = f"{width}x{height}" if width != "Unknown" and height != "Unknown" else "Unknown"
            print(f"Разрешение экрана: {resolution}")
            
            # Сохраняем в результаты
            self.results.update({
                'serial_number': serial,
                'model': model,
                'cpu': cpu_info,
                'ram_gb': ram_gb,
                'disk_info': disk_str,
                'gpu': gpu,
                'screen_resolution': resolution
            })
            
        except Exception as e:
            print(f"Ошибка при сборе информации о железе: {e}")
            return False
        
        return self.ask_user_result("Сбор информации о железе", "Проверьте правильность отображенной информации")
    
    def test_hwinfo(self):
        """Тест HWiNFO64"""
        print("\n" + "="*50)
        print("HWINFO64 - ПОДРОБНАЯ ИНФОРМАЦИЯ")
        print("="*50)
        
        choice = input("Запустить HWiNFO64 для подробной информации? [1-нет, 2-да]: ").strip()
        
        if choice == '2':
            hwinfo_path = "HWiNFO64\\HWiNFO64.exe"
            if os.path.exists(hwinfo_path):
                print("Запускаем HWiNFO64...")
                subprocess.Popen(hwinfo_path)
                input("Нажмите Enter после просмотра информации в HWiNFO64...")
                result = self.ask_user_result("HWiNFO64", "Проверьте информацию о железе в HWiNFO64")
                self.results['hwinfo_ran'] = result
                return result
            else:
                print("HWiNFO64.exe не найден!")
                self.results['hwinfo_ran'] = False
                return False
        else:
            self.results['hwinfo_ran'] = False
            return None
    
    def test_audio(self):
        """Тест аудио"""
        print("\n" + "="*50)
        print("ТЕСТ АУДИО/ДИНАМИКОВ")
        print("="*50)
        
        # Показываем аудио устройства через PowerShell
        print("Доступные аудио устройства:")
        audio_devices_cmd = 'powershell "Get-WmiObject -Class Win32_SoundDevice | Select-Object Name, Status"'
        audio_devices = self.run_command(audio_devices_cmd, encoding='utf-8')
        print(audio_devices)
        
        # Проверяем наличие тестового файла
        audio_files = ["speaker_test.mp4", "speaker_test.wav"]
        audio_file = None
        
        for file in audio_files:
            if os.path.exists(file):
                audio_file = file
                break
        
        if audio_file:
            print(f"\nВоспроизводим тестовый файл: {audio_file}")
            try:
                os.startfile(audio_file)
                result = self.ask_user_result("Тест аудио", "Слышны ли звуки из динамиков?")
                self.results['audio_test_ok'] = result
                return result
            except Exception as e:
                print(f"Ошибка воспроизведения: {e}")
                result = self.ask_user_result("Тест аудио", f"Ошибка воспроизведения: {e}")
                self.results['audio_test_ok'] = result
                return result
        else:
            print("Тестовые аудио файлы не найдены!")
            result = self.ask_user_result("Тест аудио", "Тестовые файлы не найдены, проверьте аудио вручную")
            self.results['audio_test_ok'] = result
            return result
    
    def test_camera(self):
        """Тест камеры"""
        print("\n" + "="*50)
        print("ТЕСТ КАМЕРЫ")
        print("="*50)
        
        # Показываем камеры через PowerShell
        print("Доступные камеры:")
        camera_cmd = 'powershell "Get-WmiObject -Class Win32_PnPEntity | Where-Object {$_.Name -like \'*camera*\' -or $_.Name -like \'*webcam*\'} | Select-Object Name, Status"'
        cameras = self.run_command(camera_cmd, encoding='utf-8')
        print(cameras)
        
        # Пробуем запустить разные варианты камеры
        camera_apps = ["Camera.exe", "start ms-camera:"]
        
        for app in camera_apps:
            if app == "Camera.exe" and not os.path.exists(app):
                continue
                
            print(f"\nЗапускаем камеру: {app}")
            try:
                if app.startswith("start"):
                    subprocess.Popen(app, shell=True)
                else:
                    subprocess.Popen(app)
                input("Нажмите Enter после проверки камеры...")
                result = self.ask_user_result("Тест камеры", "Работает ли камера корректно?")
                self.results['camera_ok'] = result
                return result
            except Exception as e:
                print(f"Ошибка запуска {app}: {e}")
                continue
        
        # Если ничего не сработало
        result = self.ask_user_result("Тест камеры", "Не удалось запустить приложение камеры")
        self.results['camera_ok'] = result
        return result
    
    def get_disk_smart_info(self):
        """Получает SMART информацию о дисках через smartctl"""
        print("\n=== SMART ИНФОРМАЦИЯ (smartctl) ===")
        smartctl_path = os.path.join("smartmontools", "bin", "smartctl.exe")
        if not os.path.exists(smartctl_path):
            print("smartctl.exe не найден! Проверьте наличие smartmontools в smartmontools\\bin")
            return

        # Сканируем доступные диски
        scan_cmd = f'"{smartctl_path}" --scan'
        found = False
        
        try:
            scan_output = self.run_command(scan_cmd, encoding='utf-8')
            if not scan_output:
                print("Не удалось найти диски")
                return
            
            # Перебираем найденные диски
            for line in scan_output.splitlines():
                if not line.strip():
                    continue
                device = line.split()[0]  # Получаем путь устройства
                
                print(f"\n--- SMART для {device} ---")
                cmd = f'"{smartctl_path}" -a {device}'
                
                try:
                    output = self.run_command(cmd, encoding='utf-8')
                    if output and ("SMART support is: Enabled" in output or "SMART/Health Information" in output):
                        found = True
                        power_cycles = ""
                        power_hours = ""
                        
                        for line in output.splitlines():
                            if "Power Cycles:" in line:
                                power_cycles = line.split(":")[1].strip()
                            if "Power On Hours:" in line:
                                power_hours = line.split(":")[1].strip()
                                
                        # Сохраняем в формате "категория/часы/циклы"
                        smart_info = f"A/{power_hours}/{power_cycles}"
                        self.results['smart_info'] = smart_info
                        
                        # Ищем только нужные строки
                        for line in output.splitlines():
                            if any(key in line for key in [
                                "Power Cycles:", 
                                "Power On Hours:"
                            ]):
                                print(line.strip())
                                
                        # Проверяем наличие ошибок
                        if "FAILED" in output or "Critical Warning: 0x01" in output:
                            print("\n⚠ ВНИМАНИЕ: Обнаружены ошибки SMART!")
                    else:
                        print("Нет SMART-данных для этого диска")
                except Exception as e:
                    print(f"Ошибка при опросе {device}: {e}")

            if not found:
                print("Не удалось получить SMART-информацию ни по одному диску. Запустите скрипт от имени администратора!")
            
        except Exception as e:
            print(f"Ошибка при сканировании дисков: {e}")
    
    def test_ssd(self):
        """Тест SSD через SMART"""
        print("\n" + "="*50)
        print("ТЕСТ SSD/HDD")
        print("="*50)
        
        # Получаем SMART информацию
        print("\n=== SMART ИНФОРМАЦИЯ ===")
        self.get_disk_smart_info()
        
        result = self.ask_user_result("Тест SSD/HDD", "Проверьте состояние дисков, часы работы и SMART показатели")
        self.results['ssd_tool_ok'] = result
        return result
    

    def test_battery(self):
        """Тест батареи - проверка здоровья и циклов зарядки"""
        print("\n" + "="*50)
        print("ТЕСТ БАТАРЕИ")
        print("="*50)

        print("\nСоздание отчета о батарее...")
        self.run_command('powercfg /batteryreport /output battery_report.html')
        
        if os.path.exists('battery_report.html'):
            try:
                with open('battery_report.html', 'r', encoding='utf-8') as f:
                    content = f.read()
                    cycles = ""
                    health = ""
                    
                    if "<span class=\"label\">CYCLE COUNT</span></td><td>" in content:
                        cycles = content[content.find("<span class=\"label\">CYCLE COUNT</span></td><td>") + 47:]
                        cycles = cycles[:cycles.find("</td>")]
                        self.results['battery_cycles'] = cycles
                    
                    # Расчет здоровья батареи
                    if "<span class=\"label\">DESIGN CAPACITY</span></td><td>" in content:
                        design = content[content.find("<span class=\"label\">DESIGN CAPACITY</span></td><td>") + 51:]
                        design = int(float(design[:design.find(" mWh")].replace(',', '')))
                        
                        current = content[content.find("<span class=\"label\">FULL CHARGE CAPACITY</span></td><td>") + 56:]
                        current = int(float(current[:current.find(" mWh")].replace(',', '')))
                        
                        health = round((current / design) * 100, 2)
                        self.results['battery_health'] = f"{health}%"

            except Exception as e:
                print(f"Ошибка при чтении отчета: {e}")
            
            choice = input("\nОткрыть полный отчет? [y/n]: ").lower().strip()
            if choice in ['y', 'yes', 'да', 'д']:
                os.startfile('battery_report.html')
    
        result = self.ask_user_result("Тест батареи", "Проверьте состояние батареи (циклы и здоровье)")
        self.results['battery_ok'] = result
        return result
    
    def test_screen(self):
        """Тест экрана"""
        print("\n" + "="*50)
        print("ТЕСТ ЭКРАНА")
        print("="*50)
        
        # Показываем информацию об экране
        print("Информация об экране:")
        monitor_cmd = 'wmic path Win32_VideoController get Name,VideoModeDescription,CurrentHorizontalResolution,CurrentVerticalResolution /format:table'
        monitor_info = self.run_command(monitor_cmd)
        print(monitor_info)
        
        screen_exe = "IsMyLcdOK_x64.exe"
        if os.path.exists(screen_exe):
            print("Запускаем IsMyLcdOK...")
            subprocess.Popen(screen_exe)
            input("Нажмите Enter после проверки экрана...")
        else:
            print("IsMyLcdOK_x64.exe не найден!")
            print("Проверьте экран визуально на:")
            print("- Битые пиксели")
            print("- Равномерность подсветки") 
            print("- Артефакты изображения")
            input("Нажмите Enter после визуальной проверки...")
        
        result = self.ask_user_result("Тест экрана", "Проверьте экран на битые пиксели и артефакты")
        self.results['screen_ok'] = result
        return result
    
    def test_keyboard(self):
        """Тест клавиатуры"""
        print("\n" + "="*50)
        print("ТЕСТ КЛАВИАТУРЫ")
        print("="*50)
        
        keyboard_exe = "Keyboard.exe"
        if os.path.exists(keyboard_exe):
            print("Запускаем тест клавиатуры...")
            subprocess.Popen(keyboard_exe)
            input("Нажмите Enter после проверки всех клавиш...")
        else:
            print("Keyboard.exe не найден!")
            print("Откройте блокнот и проверьте клавиши вручную...")
            subprocess.Popen("notepad.exe")
            input("Проверьте все клавиши в блокноте. Нажмите Enter когда закончите...")
        
        result = self.ask_user_result("Тест клавиатуры", "Работают ли все клавиши корректно?")
        self.results['keyboard_ok'] = result
        return result
    
    def test_mouse(self):
        """Тест мыши/тачпада"""
        print("\n" + "="*50)
        print("ТЕСТ МЫШИ/ТАЧПАДА")
        print("="*50)
        
        # Показываем информацию о мыши
        print("Устройства ввода:")
        mouse_cmd = 'wmic path Win32_PointingDevice get Name,DeviceInterface,Status /format:table'
        mouse_info = self.run_command(mouse_cmd)
        print(mouse_info)
        
        print("\nПроверьте следующие функции:")
        print("- Движение курсора")
        print("- Левая кнопка мыши/тачпада")
        print("- Правая кнопка мыши/тачпада")
        print("- Колесо прокрутки")
        print("- Жесты тачпада (если есть)")
        
        input("Проверьте все функции мыши/тачпада. Нажмите Enter когда закончите...")
        
        result = self.ask_user_result("Тест мыши/тачпада", "Работают ли все функции мыши/тачпада?")
        self.results['mouse_test_ok'] = result
        return result
    
    def test_microphone(self):
        """Тест микрофона"""
        print("\n" + "="*50)
        print("ТЕСТ МИКРОФОНА")
        print("="*50)
        
        # Показываем аудио устройства записи
        print("Устройства записи:")
        mic_cmd = 'powershell "Get-WmiObject -Class Win32_SoundDevice | Where-Object {$_.Name -like \'*microphone*\' -or $_.Name -like \'*mic*\'} | Select-Object Name, Status"'
        mic_info = self.run_command(mic_cmd, encoding='utf-8')
        print(mic_info)
        
        # Открываем микшер звука
        print("\nОткрываем микшер звука...")
        try:
            subprocess.Popen("sndvol.exe")
        except:
            pass
        
        # Пробуем открыть настройки звука
        print("Открываем настройки звука...")
        try:
            subprocess.Popen("ms-settings:sound", shell=True)
        except:
            # Альтернативный способ через mmsys.cpl
            try:
                subprocess.Popen("mmsys.cpl")
            except:
                pass
        
        input("Говорите в микрофон и проверьте уровни в настройках звука. Нажмите Enter когда закончите...")
        result = self.ask_user_result("Тест микрофона", "Работает ли микрофон? Видны ли уровни звука?")
        self.results['microphone_ok'] = result
        return result
    
    def test_device_manager(self):
        """Проверка диспетчера устройств"""
        print("\n" + "="*50)
        print("ДИСПЕТЧЕР УСТРОЙСТВ")
        print("="*50)
        
        print("Открываем диспетчер устройств...")
        subprocess.Popen("devmgmt.msc", shell=True)
        
        print("\nПроверьте следующее:")
        print("- Нет устройств с желтыми треугольниками (предупреждения)")
        print("- Нет устройств с красными крестиками (ошибки)")
        print("- Нет неизвестных устройств")
        print("- Все драйвера установлены")
        
        input("Проверьте устройства в диспетчере. Нажмите Enter когда закончите...")
        result = self.ask_user_result("Диспетчер устройств", "Есть ли проблемные устройства или ошибки?")
        self.results['devicemanager_ok'] = result
        return result
    
    def test_accounts(self):
        """Тест настроек учетных записей"""
        print("\n" + "="*50)
        print("НАСТРОЙКИ УЧЕТНЫХ ЗАПИСЕЙ")
        print("="*50)
        
        print("Текущие настройки учетных записей:")
        subprocess.run("net accounts", shell=True)
        
        print("\n1 - Сбросить пароль (установить максимальный срок действия: unlimited)")
        print("2 - Пропустить")
        choice = input("Выберите действие [1/2]: ").strip()
        
        if choice == '1':
            print("Сбрасываем настройки пароля...")
            try:
                # Пробуем выполнить команду напрямую
                result = subprocess.run("net accounts /maxpwage:unlimited", shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print("Настройки успешно изменены")
                    self.results['accounts_configured'] = True
                else:
                    print(f"Ошибка: {result.stderr}")
                    print("Попробуйте запустить скрипт от имени администратора")
                    self.results['accounts_configured'] = False
            except Exception as e:
                print(f"Ошибка выполнения команды: {e}")
                self.results['accounts_configured'] = False
        else:
            print("Пропускаем настройки учетных записей")
            self.results['accounts_configured'] = False
        
        input("Нажмите Enter для продолжения...")
        return self.results['accounts_configured']
    
    def test_touchscreen(self):
        """Тест тачскрина"""
        print("\n" + "="*50)
        print("ТЕСТ ТАЧСКРИНА")
        print("="*50)
        
        # Проверяем есть ли тачскрин
        touch_cmd = 'powershell "Get-WmiObject -Class Win32_PnPEntity | Where-Object {$_.Name -like \'*touch*\' -or $_.Name -like \'*digitizer*\'} | Select-Object Name, Status"'
        touch_devices = self.run_command(touch_cmd, encoding='utf-8')
        print("Устройства сенсорного ввода:")
        print(touch_devices)
        
        if "touch" in touch_devices.lower() or "digitizer" in touch_devices.lower():
            choice = input("Обнаружен тачскрин. Нужно ли его протестировать? [1-нет, 2-да]: ").strip()
        else:
            choice = input("Тачскрин не обнаружен. Все равно протестировать? [1-нет, 2-да]: ").strip()
        
        if choice == '2':
            touchscreen_exe = "IsMyTouchScreenOK_x64.exe"
            if os.path.exists(touchscreen_exe):
                print("Запускаем тест тачскрина...")
                subprocess.Popen(touchscreen_exe)
                input("Нажмите Enter после проверки тачскрина...")
            else:
                print("IsMyTouchScreenOK_x64.exe не найден!")
                print("Проверьте тачскрин вручную - касайтесь экрана и проверяйте реакцию")
                input("Нажмите Enter после проверки...")
            
            result = self.ask_user_result("Тест тачскрина", "Работает ли тачскрин корректно?")
            self.results['touchscreen_ok'] = result
            return result
        else:
            self.results['touchscreen_ok'] = None
            return None
    
    def test_touchpad_buttons(self):
        """Проверка кнопок тачпада"""
        print("\n" + "="*50)
        print("ПРОВЕРКА КНОПОК ТАЧПАДА")
        print("="*50)
        
        print("Проверьте следующие элементы тачпада:")
        print("- Левая кнопка тачпада")
        print("- Правая кнопка тачпада")
        print("- Средняя кнопка (если есть)")
        print("- Физические кнопки (если есть)")
        print("- Зоны нажатия на самом тачпаде")
        
        input("Проверьте все кнопки и зоны тачпада. Нажмите Enter когда закончите...")
        
        result = self.ask_user_result("Кнопки тачпада", "Работают ли все кнопки и зоны тачпада?")
        self.results['touchpad_ok'] = result
        return result
    
    def save_results(self):
        """Сохраняет результаты в CSV файл"""
        print("\n" + "="*50)
        print("СОХРАНЕНИЕ РЕЗУЛЬТАТОВ")
        print("="*50)

        # Запрашиваем обязательные поля
        notebook_number = input("Введите номер ноутбука: ").strip()
        comment = input("Комментарий (если есть): ").strip()
        checker_name = input("Введите имя проверяющего: ").strip()

        # Извлекаем модель процессора из полного названия
        cpu_model = ""
        if self.results.get('cpu'):
            if "i5-" in self.results['cpu']:
                cpu_model = "i5-" + self.results['cpu'].split("i5-")[1].split()[0]
            elif "i7-" in self.results['cpu']:
                cpu_model = "i7-" + self.results['cpu'].split("i7-")[1].split()[0]

        # Формируем строку с данными
        row = {
            'Номер': notebook_number,
            'Бренд': self.results.get('model', '').split()[0] if self.results.get('model') else '',
            'Модель': ' '.join(self.results.get('model', '').split()[1:]) if self.results.get('model') else '',
            'Серийный номер': self.results.get('serial_number', ''),
            'CPU': cpu_model,
            'RAM': f"{int(self.results.get('ram_gb', 0))} GB DDR4",
            'SSD': f"{int(self.results.get('disk_info', '').split()[1].replace('GB',''))} GB" if self.results.get('disk_info') else '',
            'LTE': '',
            'Touchscreen': '',
            'Проверил работоспособность:': checker_name,
            'Пароль BIOS:': 'Сброшен' if self.results.get('accounts_configured') else '',
            'Батарейка CMOS': '',
            'Подключение АКБ:': 'Подключен',
            'Разъемы:': '+' if self.results.get('devicemanager_ok') else '',
            'Звук (левый канал/правый канал):': '+ / +' if self.results.get('audio_test_ok') else '',
            'Камера:': '+' if self.results.get('camera_ok') else '',
            'SSD (категория/часы наработки/циклы включения):': self.results.get('smart_info', ''),  # Из SMART
            'Циклы АКБ (1):': self.results.get('battery_cycles', ''),  # Из отчета батареи
            'Емкость АКБ (1):': self.results.get('battery_health', ''),  # Из отчета батареи
            'Циклы АКБ (2):': '',
            'Емкость АКБ (2):': '',
            'Цвета:': '+' if self.results.get('screen_ok') else '',
            'Клавиатура:': '+' if self.results.get('keyboard_ok') else '',
            'Микрофон:': '+' if self.results.get('microphone_ok') else '',
            'Сканер лица/пальца:': '+ / -',
            'Драйверы:': '+' if self.results.get('devicemanager_ok') else '',
            'Сброс срока действия пароля:': 'Сброшен' if self.results.get('accounts_configured') else '',
            'Тачскрин:': 'Его нет' if not self.results.get('touchscreen_ok') else '+',
            'Кнопки трекпада:': '+' if self.results.get('touchpad_ok') else '',
            'Сенсор трекпада:': '+' if self.results.get('mouse_test_ok') else '',
            'Комментарий': comment
        }

        # Читаем существующие заголовки из файла
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            headers = next(csv.reader(f))

        # Записываем новую строку
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writerow(row)

        print(f"Результаты сохранены в {self.csv_file}")
    
    def run_all_tests(self):
        """Запускает все тесты по порядку"""
        print("="*60)
        print("ЗАПУСК ТЕСТИРОВАНИЯ НОУТБУКА")
        print(f"Время начала: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        try:
            # Последовательность тестов
            tests = [
                ("Сбор информации о железе", self.get_hardware_info),
                ("HWiNFO64", self.test_hwinfo),
                ("Аудио/Динамики", self.test_audio),
                ("Камера", self.test_camera),
                ("SSD/HDD", self.test_ssd),
                ("Батарея", self.test_battery),
                ("Экран", self.test_screen),
                ("Клавиатура", self.test_keyboard),
                ("Мышь/Тачпад", self.test_mouse),
                ("Микрофон", self.test_microphone),
                ("Диспетчер устройств", self.test_device_manager),
                ("Настройки учетных записей", self.test_accounts),
                ("Тачскрин", self.test_touchscreen),
                ("Кнопки тачпада", self.test_touchpad_buttons)
            ]
            
            print(f"\nВсего тестов для выполнения: {len(tests)}")
            
            for i, (test_name, test_func) in enumerate(tests, 1):
                print(f"\n[{i}/{len(tests)}] Выполняется: {test_name}")
                try:
                    test_func()
                except KeyboardInterrupt:
                    print(f"\nТест '{test_name}' прерван пользователем")
                    break
                except Exception as e:
                    print(f"Ошибка в тесте '{test_name}': {e}")
                    # Спрашиваем пользователя, продолжать ли
                    continue_choice = input("Продолжить тестирование? [y/n]: ").lower().strip()
                    if continue_choice not in ['y', 'yes', 'да', 'д']:
                        break
            
            # Финальное напоминание
            print("\n" + "!"*60)
            print("ФИНАЛЬНАЯ ПРОВЕРКА ЗАВЕРШЕНА!")
            print("Убедитесь, что все компоненты работают корректно.")
            print("!"*60)
            
            # Сохраняем результаты
            self.save_results()
            
            print("\n" + "="*60)
            print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
            print(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Результаты сохранены в: {self.csv_file}")
            print("="*60)
            
        except KeyboardInterrupt:
            print("\n\nТестирование прервано пользователем")
            self.save_results()
        except Exception as e:
            print(f"\nКритическая ошибка во время тестирования: {e}")
            self.save_results()

def main():
    """Главная функция"""
    try:
        # Проверяем ОС
        if platform.system() != "Windows":
            print("Внимание: Скрипт оптимизирован для Windows")
        
        # Устанавливаем кодировку консоли для Windows
        if platform.system() == "Windows":
            try:
                os.system("chcp 65001 >nul 2>&1")
            except:
                pass
        
        print("Добро пожаловать в систему тестирования ноутбуков!")
        print("Для получения наилучших результатов запустите скрипт от имени администратора.")
        
        input("\nНажмите Enter для начала тестирования...")
        
        tester = LaptopTester()
        tester.run_all_tests()
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()