
from typing import Tuple
from typing_extensions import Literal

import win32api
import win32gui
import pyautogui
from time import sleep
from win32api import GetAsyncKeyState
from util import locate
from screenshot import run_screenshot_thread, stop_screenshot_thread

STATE: Literal['SELECT_LEVEL', 'SELECT_ACT', 'PREPARE', 'PREPARE_ENOUGH',
               'PREPARE_NOT_ENOUGH', 'WAIT_SELECT_FRIEND', 'SELECTED_FRIEND', 'LOADING', 'PLAYING',
               'END1', 'END2', 'END2_NO_DLG', 'END2_HAS_DLG', 
               '没体力'] = 'SELECT_LEVEL'

ACT = 1


def state_change():
    global STATE, ACT

    if STATE == 'SELECT_LEVEL':
        STATE = 'SELECT_ACT'

    elif STATE == 'SELECT_ACT':
        if select_act(ACT):
            STATE = 'PREPARE'

    elif STATE == 'PREPARE':
        sleep(1)
        # if check_enough():
        if True:
            STATE = 'PREPARE_ENOUGH'
        else:
            STATE = 'PREPARE_NOT_ENOUGH'

    elif STATE == 'PREPARE_ENOUGH':
        sleep(.2)
        if click_prepare():
            STATE = 'WAIT_SELECT_FRIEND'

    elif STATE == 'PREPARE_NOT_ENOUGH':
        sleep(.2)
        ACT += 1
        if click_back():
            STATE = 'SELECT_ACT'

    elif STATE == 'WAIT_SELECT_FRIEND':
        sleep(.2)
        if select_helper():
            STATE = 'SELECTED_FRIEND'

    elif STATE == 'SELECTED_FRIEND':
        sleep(.2)
        if click_battle():
            sleep(4)
            if check_not_enough_tili():
                close_dlg()
                STATE = '没体力'
            elif close_dlg():
                STATE = 'PREPARE_NOT_ENOUGH'
            else:
                STATE = 'LOADING'

    elif STATE == 'LOADING':
        sleep(1)
        if attack():
            STATE = 'PLAYING'

    elif STATE.startswith('PLAYING'):
        if not attack():
            STATE = STATE+str(1)
            if STATE.count('1') > 5:
                STATE = 'END1'
        else:
            STATE = 'PLAYING'

    elif STATE == 'END1':
        sleep(5)
        click_window_center()
        STATE = 'END2_HAS_DLG'

    elif STATE == 'END2_HAS_DLG':
        sleep(6)
        if close_dlg():
            sleep(.1)
            click_confirm()
            STATE = 'SELECT_LEVEL'
    
    elif STATE == '没体力':
        raise Exception()


def select_act(actnum: int):
    assert 1 <= actnum <= 5
    coords, confi = locate(f"./act{actnum}.png")
    if confi < 0.6:
        return False
    print(f'选择ACT{actnum}', coords)
    x, y = coords
    pyautogui.click(x, y)
    return True


def click_prepare():
    coords, confi = locate(f"./prepare.png")
    if confi < 0.84:
        return False
    print(f'战斗准备', coords)
    x, y = coords
    pyautogui.click(x, y)
    return True


def check_enough():
    """剩余次数够不够"""
    coords, confi = locate(f"./not_enough.png")
    print(coords)
    if confi < 0.725:
        return True
    return False


def select_helper():
    coords, confi = locate(f"./friend.png")
    if confi < 0.7:
        return False
    print(f'选择路人', coords)
    x, y = coords
    pyautogui.click(x, y)
    return True


def click_battle():
    coords, confi = locate(f"./batt.png")
    if confi < 0.79:
        return False
    print(f'开战', coords)
    x, y = coords
    pyautogui.click(x, y)
    return True


def attack():
    coords, confi = locate(r"./a.png")
    if confi < 0.5:
        return False
    print('平A', coords)
    x, y = coords
    pyautogui.click(x, y)

    while 1:
        coords, confi = locate(r"./q.png")
        if confi < 0.7:
            break
        print('开大', coords)
        x, y = coords
        pyautogui.click(x, y)
        break

    return True


def close_dlg():
    coords, confi = locate(f"./close.png")
    if confi < 0.8:
        return False
    print(f'关闭对话框', coords)
    x, y = coords
    pyautogui.click(x, y)
    return True


def click_confirm():
    coords, confi = locate(f"./confirm.png")
    if confi < 0.84:
        return False
    print(f'确认', coords)
    x, y = coords
    pyautogui.click(x, y)
    return True


def click_back():
    coords, confi = locate(f"./back.png")
    if confi < 0.84:
        return False
    print(f'返回', coords)
    x, y = coords
    pyautogui.click(x, y)
    return True


def click_window_center():
    hwnd = win32gui.FindWindow(None, '崩坏3')
    l, t, r, b = win32gui.GetWindowRect(hwnd)
    x = (l+r)//2
    y = (t+b)//2
    pyautogui.click(x, y)


def check_not_enough_tili():
    coords, confi = locate(f"./tilidlg.png")
    if confi < 0.84:
        return False
    print(f'没体力了', coords)
    x, y = coords
    pyautogui.click(x, y)
    return True



def main():
    while True:
        if GetAsyncKeyState(112) != 0:
            return
        state_change()
        print(STATE)
        if STATE == 'PLAYING':
            continue
        sleep(.1)


if __name__ == "__main__":
    run_screenshot_thread()
    main()
    stop_screenshot_thread()
