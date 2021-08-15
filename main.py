
from typing import Tuple
from typing_extensions import Literal

import win32api
import win32gui
import pyautogui
from time import sleep
from win32api import GetAsyncKeyState
from util import locate_with_cache
from screenshot import run_screenshot_thread, stop_screenshot_thread

from state import get_act, start_state_change, get_state
ACT = 1


def click(x: int, y: int):
    hwnd = win32gui.FindWindow(None, '崩坏3')
    l, t, _, _ = win32gui.GetWindowRect(hwnd)
    pyautogui.click(l+x, t+y)


def handle_state(STATE):
    global ACT

    if STATE == 'SELECT_LEVEL':
        pass

    elif STATE == 'SELECT_ACT':
        print(get_act())
        select_act(get_act())

    elif STATE == 'PREPARE':
        pass

    elif STATE == 'PREPARE_ENOUGH':
        click_prepare()
        pyautogui.moveTo(50, 50)
        sleep(1)
        pass

    elif STATE == 'PREPARE_NOT_ENOUGH':
        # ACT += 1
        click_back()
        sleep(1)

    elif STATE == 'WAIT_SELECT_FRIEND':
        select_helper()
        pass

    elif STATE == 'SELECTED_FRIEND':
        click_battle()
        pyautogui.moveTo(50, 50)
        sleep(1)

    elif STATE == 'LOADING':
        pass

    elif STATE == 'PLAYING':
        attack()

    elif STATE == 'PLAYING_HASQ':
        q()

    elif STATE == 'END1':
        pass

    elif STATE == 'END1END':
        click_window_center()

    elif STATE == 'END2_HAS_DLG':
        close_dlg()

    elif STATE == 'END2_NO_DLG':
        click_confirm()
        sleep(2)

    elif STATE == '没体力':
        raise Exception()


def select_act(actnum: int):
    assert 1 <= actnum <= 5
    coords, confi = locate_with_cache(f"./act{actnum}.png")
    if confi < 0.6:
        return False
    print(f'选择ACT{actnum}', coords)
    x, y = coords
    click(x, y)
    return True


def click_prepare():
    coords, confi = locate_with_cache(f"./prepare.png")
    if confi < 0.84:
        return False
    print(f'战斗准备', coords)
    x, y = coords
    click(x, y)
    return True


def check_enough():
    """剩余次数够不够"""
    coords, confi = locate_with_cache(f"./not_enough.png")
    print(coords)
    if confi < 0.725:
        return True
    return False


def select_helper():
    coords, confi = locate_with_cache(f"./friend0.png")
    if confi < 0.7:
        return False
    print(f'选择路人', coords)
    x, y = coords
    click(x, y)
    return True


def click_battle():
    coords, confi = locate_with_cache(f"./batt.png")
    print(confi)
    if confi < 0.7:
        return False
    print(f'开战', coords)
    x, y = coords
    click(x, y)
    return True


def attack():
    coords, confi = locate_with_cache(r"./a.png")
    if confi < 0.3:
        return False
    print('平A', coords)
    x, y = coords
    click(x, y)

def q():
    coords, confi = locate_with_cache(r"./q.png")
    if confi < 0.7:
        return False
    print('开大', coords)
    x, y = coords
    click(x, y)
    return True


def close_dlg():
    coords, confi = locate_with_cache(f"./close.png")
    if confi < 0.8:
        return False
    print(f'关闭对话框', coords)
    x, y = coords
    click(x, y)
    return True


def click_confirm():
    coords, confi = locate_with_cache(f"./confirm.png")
    if confi < 0.84:
        return False
    print(f'确认', coords)
    x, y = coords
    click(x, y)
    return True


def click_back():
    coords, confi = locate_with_cache(f"./back.png")
    if confi < 0.84:
        return False
    print(f'返回', coords)
    x, y = coords
    click(x, y)
    return True


def click_window_center():
    hwnd = win32gui.FindWindow(None, '崩坏3')
    l, t, r, b = win32gui.GetWindowRect(hwnd)
    x = (l+r)//2
    y = (t+b)//2
    click(x, y)


def check_not_enough_tili():
    coords, confi = locate_with_cache(f"./tilidlg.png")
    if confi < 0.84:
        return False
    print(f'没体力了', coords)
    x, y = coords
    click(x, y)
    return True


def main():
    while True:
        if GetAsyncKeyState(112) != 0:
            return
        state = get_state()
        print(state)
        handle_state(state)


        if state == 'PLAYING':
            continue
        sleep(.8)


if __name__ == "__main__":
    run_screenshot_thread()
    start_state_change()
    main()
