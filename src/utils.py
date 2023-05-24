from scipy.spatial.transform import Rotation
import numpy as np

# get quatoernion from BLE decoded data
def get_quaternion(dec):
    assert(len(dec) == 20 or len(dec) == 160)

    value = ''.join([bin(bt+256)[3:] for bt in dec]) if len(dec) == 20 else dec
    mode = int(value[0:4], 2)
    assert(mode == 1)

    qs = []
    q = [0]*4
    for i in range(4):
        sign = -1 if int(value[4+i*16]) == 1 else 1
        v = int(value[5+i*16 : 20+i*16], 2)
        v *= sign
        v /= (2**15-1)
        q[i] = v
    qs.append(q)

    q = [0]*4
    for i in range(4):
        sign = -1 if int(value[80+i*16]) == 1 else 1
        v = int(value[81+i*16 : 96+i*16], 2)
        v *= sign
        v /= (2**15-1)
        q[i] = v
    qs.append(q)

    return qs

def quat2rotm(q):
    # written by myself
    # according to https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
    # w, x, y, z = q
    # R = [
    #     [1-2*(y**2+z**2), 2*(x*y-z*w), 2*(x*z+y*w)],
    #     [2*(x*y+z*w), 1-2*(x**2+z**2), 2*(y*z-x*w)],
    #     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x**2+y**2)]
    # ]
    # return np.array(R)
    # forgive for this shit

    return Rotation.from_quat(q).as_matrix()

def devices_selection(devices):
    selected_device = None
    if len(devices) == 0:
        print("No CUBE found")
        assert(selected_device is not None)
    elif len(devices) == 1:
        print(f"Found CUBE: {devices[0].name}")
        selected_device = devices[0]
    else:
        device_names = [d.name for d in devices]
        print("Multiple CUBEs found, please select one: [index]")
        for i, name in enumerate(device_names):
            print(f"{i}: {name}")
        while selected_device is None:
            try:
                selection = int(input("Selection: "))
                selected_device = devices[selection]
            except ValueError:
                print("Invalid selection")
            except IndexError:
                print("Invalid selection")
    return selected_device


def twos_comp(val, bits):
    # convert 2's complement binary string to int
    val = int(val, 2)
    if val & (1 << (bits - 1)):
        val -= 1 << bits
    return val
