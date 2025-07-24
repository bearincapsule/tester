import platform
import psutil
import subprocess
import shutil
import csv
import cv2
from playsound import playsound
from pynput import mouse, keyboard

# ======================= CONFIG =======================
CSV_PATH = 'test_results.csv'

# ======================= FUNCTIONS =======================
def get_hardware_info():
    info = {}
    info['hostname'] = platform.node()
    info['cpu'] = platform.processor()
    info['ram_gb'] = round(psutil.virtual_memory().total / (1024 ** 3), 2)

    gpu = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'], capture_output=True, text=True)
    info['gpu'] = gpu.stdout.strip().split('\n')[1] if len(gpu.stdout.strip().split('\n')) > 1 else 'Unknown'

    return info

def ask_run_exe(path):
    choice = input(f"Run {path}? [1 - no (default), 2 - yes]: ")
    if choice.strip() == "2":
        subprocess.Popen(path)

def test_speaker():
    print("Testing speakers...")
    playsound('speaker_test.mp4')

def test_camera():
    print("Testing camera (press Q to quit)...")
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Camera Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def test_mouse_buttons():
    result = {"left": False, "right": False}
    def on_click(x, y, button, pressed):
        if pressed:
            if button.name == 'left':
                print("Left button pressed")
            elif button.name == 'right':
                print("Right button pressed")
            elif button.name == 'middle':
                result['left'] = True
                result['right'] = True
                return False
        if all(result.values()):
            return False
    print("Click left and right mouse buttons...")
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    return result

def test_keyboard():
    pressed_keys = set()
    def on_press(key):
        try:
            pressed_keys.add(key.char)
        except:
            pressed_keys.add(str(key))
        print(f"Key pressed: {key}")
        if len(pressed_keys) >= 5:
            return False
    print("Press at least 5 keys to continue...")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
    return list(pressed_keys)

def test_mic():
    input("Speak into the mic and check levels in sound mixer. Press Enter to continue...")

def run_external_tools():
    ask_run_exe(r"HWiNFO64\HWiNFO64.exe")
    test_speaker()
    test_camera()
    ask_run_exe(r"CrystalDiskInfo\DiskInfo64.exe")
    shutil.rmtree("CrystalDiskInfo/Smart", ignore_errors=True)
    ask_run_exe(r"gBatteryInfoView.exe")
    ask_run_exe(r"IsMyLcdOK_x64.exe")
    ask_run_exe(r"Keyboard.exe")
    test_mic()
    subprocess.Popen("sndvol")
    input("Check Device Manager, then press Enter...")
    subprocess.call("accounts.bat", shell=True)
    touchscreen = input("Check touchscreen? [1 - no (default), 2 - yes]: ")
    if touchscreen.strip() == "2":
        subprocess.Popen(r"IsMyTouchScreenOK_x64.exe")
    print("Check touchpad buttons manually!")
    input("Press Enter when done...")

def log_results(info, mouse_result, keys):
    with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            info['hostname'],
            info['cpu'],
            info['ram_gb'],
            info['gpu'],
            mouse_result['left'],
            mouse_result['right'],
            ",".join(keys)
        ])

# ======================= MAIN =======================
print("=== HARDWARE TESTER START ===")
hardware_info = get_hardware_info()
mouse_buttons = test_mouse_buttons()
keyboard_keys = test_keyboard()
run_external_tools()
log_results(hardware_info, mouse_buttons, keyboard_keys)
print("=== TEST COMPLETE ===")