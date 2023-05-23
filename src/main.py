from aes import AES

import math
import asyncio
from bleak import BleakScanner, BleakClient
from pynput.keyboard import Key, Controller
from pynput.mouse import Button, Controller as MController

# FOR GAN i 3
SERVICE_UUID        = '6e400001-b5a3-f393-e0a9-e50e24dc4179'
CHRCT_UUID_READ     = '28be4cb6-cd67-11e9-a32f-2a2ae2dbcce4'
CHRCT_UUID_WRITE    = '28be4a4a-cd67-11e9-a32f-2a2ae2dbcce4'

DECODER = None

def init_kiv(mac):
    '''
    Initialize the key and iv for the GAN CUBE AES-128 encryption
    '''
    key = [1,2,66,40,49,145,22,7,32,5,24,84,66,17,18,83]
    iv = [17,3,50,40,33,1,118,39,32,149,120,20,50,18,2,67]

    mac = list(map(int, mac.split(':'), [16]*6))
    for i in range(6):
        key[i] = (key[i] + mac[5-i]) % 255
        iv[i] = (iv[i] + mac[5-i]) % 255
    
    return key, iv

def encrypt(data):
    assert(len(data) == 20)

    iv = DECODER.iv
    enc = DECODER.encrypt([data[i] ^ iv[i] for i in range(16)]) + [0]*4
    enc = enc[:4] + DECODER.encrypt([enc[i+4] ^ iv[i] for i in range(16)])
    return enc

def decrypt(enc):
    assert(len(enc) == 20)

    iv = DECODER.iv
    _block = DECODER.decrypt(enc[4:])
    dec = [_block[i] ^ iv[i]  for i in range(16)]
    _block = DECODER.decrypt(enc[:4] + dec[:12]) 
    dec = [_block[i] ^ iv[i] for i in range(16)] + dec[12:]
    
    return dec


# 将所有输出重定向到文件
import sys
# sys.stdout = open('../data/stable_long3_gyro', 'w')
out_file = open('./flip_out.txt', 'w')

# 记录采样频率
# 约50ms
import time
first_time = True
prev_time = None

# Mouse and Keyboard
mouse = MController()
keyboard = Controller()

# convert 2's complement binary string to int
def twos_comp (val, bits):
    # convert binary string to int
    val = int (val, 2)
    # if sign bit is set, subtract 2^bits
    if val & (1 << (bits - 1)):
        val -= 1 << bits
    return val


fb_state = 0
lr_state = 0
def do_mskb(moves: [str]):
    global lr_state, fb_state
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
    



def read_handler(sender, data):
    global first_time, prev_time
    data = [int(i) for i in data]
    
    dec = decrypt(data)
    
    value = ''.join([bin(bt+256)[3:] for bt in dec])

    # get the mode
    mode = int(value[0:4], 2)

    if dec[0] == 208:
        exit()
    
    # print(' '.join([hex(d+256)[3:] for d in dec]), end="\n", file=out_file)
    if mode == 1:

        if first_time:
            first_time = False
            prev_time = time.time()

        # may be first 3 x 16bit(signed 16) is the quaternion?
        # from https://github.com/AshleyF/briefcubing/issues/4
        # lets see
        # may not

        # print("%.3f %.3f %.3f" % (x, y, z))
        # 只保留三位小数输出datas为一行
        # print('\r'+' '.join([f'{d/2**16:.3f}' for d in datas]), end='')
        # print(dec)
        # 输出 hex data
        know_bits_num = []
        know_bits = []
        for i in range(4):
            # 原码传递有符号数
            sign = -1 if int(value[4+i*16]) == 1 else 1
            v = int(value[5+i*16 : 20+i*16], 2)
            v *= sign
            know_bits_num.append(v)

            # know_bits_num.append( int(value[4+i*16 : 20+i*16], 2) )
            know_bits.append( hex(int(value[4+i*16 : 20+i*16], 2) + 65536)[3:] )
        know_bits2_num = []
        know_bits2 = []
        for i in range(4):
            know_bits2_num.append( int(value[80+i*16 : 96+i*16], 2) )
            know_bits2.append( hex(int(value[80+i*16 : 96+i*16], 2) + 65536)[3:] )
        
        
        # 验证四元数，模等于1
        nums_to1 = [know_bits_num[i] / 32767 for i in range(4)]
        print(nums_to1, sum([i*i for i in nums_to1]))

        

        
        # print(' '.join(know_bits), end=" ")
        # print(hex(int(value[68:80], 2) + 2**12)[3:])

        # print(' '.join(know_bits2), end=" ")
        # print(hex(int(value[144:156], 2) + 2**12)[3:])
        
        # diffs = [know_bits2_num[i] - know_bits_num[i] for i in range(4)]
        # print(' '.join([str(d) for d in diffs]))
        
        # print(' '.join([hex(d+256)[3:] for d in dec]), end="\n")        
        # print()
        # print('\r' + ' '.join([hex(d+256)[3:] for d in dec]), end="")
        prev_time = time.time()
        pass
    
    # 采数据呢
    # return
    
    if mode == 1:
        pass
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
                pass
                # print(f'le: {m}')
            # print(f'get: {pre_move}')
        do_mskb(prev_moves)
        print(f'move_cnt: {move_cnt}, {timeoffs}, {prev_moves}')
    # print(dec, mode)
    elif mode == 4:
        # print("get faces")
        pass
    elif mode == 5:
        print("get info")
    elif mode == 9:
        print("get battery")
    else:
        print(f"get wrong mode: {mode}")
    

async def main():
    global DECODER, iv

    # Search the GAN CUBE
    print("Searching for GAN CUBE...")
    devices = await BleakScanner.discover()
    gan_devices = []
    for d in devices:
        if d.name and d.name.startswith("GAN"):
            gan_devices.append(d)
    cube = None
    if len(gan_devices) == 0:
        print("No GAN CUBE found")
        return
    elif len(gan_devices) == 1:
        print(f"Found GAN CUBE: {gan_devices[0].name}")
        cube = gan_devices[0]
    else:
        device_names = [d.name for d in gan_devices]
        print("Multiple GAN CUBEs found, please select one:")
        for i, name in enumerate(device_names):
            print(f"{i}: {name}")
        while cube is None:
            try:
                selection = int(input("Selection: "))
                cube = gan_devices[selection]
            except ValueError:
                print("Invalid selection")
            except IndexError:
                print("Invalid selection")

    key, iv = init_kiv(cube.address)
    DECODER = AES(key)
    DECODER.iv = iv

    print(f"Connecting to {cube.name}, {cube.address}")
    async with BleakClient(cube.address) as client:
        
        cube_service = None
        for service in client.services:
            if service.uuid == SERVICE_UUID:
                cube_service = service
                break
        
        if cube_service is None:
            print("Unable to find GAN CUBE service or unsppported GAN CUBEs")
            return
        
        read_chrct = None
        write_chrct = None
        for chrct in cube_service.characteristics:
            if chrct.uuid == CHRCT_UUID_READ:
                read_chrct = chrct
            elif chrct.uuid == CHRCT_UUID_WRITE:
                write_chrct = chrct
        
        if read_chrct is None or write_chrct is None:
            print("Unable to find GAN CUBE read or write characteristic")
            return
        
        print("Connected to GAN CUBE")

        await client.start_notify(read_chrct, read_handler)

        while True:

            await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
    exit()

    # key: [139, 166, 161, 92, 67, 61, 22, 7, 32, 5, 24, 84, 66, 17, 18, 83] 
    # iv: [155, 167, 145, 92, 51, 172, 118, 39, 32, 149, 120, 20, 50, 18, 2, 67]
    
    key = [139, 166, 161, 92, 67, 61, 22, 7, 32, 5, 24, 84, 66, 17, 18, 83] 
    iv  = [155, 167, 145, 92, 51, 172, 118, 39, 32, 149, 120, 20, 50, 18, 2, 67]

    AES = AES(key)

    bts = [0]*20
    bts[0] = 5

    # encrypt
    enc = AES.encrypt([bts[i] ^ iv[i] for i in range(16)]) + [0]*4
    enc = enc[:4] + AES.encrypt([enc[i+4] ^ iv[i] for i in range(16)])
    
    print(enc)

    # decrypt
    _block = AES.decrypt(enc[4:])
    dec = [_block[i] ^ iv[i]  for i in range(16)]
    _block = AES.decrypt(enc[:4] + dec[:12]) 
    dec = [_block[i] ^ iv[i] for i in range(16)] + dec[12:]
    print(dec)

    # end bytes
    [208, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]