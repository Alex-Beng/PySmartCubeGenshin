from pynput.keyboard import Key, Controller
from pynput.mouse import Button, Controller as MController

import time

PAUSE = 0.01

def click_key(keyboard, key):
    keyboard.press(key)
    time.sleep(PAUSE)
    keyboard.release(key)

fb_state = 0
lr_state = 0
B_state = 0
Rr_state = 0
def move_handler(moves, keyboard, mouse):
    global fb_state, lr_state, B_state, Rr_state

    if moves[0] == "L'":
        if fb_state == 2:
            pass
        elif fb_state == 1:
            keyboard.press(Key.shift)
            fb_state = 2
        elif fb_state == 0:
            keyboard.press('w')
            fb_state = 1
        elif fb_state == -1:
            keyboard.release('s')
            fb_state = 0
    elif moves[0] == "L ":
        if fb_state == 2:
            keyboard.release(Key.shift)
            fb_state = 1
        elif fb_state == 1:
            keyboard.release('w')
            fb_state = 0
        elif fb_state == 0:
            keyboard.press('s')
            fb_state = -1
        elif fb_state == -1:
            pass
    elif moves[0] == "U'":
        if lr_state == -1:
            pass
        elif lr_state == 0:
            keyboard.press('a')
            lr_state = -1
        elif lr_state == 1:
            keyboard.release('d')
            lr_state = 0
    elif moves[0] == "U ":
        
        if lr_state == -1:
            keyboard.release('a')
            lr_state = 0
        elif lr_state == 0:
            keyboard.press('d')
            lr_state = 1
        elif lr_state == 1:
            pass
    elif moves[0] == "F ":
        if B_state == 1:
            click_key(keyboard, '2')
            B_state = 0
            return
        click_key(keyboard, 'f')
    elif moves[0] == "F'":
        if B_state == 1:
            click_key(keyboard, '3')
            B_state = 0
            return
        click_key(keyboard, Key.space)
    elif moves[0] == "D ":
        click_key(keyboard, Key.shift)
    elif moves[0] == "D'":
        click_key(keyboard, 'x')
    elif moves[0] == "R ":

        if B_state == 1:
            click_key(keyboard, '4')
            B_state = 0
            return
        if Rr_state == 1:
            click_key(keyboard, 'e')
            Rr_state = 0
            return
        mouse.click(Button.left, 1)
    elif moves[0] == "R'":
        if Rr_state == 1:
            keyboard.press('e')
            time.sleep(1)
            keyboard.release('e')
            Rr_state = 0
        elif Rr_state == 0:
            Rr_state = 1

    elif moves[0] == "B'":
        if B_state == 1:
            # !!! EXIT HERE !!!
            exit()
        click_key(keyboard, 'q')
    elif moves[0] == "B ":
        if B_state == 1:
            click_key(keyboard, '1')
            B_state = 0
            return
        elif B_state == 0:
            B_state = 1
    
    