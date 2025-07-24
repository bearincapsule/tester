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
from datetime import datetime
from pathlib import Path

class LaptopTester:
    def __init__(self):
        self.results = {}
        self.csv_file = "results.csv"
        self.start_time = datetime.now()
        self.setup_csv()
        
    def setup_csv(self):
        """Создает CSV файл с заголовками если его нет"""
        if not os.path.exists(self.csv_file):
            headers = [
                'timestamp', 'serial_number', 'model', 'cpu', 'ram', 'disk', 'gpu', 
                'screen_resolution', 'hwinfo_ran', 'audio_test_ok', 'camera_ok', 
                'ssd_tool_ok', 'smart_logs_deleted', 'battery_ok', 'screen_ok', 
                'keyboard_ok', 'microphone_ok', 'devicemanager_ok', 'accounts_bat_called', 
                'touchscreen_ok', 'notes'
            ]
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
    
    def run_command(self, command, capture_output=True, shell=True):
        """Выполняет команду и возвращает результат"""
        try:
            if capture_output:
                result = subprocess.run(command, shell=shell, capture_output=True, text=True, encoding='cp866')
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
                return False, note
            elif result in ['s', 'skip', 'пропустить', 'п']:
                return None
            else:
                print("Пожалуйста, введите y, n или s")
    
    def get_hardware_info(self):
        """Собирает информацию о железе через командную строку"""
        print("\n" + "="*30)
        print("СБОР ИНФОРМАЦИИ О ЖЕЛЕЗЕ")
        print("="*30)
        
        # Серийный номер и модель
        serial_cmd = "wmic csproduct get IdentifyingNumber"
        model_cmd = "wmic csproduct get Name"
        
        serial = self.run_command(serial_cmd)
        model = self.run_command(model_cmd)
        
        # Очищаем вывод от лишних строк
        serial = serial.split('\n')[1].strip() if len(serial.split('\n')) > 1 else "Unknown"
        model = model.split('\n')[1].strip() if len(model.split('\n')) > 1 else "Unknown"
        
        print(f"Серийный номер: {serial}")
        print(f"Модель: {model}")
        
        # CPU
        cpu_cmd = "wmic cpu get name"
        cpu = self.run_command(cpu_cmd)
        cpu = cpu.split('\n')[1].strip() if len(cpu.split('\n')) > 1 else "Unknown"
        print(f"Процессор: {cpu}")
        
        # RAM
        ram_cmd = 'systeminfo | findstr /c:"Total Physical Memory"'
        ram = self.run_command(ram_cmd)
        print(f"Память: {ram}")
        
        # Диски
        disk_cmd = "wmic diskdrive get name,model,size"
        disk = self.run_command(disk_cmd)
        print("Диски:")
        print(disk)
        
        # GPU
        gpu_cmd = "wmic path win32_videocontroller get name"
        gpu = self.run_command(gpu_cmd)
        gpu_clean = gpu.split('\n')[1].strip() if len(gpu.split('\n')) > 1 else "Unknown"
        print(f"Видеокарта: {gpu_clean}")
        
        # Разрешение экрана
        resolution_cmd = "wmic path win32_VideoController get CurrentHorizontalResolution,CurrentVerticalResolution"
        resolution = self.run_command(resolution_cmd)
        print("Разрешение экрана:")
        print(resolution)
        
        # Сохраняем в результаты
        self.results.update({
            'serial_number': serial,
            'model': model,
            'cpu': cpu,
            'ram': ram,
            'disk': disk,
            'gpu': gpu_clean,
            'screen_resolution': resolution
        })
        
        return self.ask_user_result("Сбор информации о железе", "Проверьте правильность отображенной информации")
    
    def test_hwinfo(self):
        """Тест HWiNFO64"""
        print("\n" + "="*30)
        print("HWINFO64 - ПОДРОБНАЯ ИНФОРМАЦИЯ")
        print("="*30)
        
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
        print("\n" + "="*30)
        print("ТЕСТ АУДИО/ДИНАМИКОВ")
        print("="*30)
        
        # Проверяем наличие тестового файла
        audio_files = ["speaker_test.mp4", "speaker_test.wav"]
        audio_file = None
        
        for file in audio_files:
            if os.path.exists(file):
                audio_file = file
                break
        
        if audio_file:
            print(f"Воспроизводим тестовый файл: {audio_file}")
            try:
                # Используем системный плеер
                if audio_file.endswith('.mp4'):
                    os.startfile(audio_file)
                else:
                    # Для wav файлов можем использовать PowerShell
                    cmd = f'powershell -c "(New-Object Media.SoundPlayer \\"{audio_file}\\").PlaySync();"'
                    subprocess.run(cmd, shell=True)
                
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
        print("\n" + "="*30)
        print("ТЕСТ КАМЕРЫ")
        print("="*30)
        
        camera_exe = "Camera.exe"
        if os.path.exists(camera_exe):
            print("Запускаем приложение камеры...")
            subprocess.Popen(camera_exe)
            input("Нажмите Enter после проверки камеры...")
            result = self.ask_user_result("Тест камеры", "Работает ли камера корректно?")
            self.results['camera_ok'] = result
            return result
        else:
            # Пробуем запустить встроенное приложение камеры Windows
            print("Запускаем встроенное приложение камеры Windows...")
            try:
                subprocess.Popen("start ms-camera:", shell=True)
                input("Нажмите Enter после проверки камеры...")
                result = self.ask_user_result("Тест камеры", "Работает ли камера корректно?")
                self.results['camera_ok'] = result
                return result
            except:
                result = self.ask_user_result("Тест камеры", "Не удалось запустить приложение камеры")
                self.results['camera_ok'] = result
                return result
    
    def test_ssd(self):
        """Тест SSD через CrystalDiskInfo"""
        print("\n" + "="*30)
        print("ТЕСТ SSD/HDD")
        print("="*30)
        
        crystal_path = "CrystalDiskInfo\\DiskInfo64.exe"
        if os.path.exists(crystal_path):
            print("Запускаем CrystalDiskInfo...")
            subprocess.Popen(crystal_path)
            input("Нажмите Enter после проверки состояния дисков...")
            
            # Удаляем логи Smart
            smart_dir = "CrystalDiskInfo\\Smart"
            if os.path.exists(smart_dir):
                try:
                    import shutil
                    shutil.rmtree(smart_dir)
                    print("Логи SMART удалены")
                    self.results['smart_logs_deleted'] = True
                except Exception as e:
                    print(f"Ошибка удаления логов: {e}")
                    self.results['smart_logs_deleted'] = False
            else:
                self.results['smart_logs_deleted'] = True
            
            result = self.ask_user_result("Тест SSD/HDD", "Проверьте состояние дисков (должно быть Good/Хорошо)")
            self.results['ssd_tool_ok'] = result
            return result
        else:
            print("CrystalDiskInfo не найден!")
            result = self.ask_user_result("Тест SSD/HDD", "CrystalDiskInfo не найден")
            self.results['ssd_tool_ok'] = result
            return result
    
    def test_battery(self):
        """Тест батареи"""
        print("\n" + "="*30)
        print("ТЕСТ БАТАРЕИ")
        print("="*30)
        
        # Сначала показываем информацию через PowerShell
        print("Получаем информацию о батарее...")
        battery_cmd = 'powershell "Get-WmiObject -Class Win32_Battery | Select-Object Name, BatteryStatus, EstimatedChargeRemaining"'
        battery_info = self.run_command(battery_cmd)
        print("Информация о батарее:")
        print(battery_info)
        
        # Запускаем внешнюю утилиту если есть
        battery_exe = "gBatteryInfoView.exe"
        if os.path.exists(battery_exe):
            print("Запускаем gBatteryInfoView...")
            subprocess.Popen(battery_exe)
            input("Нажмите Enter после проверки информации о батарее...")
        
        result = self.ask_user_result("Тест батареи", "Проверьте состояние и заряд батареи")
        self.results['battery_ok'] = result
        return result
    
    def test_screen(self):
        """Тест экрана"""
        print("\n" + "="*30)
        print("ТЕСТ ЭКРАНА")
        print("="*30)
        
        screen_exe = "IsMyLcdOK_x64.exe"
        if os.path.exists(screen_exe):
            print("Запускаем IsMyLcdOK...")
            subprocess.Popen(screen_exe)
            input("Нажмите Enter после проверки экрана...")
            result = self.ask_user_result("Тест экрана", "Проверьте экран на битые пиксели и артефакты")
            self.results['screen_ok'] = result
            return result
        else:
            print("IsMyLcdOK_x64.exe не найден!")
            result = self.ask_user_result("Тест экрана", "Проверьте экран визуально на битые пиксели")
            self.results['screen_ok'] = result
            return result
    
    def test_keyboard(self):
        """Тест клавиатуры"""
        print("\n" + "="*30)
        print("ТЕСТ КЛАВИАТУРЫ")
        print("="*30)
        
        keyboard_exe = "Keyboard.exe"
        if os.path.exists(keyboard_exe):
            print("Запускаем тест клавиатуры...")
            subprocess.Popen(keyboard_exe)
            input("Нажмите Enter после проверки всех клавиш...")
            result = self.ask_user_result("Тест клавиатуры", "Работают ли все клавиши корректно?")
            self.results['keyboard_ok'] = result
            return result
        else:
            print("Keyboard.exe не найден!")
            print("Откройте блокнот и проверьте клавиши вручную...")
            subprocess.Popen("notepad.exe")
            input("Нажмите Enter после проверки клавиатуры...")
            result = self.ask_user_result("Тест клавиатуры", "Работают ли все клавиши корректно?")
            self.results['keyboard_ok'] = result
            return result
    
    def test_microphone(self):
        """Тест микрофона"""
        print("\n" + "="*30)
        print("ТЕСТ МИКРОФОНА")
        print("="*30)
        
        # Открываем микшер звука
        print("Открываем микшер звука...")
        try:
            subprocess.Popen("sndvol.exe")
        except:
            pass
        
        # Пробуем открыть Sound через .lnk файл
        sound_lnk = "Sound.lnk"
        if os.path.exists(sound_lnk):
            try:
                os.startfile(sound_lnk)
            except:
                pass
        
        input("Говорите в микрофон и проверьте уровни в микшере. Нажмите Enter когда закончите...")
        result = self.ask_user_result("Тест микрофона", "Работает ли микрофон? Видны ли уровни звука?")
        self.results['microphone_ok'] = result
        return result
    
    def test_device_manager(self):
        """Проверка диспетчера устройств"""
        print("\n" + "="*30)
        print("ДИСПЕТЧЕР УСТРОЙСТВ")
        print("="*30)
        
        print("Открываем диспетчер устройств...")
        subprocess.Popen("devmgmt.msc", shell=True)
        input("Проверьте устройства в диспетчере. Нажмите Enter когда закончите...")
        result = self.ask_user_result("Диспетчер устройств", "Есть ли неизвестные устройства или ошибки?")
        self.results['devicemanager_ok'] = result
        return result
    
    def test_accounts(self):
        """Тест настроек учетных записей"""
        print("\n" + "="*30)
        print("НАСТРОЙКИ УЧЕТНЫХ ЗАПИСЕЙ")
        print("="*30)
        
        print("1 - Сбросить пароль")
        print("2 - Проверить сброс")
        choice = input("Выберите действие [1/2]: ").strip()
        
        if choice == '1':
            print("Сбрасываем настройки пароля...")
            cmd = 'powershell -Command "Start-Process -FilePath \'cmd\' -Verb RunAs -ArgumentList \'/c net accounts /maxpwage:unlimited && pause\'"'
            subprocess.run(cmd, shell=True)
            self.results['accounts_bat_called'] = True
        elif choice == '2':
            print("Проверяем настройки учетных записей...")
            subprocess.run("net accounts", shell=True)
            self.results['accounts_bat_called'] = True
        else:
            print("Пропускаем настройки учетных записей")
            self.results['accounts_bat_called'] = False
        
        input("Нажмите Enter для продолжения...")
        return self.results['accounts_bat_called']
    
    def test_touchscreen(self):
        """Тест тачскрина"""
        print("\n" + "="*30)
        print("ТЕСТ ТАЧСКРИНА")
        print("="*30)
        
        choice = input("Нужно ли проверить тачскрин? [1-нет, 2-да]: ").strip()
        
        if choice == '2':
            touchscreen_exe = "IsMyTouchScreenOK_x64.exe"
            if os.path.exists(touchscreen_exe):
                print("Запускаем тест тачскрина...")
                subprocess.Popen(touchscreen_exe)
                input("Нажмите Enter после проверки тачскрина...")
                result = self.ask_user_result("Тест тачскрина", "Работает ли тачскрин корректно?")
                self.results['touchscreen_ok'] = result
                return result
            else:
                print("IsMyTouchScreenOK_x64.exe не найден!")
                result = self.ask_user_result("Тест тачскрина", "Проверьте тачскрин вручную")
                self.results['touchscreen_ok'] = result
                return result
        else:
            self.results['touchscreen_ok'] = None
            return None
    
    def save_results(self):
        """Сохраняет результаты в CSV файл"""
        print("\n" + "="*30)
        print("СОХРАНЕНИЕ РЕЗУЛЬТАТОВ")
        print("="*30)
        
        # Добавляем timestamp
        self.results['timestamp'] = self.start_time.isoformat()
        
        # Собираем заметки
        notes = []
        for key, value in self.results.items():
            if isinstance(value, tuple) and len(value) == 2:
                # Это результат с заметкой об ошибке
                self.results[key] = value[0]  # Сохраняем только булево значение
                if value[1]:  # Если есть заметка
                    notes.append(f"{key}: {value[1]}")
        
        self.results['notes'] = "; ".join(notes) if notes else ""
        
        # Заполняем пропущенные поля
        csv_fields = [
            'timestamp', 'serial_number', 'model', 'cpu', 'ram', 'disk', 'gpu', 
            'screen_resolution', 'hwinfo_ran', 'audio_test_ok', 'camera_ok', 
            'ssd_tool_ok', 'smart_logs_deleted', 'battery_ok', 'screen_ok', 
            'keyboard_ok', 'microphone_ok', 'devicemanager_ok', 'accounts_bat_called', 
            'touchscreen_ok', 'notes'
        ]
        
        for field in csv_fields:
            if field not in self.results:
                self.results[field] = ""
        
        # Записываем в CSV
        try:
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                row = [self.results.get(field, "") for field in csv_fields]
                writer.writerow(row)
            print(f"Результаты сохранены в {self.csv_file}")
        except Exception as e:
            print(f"Ошибка сохранения результатов: {e}")
    
    def run_all_tests(self):
        """Запускает все тесты по порядку"""
        print("="*50)
        print("ЗАПУСК ТЕСТИРОВАНИЯ НОУТБУКА")
        print("="*50)
        
        try:
            # Последовательность тестов
            self.get_hardware_info()
            self.test_hwinfo()
            self.test_audio()
            self.test_camera()
            self.test_ssd()
            self.test_battery()
            self.test_screen()
            self.test_keyboard()
            self.test_microphone()
            self.test_device_manager()
            self.test_accounts()
            self.test_touchscreen()
            
            # Финальное напоминание
            print("\n" + "!"*60)
            print("НЕ ЗАБУДЬТЕ ПРОВЕРИТЬ КНОПКИ ТАЧПАДА И САМ ТАЧПАД!")
            print("!"*60)
            input("Нажмите Enter после проверки тачпада...")
            
            # Сохраняем результаты
            self.save_results()
            
            print("\n" + "="*50)
            print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
            print("="*50)
            
        except KeyboardInterrupt:
            print("\nТестирование прервано пользователем")
            self.save_results()
        except Exception as e:
            print(f"Ошибка во время тестирования: {e}")
            self.save_results()

def main():
    """Главная функция"""
    try:
        # Устанавливаем кодировку консоли
        os.system("chcp 65001 >nul")
        
        tester = LaptopTester()
        tester.run_all_tests()
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()
