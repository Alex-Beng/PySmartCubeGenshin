from utils import get_quaternion, quat2rotm

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from numpy import sin, cos

from itertools import product, combinations


def rorate_mat_generator(file_path):
    def read_file(file_path):
        lists = []
        with open(file_path, 'r') as f:
            
            lines = f.readlines()
            # lists = [eval(line) for line in lines]
            lists = lines
        return lists
    datas = read_file(file_path)
    
    for dt in datas:
        dec = dt.strip()
        value = ''.join([bin(bt+256)[3:] for bt in dec]) if len(dec) == 20 else dec
        mode = int(value[0:4], 2)
        if mode != 1:
            continue

        qs = get_quaternion(dec)
        rotms = [quat2rotm(q) for q in qs]

        for qr in zip(qs, rotms):
            yield qr

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
ax.scatter([0],[0],[0],color="black",s=10)

d = [-4, 4]
vertex = []
rad = 0
colors = ['r', 'g', 'b', 'y', 'c', 'm']
cnt = 0
for s, e in combinations(np.array(list(product(d,d,d))), 2):
    if np.sum(np.abs(s-e)) == d[1]-d[0]: 
        # init vertex
        v = ax.plot3D(*zip(s, e), color=colors[cnt%len(colors)])
        cnt += 1
        vertex.append(v + [s, e])
# draw line
for i in range(3):
    s = [0]*3
    e = [0]*3
    e[i] = coor_len // 2
    v = ax.plot3D(*zip(s, e), color=coor_color[i])
    vertex.append(v + [s, e])
# gravity?
s = [0]*3
e = [0]*3
v = ax.plot3D(*zip(s, e), color='pink')
vertex.append(v + [s, e])

rotm_gen = rorate_mat_generator('../data/yrot.bin')
rotms = [m for m in rotm_gen]

def update(frame):
    print(f"f: {frame}")

    q, rotm = rotms[frame]
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
    e = [-i*10 for i in e]
    v.set_data_3d(*zip(s,e))

    return vertex

ani = animation.FuncAnimation(fig, update, interval=50)

plt.show()
# ani.save('../data/test2.gif', writer='imagemagick', fps=30)

