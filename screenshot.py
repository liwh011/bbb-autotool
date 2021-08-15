from time import sleep

import win32gui
from pyautogui import screenshot
from threading import Thread, Lock


# 双缓冲，一个用来写，一个用来读
_SCREENSHOT0 = None
_SCREENSHOT1 = None
_CUR_AVALIABLE_NUM = 0

_THREAD = None
_STOP = False
_LOCK = Lock()


def get_screenshot():
    if _CUR_AVALIABLE_NUM == 0:
        return _SCREENSHOT0
    if _CUR_AVALIABLE_NUM == 1:
        return _SCREENSHOT1
    return None


def _update_screenshot():
    global _SCREENSHOT0, _SCREENSHOT1, _LOCK, _CUR_AVALIABLE_NUM
    hwnd = win32gui.FindWindow(None, '崩坏3')
    rect = win32gui.GetWindowRect(hwnd)

    # 写入另一个
    if _CUR_AVALIABLE_NUM==0:
        _SCREENSHOT1 = screenshot(region=rect) 
    else:
        _SCREENSHOT0 = screenshot(region=rect) 
        
    # 上锁，切换
    _LOCK.acquire()
    _CUR_AVALIABLE_NUM = int(not _CUR_AVALIABLE_NUM)
    _LOCK.release()


def run_screenshot_thread():
    global _STOP, _THREAD

    # 先获取一下截图
    _update_screenshot()

    def func():
        while not _STOP:
            _update_screenshot()
            sleep(.5)

    _THREAD = Thread(target=func)
    _THREAD.setDaemon(True)
    _THREAD.start()


def stop_screenshot_thread():
    global _STOP
    _STOP = True
