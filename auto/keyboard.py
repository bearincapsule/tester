import os
import msvcrt

layout = [
    "ESC  F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 F11 F12",
    "`  1 2 3 4 5 6 7 8 9 0 - =  BACK",
    "TAB  Q W E R T Y U I O P [ ] \\",
    "CAPS A S D F G H J K L ; ' ENTER",
    "SHIFT Z X C V B N M , . / SHIFT",
    "CTRL WIN ALT     SPACE     ALT MENU CTRL",
    "INS DEL HOME END PGUP PGDN",
    "      ↑      ",
    "←     ↓     →",
    "NUM / * -",
    "7 8 9 +",
    "4 5 6",
    "1 2 3 ENTER",
    "0 ."
]

def clear():
    os.system('cls')

def render_layout(last_key=None, error=False):
    clear()
    print("Press keys to test them. Ctrl+C to exit.\n")
    for line in layout:
        if last_key and last_key.upper() in line.upper():
            hl = line.upper().replace(last_key.upper(), f"[{last_key.upper()}]")
            print(hl)
        else:
            print(line)
    if error:
        print("\n[ERROR] Unrecognized key pressed!")

try:
    while True:
        render_layout()
        key = msvcrt.getch()
        try:
            decoded = key.decode('utf-8').upper()
            render_layout(decoded)
        except UnicodeDecodeError:
            render_layout(last_key=None, error=True)
except KeyboardInterrupt:
    clear()
    print("Exiting tester.")