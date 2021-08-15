
from datetime import datetime
from threading import Thread
from typing import Any, Callable, Tuple
from typing_extensions import Literal

import win32api
import win32gui
import pyautogui
from time import sleep
from win32api import GetAsyncKeyState
from util import locate
from multiprocessing.dummy import Pool


STATE: Literal['SELECT_LEVEL', 'SELECT_ACT',
               'PREPARE', 'PREPARE_ENOUGH', 'PREPARE_NOT_ENOUGH',
               'WAIT_SELECT_FRIEND', 'SELECTED_FRIEND', 'LOADING',
               'PLAYING', 'PLAYING_HASQ', 'PLAYING_RETRY',
               'END1', 'END1END', 'END1LOADING', 'END2', 'END2_NO_DLG', 'END2_HAS_DLG',
               '没体力'] = 'SELECT_LEVEL'

ACT = 1

_THREAD_POOL = None


def get_state():
    return STATE

def get_act():
    return ACT


def state_change():
    global STATE, ACT, _THREAD_POOL

    if STATE == 'SELECT_LEVEL':
        if is_select_act():
            STATE = 'SELECT_ACT'

    elif STATE == 'SELECT_ACT':
        if is_prepare():
            STATE = 'PREPARE'
        # elif is_select_act():
        #     pass

    elif STATE == 'PREPARE':
        # sleep(1)
        # if check_enough():
        if True:
            STATE = 'PREPARE_ENOUGH'
        else:
            STATE = 'PREPARE_NOT_ENOUGH'

    elif STATE == 'PREPARE_ENOUGH':
        # sleep(.2)
        if is_battle():
            STATE = 'WAIT_SELECT_FRIEND'

    elif STATE == 'PREPARE_NOT_ENOUGH':
        # sleep(.2)
        if is_select_act():
            ACT += 1
            STATE = 'SELECT_ACT'

    elif STATE == 'WAIT_SELECT_FRIEND':
        # sleep(.2)
        if is_friend_select():
            STATE = 'SELECTED_FRIEND'

    elif STATE == 'SELECTED_FRIEND':
        # if is_loading():
        #     STATE = 'LOADING'
        # elif is_not_enough_limit():   # 次数不够
        #     STATE = 'PREPARE_NOT_ENOUGH'
        # elif check_not_enough_tili():   # 体力不够
        #     STATE = '没体力'

        # 并行版
        def run_job(func: Callable[[], bool]) -> bool:
            return func()
        res = _THREAD_POOL.map(run_job,
                               [is_loading, is_not_enough_limit, check_not_enough_tili])
        is_loading_res, is_not_enough_limit_res, check_not_enough_tili_res = res
        if is_loading_res:
            STATE = 'LOADING'
        elif is_not_enough_limit_res:   # 次数不够
            STATE = 'PREPARE_NOT_ENOUGH'
        elif check_not_enough_tili_res:   # 体力不够
            STATE = '没体力'

    elif STATE == 'LOADING':
        # sleep(1)
        if not is_loading():
            STATE = 'PLAYING'

    elif STATE == 'PLAYING':
        if not has_atk_btn():
            STATE = 'PLAYING_RETRY'
        elif has_q_btn():
            STATE = 'PLAYING_HASQ'
        else:
            STATE = 'PLAYING'

    elif STATE == 'PLAYING_HASQ':
        if not has_q_btn():
            STATE = 'PLAYING'

    elif STATE.startswith('PLAYING_RETRY'):
        if not has_atk_btn():
            STATE = STATE+str(1)
            if STATE.count('1') > 10:
                STATE = 'END1'
        else:
            STATE = 'PLAYING'

    elif STATE == 'END1':
        sleep(5)
        if is_end1_end():
            STATE = 'END1END'
        else:
            STATE = 'PLAYING'

    elif STATE == 'END1END':
        sleep(1)
        if not is_end1_end():
            STATE = 'END2'

    # elif STATE == 'END1LOADING':
    #     if not is_loading():
    #         if is_end1_end():   # 失败回退
    #             STATE = 'END1'
    #         else:
    #             STATE = 'END2'

    elif STATE == 'END2':
        sleep(6)
        if has_dlg():
            STATE = 'END2_HAS_DLG'
        else:
            STATE = 'END2_NO_DLG'

    elif STATE == 'END2_HAS_DLG':
        if not has_dlg():
            STATE = 'END2_NO_DLG'

    elif STATE == 'END2_NO_DLG':
        if not has_confirm():
            if is_select_act():
                STATE = 'SELECT_LEVEL'
            elif has_dlg:
                STATE = 'END2_HAS_DLG'

    elif STATE == '没体力':
        input('没体力了')


def is_select_act():
    coords, confi = locate(f"./acts.png")
    if confi < 0.5:
        return False
    else:
        return True


def is_prepare():
    coords, confi = locate(f"./prepare.png")
    if confi < 0.84:
        return False
    return True


def check_enough():
    """剩余次数够不够"""
    coords, confi = locate(f"./not_enough.png")
    # print(coords)
    if confi < 0.725:
        return True
    return False


def is_friend_select():
    """选了助战好友没有"""
    # 并行check三种情况，串行耗时巨久
    def func(i):
        r = False if locate(f"./friend{i}.png")[1] < 0.5 else True
        return r
    ret = _THREAD_POOL.map(func, [1, 2, 3])
    return any(ret)

    # for i in range(1, 4):
    #     r = False if locate(f"./friend{i}.png")[1] < 0.7 else True
    #     if r:
    #         return True
    # return False


def is_battle():
    """是不是准备出战"""
    coords, confi = locate(f"./cam.png")
    if confi < 0.6:
        return False
    return True


def is_loading():
    """是否加载中"""
    coords, confi = locate(f"./loading.png")
    # print(confi)
    if confi < 0.8:
        return False
    return True


def has_atk_btn():
    coords, confi = locate(r"./a.png")
    if confi < 0.5:
        return False
    return True


def has_q_btn():
    coords, confi = locate(r"./q.png")
    if confi < 0.7:
        return False
    return True


def has_dlg():
    coords, confi = locate(f"./close.png")
    # print(confi)
    if confi < 0.8:
        return False
    return True


def has_confirm():
    coords, confi = locate(f"./confirm.png")
    # print(confi)
    if confi < 0.7:
        return False
    return True


def check_not_enough_tili():
    """有没有弹出体力不足的对话框"""
    coords, confi = locate(f"./tilidlg.png")
    if confi < 0.5:
        return False
    return True


def is_not_enough_limit():
    """挑战次数够不够"""
    coords, confi = locate(f"./limit.png")
    if confi < 0.84:
        return False
    return True


def is_end1_end():
    coords, confi = locate(f"./end1.png")
    print(confi)
    if confi < 0.7:
        return False
    return True


def start_state_change():
    global _THREAD_POOL
    _THREAD_POOL = Pool(5)

    def run():
        while True:
            # sleep(.01)
            s = datetime.now()
            state_change()
            d = datetime.now()-s
            # print(STATE, d.microseconds//1000)
    t = Thread(target=run)
    t.setDaemon(True)
    t.start()
