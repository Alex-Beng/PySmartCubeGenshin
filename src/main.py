from aes import AES
from gancube import GanCube
from utils import devices_selection, get_quaternion, quat2rotm, quat2ypr, quat2gravity

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from bleak import BleakScanner, BleakClient, BleakGATTCharacteristic
from pynput.keyboard import Key, Controller
from pynput.mouse import Button, Controller as MController
import pydirectinput # for mouse
pydirectinput.PAUSE = 0

from ctypes import windll, c_uint
from math import atan2, asin, atan, sqrt, pi
import asyncio
from itertools import product, combinations

# 重定向stdout到文件 or 直接输出到out_file
import sys
# sys.stdout = open('../data/stable_long3_gyro', 'w')
out_file = open('../data/freerot.bin', 'w')

def move_mouse(x, y):
    pydirectinput.move(x, y, relative=True)

# Mouse and Keyboard
mouse = MController()
keyboard = Controller()

# cube
cube = None

# asyncio queues
qm_plot_queue = asyncio.Queue()
q_mouse_queue = asyncio.Queue()
move_queue = asyncio.Queue()
gyro_en_queue = asyncio.Queue()

async def keyboard_handler():
    fb_state = 0
    lr_state = 0
    while True:
        moves = await move_queue.get()
        if moves[0] == "L'":
            if fb_state == 1:
                pass
            elif fb_state == 0:
                keyboard.press('w')
                fb_state = 1
            elif fb_state == -1:
                keyboard.release('s')
                fb_state = 0
        elif moves[0] == "L ":
            if fb_state == 1:
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
            keyboard.press('f')
            keyboard.release('f')

async def mouse_handler():
    # pitch and roll zero calibration for 50 times
    print("Calibrating...")
    p_sum = 0.0
    r_sum = 0.0
    for i in range(50):
        q = await q_mouse_queue.get()
        # print(q)
        ypr = quat2ypr(q)
        p_sum += ypr[1]
        r_sum += ypr[2]
        await asyncio.sleep(0.001)
    p_zero = p_sum / 50
    r_zero = r_sum / 50
    print(f"Calibration finished. p_zero: {p_zero}, r_zero: {r_zero}")

    while True:
        q = await q_mouse_queue.get()
        ypr = quat2ypr(q)
        # map pitch and roll to mouse horizontal and vertical
        d_p = ypr[1] - p_zero
        d_r = ypr[2] - r_zero
        def scalex(x):
            x = int(0.4*x)
            return x if abs(x) > 2 else 0
        # mouse.move(-scalex(d_p), -scalex(d_r))
        move_mouse(-scalex(d_p), -scalex(d_r))

        await asyncio.sleep(0.001)

async def plt_plot():
    # viz
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.set_aspect("auto")
    ax.set_autoscale_on(True)
    # draw cuboid
    r = [-10, 10]
    for s, e in combinations(np.array(list(product(r,r,r))), 2):
        if np.sum(np.abs(s-e)) == r[1]-r[0]:
            ax.plot3D(*zip(s,e), color="black")
    # draw coors
    coor_len = 10
    coor_color = ['r', 'g', 'b']
    for i in range(3):
        s = [0]*3
        e = [0]*3
        s[i] = coor_len
        ax.plot3D(*zip(s,e), color=coor_color[i])
    # draw point
    ax.scatter([0],[0],[0],color="black",s=100)
    d = [-4, 4]
    vertex = []
    rad = 0
    colors = ['r', 'g', 'b', 'y', 'c', 'm']
    cnt = 0
    # for s, e in combinations(np.array(list(product(d,d,d))), 2):
    #     if np.sum(np.abs(s-e)) == d[1]-d[0]: 
    #         # init vertex
    #         v = ax.plot3D(*zip(s, e), color=colors[cnt%len(colors)])
    #         cnt += 1
    #         vertex.append(v + [s, e])
    # draw line
    for i in range(3):
        s = [0]*3
        e = [0]*3
        e[i] = - coor_len // 2
        # v = ax.plot3D(*zip(s, e), color=coor_color[i])
        # vertex.append(v + [s, e])
    # draw gravity
    s = [0]*3 
    e = [0]*3
    v = ax.plot3D(*zip(s, e), color='pink')
    vertex.append(v + [s, e])

    while True:
        q, rotm = await qm_plot_queue.get()

        for v, s, e in vertex[:-1]:
            # apply rotation matrix to each vertex
            s_rotated = np.dot(rotm, s)
            e_rotated = np.dot(rotm, e)
            v.set_data_3d(*zip(s_rotated,e_rotated))
        # update gravity
        v, s, e = vertex[-1]
        e[0] = 2 * (q[1]*q[3] - q[0]*q[2])
        e[1] = 2 * (q[0]*q[1] + q[2]*q[3])
        e[2] = q[0]**2 - q[1]**2 - q[2]**2 + q[3]**2

        # compute ypr
        ypr = [0]*3
        ypr[0] = atan2(2*q[1]*q[2] - 2*q[0]*q[3], 2*q[0]*q[0] + 2*q[1]*q[1] - 1)
        ypr[1] = atan(e[0] / sqrt(e[1]*e[1] + e[2]*e[2]))
        ypr[2] = atan(e[1] / sqrt(e[0]*e[0] + e[2]*e[2]))
        ypr = [i*180/pi for i in ypr]
        # print(f'ypr: {ypr}')
        # print(f'grav: {e}')

        e = [-i*10 for i in e]
        v.set_data_3d(*zip(s,e))
        plt.draw()
        plt.pause(0.001)
        await asyncio.sleep(0.001)

async def gan_read_handler(sender: BleakGATTCharacteristic, data: bytearray):
    global cube
    data = [int(i) for i in data]
    
    dec = cube.decrypt(data)
    
    value = ''.join([bin(bt+256)[3:] for bt in dec])

    # get the mode
    mode = int(value[0:4], 2)

    if dec[0] == 208:
        exit()
    
    print(''.join([bin(d+256)[3:] for d in dec]), end="\n", file=out_file)
    if mode == 1:
        # get quat and rotm
        qs = get_quaternion(dec)
        rotms = [quat2rotm(q) for q in qs]
        for q in qs:
            await q_mouse_queue.put(q)
        for qr in zip(qs, rotms):
            await qm_plot_queue.put(qr)
    elif mode == 2:
        move_cnt = int(value[4:12], 2)
        timeoffs = []
        prev_moves = []
        for i in range(7):
            m = int(value[12 + i*5 : 17 + i*5], 2)
            timeoffs.append( int(value[47 + i*16 : 63 + i*16], 2) )
            pre_move = "URFDLB"[m>>1] + " '"[m&1]
            prev_moves.append( pre_move )
            if m >= 12:
                # WRONG
                print(f'WARNING wrong move: {m}')
                pass
        await move_queue.put(prev_moves)
        print(f'move_cnt: {move_cnt}, {timeoffs}, {prev_moves}')
    elif mode == 4:
        print("reveived faces info")
    elif mode == 5:
        hw_ver = f'{int(value[8:16], 2)}.{int(value[16:24], 2)}'
        sw_ver = f'{int(value[24:32], 2)}.{int(value[32:40], 2)}'
        dev_name = ''.join([chr(int(value[40 + i*8 : 48 + i*8], 2)) for i in range(8)])
        gyro_enable = int(value[104], 2) == 1
        await gyro_en_queue.put(gyro_enable)
        print(f'hw_ver: {hw_ver}, sw_ver: {sw_ver}, dev_name: {dev_name}, gyro_enable: {gyro_enable}')
    elif mode == 9:
        battery = int(value[8:16], 2)
        print(f'battery: {battery}%')
    elif mode == 13:
        print("reveived good bye")
    else:
        print(f"get wrong mode: {mode}")


async def main():
    global cube

    # Search BLE CUBEs
    print("Searching for CUBEs...")
    devices = await BleakScanner.discover()

    possible_devices = []
    for d in devices:
        # ONLY GAN CUBE NOW
        if d.name and d.name.startswith("GAN"):
            possible_devices.append(d)

    selected_device = devices_selection(possible_devices)
    
    if selected_device.name.startswith("GAN"):
        cube = GanCube(selected_device.address)
        cube.name = selected_device.name
        cube.address = selected_device.address
    
    print(f"Connecting to {cube.name}, {cube.address}")
    async with BleakClient(cube.address) as client:
        
        cube_service = None
        for service in client.services:
            if service.uuid == cube.SERVICE_UUID:
                cube_service = service
                break
        
        if cube_service is None:
            print(f"Unable to find {cube.BRAND} CUBE service or unsppported {cube.BRAND} CUBEs")
            return
        
        read_chrct = None
        write_chrct = None
        for chrct in cube_service.characteristics:
            if chrct.uuid == cube.CHRCT_UUID_READ:
                read_chrct = chrct
            elif chrct.uuid == cube.CHRCT_UUID_WRITE:
                write_chrct = chrct
        
        if read_chrct is None or write_chrct is None:
            print(f"Unable to find {cube.BRAND} CUBE read or write characteristic")
            return
        print(f"Connected to {cube.BRAND} CUBE")

        await client.start_notify(read_chrct, gan_read_handler)

        # task for asking battery
        async def ask_battery():
            bts = [0]*20
            bts[0] = 9
            bts = cube.encrypt(bts)
            while True:
                await client.write_gatt_char(write_chrct, bytes(bts))
                await asyncio.sleep(30)
        # ask for hardware info
        bts = [0]*20
        bts[0] = 5
        await client.write_gatt_char(write_chrct, bytes(cube.encrypt(bts)))
        asyncio.create_task(ask_battery())
        # asyncio.create_task(plt_plot())
        asyncio.create_task(keyboard_handler())

        gyro_en = await gyro_en_queue.get()
        # only support gyro to mouse map
        if gyro_en:
            print("gyro air mouse enable")
            # 需要
            asyncio.create_task(mouse_handler())

        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
    out_file.close()
    exit()

