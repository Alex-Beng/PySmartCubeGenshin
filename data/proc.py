import matplotlib.pyplot as plt


def read_file(file_path):
    lists = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        lists = [eval(line) for line in lines]
    return lists

def read_file2(file_path):
    lists = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        lists = [list(map(int, line.strip().split(' '))) for line in lines]
    return lists

def read_file3(file_path):
    lists = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        # map hex strings to int 
        lists = [list(map(lambda x: int(x, 16), line.strip().split(' '))) for line in lines]
    return lists

gyros = read_file('./stable_gyro')
# gyros = read_file('./throw_gyro')
gyros = read_file('./stable_long2_gyro')
gyros = read_file('./throw_long_gyro')
gyros = read_file3('../src/flip_out.txt')
# gyros = read_file2('./le')

for g in gyros:
    print(''.join([bin(d+256)[3:] for d in g]), end="\n")
exit()

# gyros = gyros[200:]
# 先获得每16bit的平均数
# 再检查与每16bit平均数相同的次数
def avg_test(win_size: int, x: int):
    win_num = 160-4-4-win_size+1
    avgs = [0]*(win_num)
    for g in gyros:
        value = ''.join([bin(bt+256)[3:] for bt in g])[4:-4]
        for beg in range(win_num):
            
            avgs[beg] += int(value[beg : beg+win_size], 2)
    for i in range(win_num):
        avgs[i] /= len(gyros)
        avgs[i] = int(avgs[i])

    times = {}
    for g in gyros:
        value = ''.join([bin(bt+256)[3:] for bt in g])[4:-4]
        for beg in range(win_num):
            if int(value[beg : beg+win_size], 2) == avgs[beg]:
                times[beg] = times.setdefault(beg, 0) + 1
    most_x_keys = sorted(times, key=lambda x: times[x], reverse=True)[:x]

    print(win_size)
    print(most_x_keys)
    print([times[key]+4 for key in most_x_keys])
    print()

    # 画出前x多的折线图
    
    # 新建窗口
    plt.figure()
    plt.title(f'sames: {win_size}, {x}')
    plt.plot([times[key]+4 for key in most_x_keys])
for i in range(4, 20):
    # avg_test(i, 10)
    pass
plt.show()

# 角速度为0
# 故检查所有 win_size 中全为零的次数
def zero_test(win_size: int, x: int):
    win_num = 160-4-4-win_size+1
    zcnts = [0]*(win_num)

    for g in gyros:
        value = ''.join([bin(bt+256)[3:] for bt in g])[4:-4]
        for beg in range(win_num):
            if int(value[beg : beg+win_size], 2) <= 1:
                zcnts[beg] += 1
    most_x_keys = sorted(range(win_num), key=lambda x: zcnts[x], reverse=True)[:x]

    print(win_size)
    print(most_x_keys)
    print([zcnts[key] for key in most_x_keys])
    print()

    # 画出前x多的折线图

    # 新建窗口
    plt.figure()
    plt.title(f'zeros: {win_size}, {x}')
    plt.plot([zcnts[key] for key in most_x_keys])
# for i in range(4, 9):
#     avg_test(i, 20)
# plt.show()

# 验证20 & 96
def test_20_96():
    for i,g in enumerate(gyros):
        value = ''.join([bin(bt+256)[3:] for bt in g])
        _20 = int(value[20:36], 2)
        _96 = int(value[96:112], 2)
        
        print(f'{i}:\t{_20}\t{_96}')
# test_20_96()



# 获取不变的bit
ans = gyros[0]
for g in gyros:
    for i in range(20):
        ans[i] &= g[i]
ans_mask = [255]*20
for g in gyros:
    for i in range(20):
        t_mask = ~(ans[i] ^ g[i])
        ans_mask[i] &= t_mask
    
# print(bin(ans_mask[0]))
print(''.join([bin(bt+256)[3:] for bt in ans_mask]))
print(''.join([bin(bt+256)[3:] for bt in ans]))
exit()
 
# 转换进制
for g in gyros:
    # bin
    tg = [bin(bt+256)[3:] for bt in g]
    print(' '.join(tg)[4:])

    # hex
    # tg = [hex(bt+256)[3:] for bt in g]
    # print(' '.join(tg))

    # 在十进制中补齐到三位
    # tg = ['%03d' % bt for bt in g]
    # print(' '.join(tg))
'''
1111
1111111000000000
1111110000000000
1111000000000000
11111111110000000
111011101111111111000000000111111000000000011110000000000001111111111000000011101110111


1111
'''

'''
1111
111000000000000000000000000000000110000000000000110000000000000000000000010011100000000000000000000000000000011000000000000011000000000000000000000001001111
'''