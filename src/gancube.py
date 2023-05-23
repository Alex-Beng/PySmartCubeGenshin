from aes import AES

class GanCube:
    # ONLY TESTED FOR GAN i3 NOW !
    BRAND = 'GAN'

    SERVICE_UUID        = '6e400001-b5a3-f393-e0a9-e50e24dc4179'
    CHRCT_UUID_READ     = '28be4cb6-cd67-11e9-a32f-2a2ae2dbcce4'
    CHRCT_UUID_WRITE    = '28be4a4a-cd67-11e9-a32f-2a2ae2dbcce4'

    KEY = [1,2,66,40,49,145,22,7,32,5,24,84,66,17,18,83]
    IV = [17,3,50,40,33,1,118,39,32,149,120,20,50,18,2,67]
    
    def __init__(self, mac: str):
        mac = list(map(int, mac.split(':'), [16]*6))
        key = [i for i in self.KEY]
        iv = [i for i in self.IV]
        for i in range(6):
            key[i]  = (key[i] + mac[5-i]) % 255
            iv[i]   = (iv[i] + mac[5-i]) % 255
        self.decoder = AES(key)
        self.decoder.iv = iv

    def encrypt(self, data):
        assert(len(data) == 20)

        iv = self.decoder.iv
        enc = self.decoder.encrypt([data[i] ^ iv[i] for i in range(16)]) + [0]*4
        enc = enc[:4] + self.decoder.encrypt([enc[i+4] ^ iv[i] for i in range(16)])

        return enc

    def decrypt(self, enc):
        assert(len(enc) == 20)

        iv = self.decoder.iv
        _block = self.decoder.decrypt(enc[4:])
        dec = [_block[i] ^ iv[i]  for i in range(16)]
        _block = self.decoder.decrypt(enc[:4] + dec[:12]) 
        dec = [_block[i] ^ iv[i] for i in range(16)] + dec[12:]
        
        return dec
    