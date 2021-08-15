from datetime import datetime
from functools import lru_cache
from typing import Tuple
import cv2
import pyautogui
from screenshot import _LOCK, get_screenshot
import numpy
# from screenshot import get_screenshot


def img_match(img, template):
    # img = cv2.imread('messi5.jpg', 0)
    # img2 = img.copy()
    # img2 = img
    # template = cv2.imread('template.jpg', 0)
    _, w, h = template.shape[::-1]

    # All the 6 methods for comparison in a list
    methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
               'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
    meth = 'cv2.TM_CCOEFF_NORMED'

    # img = img2.copy()
    method = eval(meth)

    # Apply template Matching
    res = cv2.matchTemplate(img, template, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)


    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    return (*top_left, *bottom_right), max_val


def center(t, l, b, r) -> Tuple[int, int]:
    return ((t+b)//2, (l+r)//2)


@lru_cache(maxsize=512)
def _read_img(img_path):
    """读取模板图，并缓存，避免频繁IO"""
    return cv2.imread(img_path, 0)


def locate(img_path) -> Tuple[Tuple[int, int], float]:
    """定位目标图片中心"""
    templ = _read_img(img_path).copy()
    templ = cv2.cvtColor(templ, cv2.COLOR_BGR2RGB)

    _LOCK.acquire()
    screenshot = get_screenshot()
    screenshot = numpy.asarray(screenshot).copy()
    _LOCK.release()
    # screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
    res = img_match(screenshot, templ)
    # print(res[1])
    return center(*res[0]), res[1]


@lru_cache()
def locate_with_cache(img_path):
    """缓存找到的位置"""
    return locate(img_path)
