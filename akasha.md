# Bluetooth characteristic notify gap

about 50 ms

# GAN gyro format

**Thanks to cs0x7f.**

There are (may be more)two types of gan gyro data format, one is for older gan devices, the other is for newer gan devices.

For new gan devices, maybe i3 and newer, using quaternion, int16 in original code, two quaternion in a BLE packet.


```python
# a decrypted BLE packet
dec = [byte]*20 
# convert to binarys
value = ''.join([bin(bt+256)[3:] for bt in dec])

mode = int(value[0:4], 2)
# 1. gyro mode is 1
assert(mode == 1)

# 2. the first quaternion lay in 
#   [ value[4 + i*16 : 20 + i*16] for i in range(4) ]
quat = []
for i in range(4):
    sign = -1 if int(value[4+i*16]) == 1 else 1
    v = int(value[5+i*16 : 20+i*16], 2)
    v *= sign
    v /= (2**15-1)
    quat.append(v)
# 3. the second quaternion lay in 
#   [ value[80 + i*16 : 96 + i*16] for i in range(4) ]
quat = []
for i in range(4):
    sign = -1 if int(value[80+i*16]) == 1 else 1
    v = int(value[81+i*16 : 96+i*16], 2)
    v *= sign
    v /= (2**15-1)
    quat.append(v)
```

for older gan devices, see: [AshleyF/briefcubing/issues/4](https://github.com/AshleyF/briefcubing/issues/4), which is not tested by me due to the lack of old gan devices.

# GAN en/decrypt format

new gan cubes using AES128 to encrypt the data

```python
KEY = [1,2,66,40,49,145,22,7,32,5,24,84,66,17,18,83]
IV = [17,3,50,40,33,1,118,39,32,149,120,20,50,18,2,67]

# the truly key and iv will be add mac mod to 0xff for the first 6 bytes

AES = AES(key)

# encrypt
enc = AES.encrypt([bts[i] ^ iv[i] for i in range(16)]) + [0]*4
enc = enc[:4] + AES.encrypt([enc[i+4] ^ iv[i] for i in range(16)])

# decrypt
_block = AES.decrypt(enc[4:])
dec = [_block[i] ^ iv[i]  for i in range(16)]
_block = AES.decrypt(enc[:4] + dec[:12]) 
dec = [_block[i] ^ iv[i] for i in range(16)] + dec[12:]

```

# GAN end bytes

```python
[208, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```