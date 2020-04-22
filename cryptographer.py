from PIL import Image, ImageDraw
from cryptography.fernet import Fernet
import datetime


class Cryptographer:
    def __init__(self, image, key, text="decrypt"):
        self.image = Image.open(image)
        self.text = text
        self.key = key
        self.draw = ImageDraw.Draw(self.image)
        self.width = self.image.size[0]
        self.height = self.image.size[1]
        self.pix = self.image.load()
        self.cos_t = [
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            [0.9807853, 0.8314696, 0.5555702, 0.1950903, -0.1950903,-0.5555702,-0.8314696,-0.9807853],
            [0.9238795, 0.3826834,-0.3826834,-0.9238795, -0.9238795,-0.3826834, 0.3826834, 0.9238795],
            [0.8314696,-0.1950903,-0.9807853,-0.5555702, 0.5555702, 0.9807853, 0.1950903,-0.8314696],
            [0.7071068,-0.7071068,-0.7071068, 0.7071068, 0.7071068,-0.7071068,-0.7071068, 0.7071068],
            [0.5555702,-0.9807853, 0.1950903, 0.8314696, -0.8314696,-0.1950903, 0.9807853,-0.5555702],
            [0.3826834,-0.9238795, 0.9238795,-0.3826834, -0.3826834, 0.9238795,-0.9238795, 0.3826834],
            [0.1950903,-0.5555702, 0.8314696,-0.9807853, 0.9807853,-0.8314696, 0.5555702,-0.1950903]
        ]
        self.e = [
            [0.125, 0.176777777, 0.176777777, 0.176777777, 0.176777777, 0.176777777, 0.176777777, 0.176777777],
            [0.176777777, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
            [0.176777777, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
            [0.176777777, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
            [0.176777777, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
            [0.176777777, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
            [0.176777777, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
            [0.176777777, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25]
        ]

    def dct(self, dct, arr):
        s=0
        for i in range(8):
            for j in range(8):
                temp = 0.0
                for x in range(8):
                    for y in range(8):
                        temp = temp + self.cos_t[i][x]*self.cos_t[j][y]*arr[x][y][2]
                dct[i][j] = self.e[i][j] * temp
        return dct

    def idct(self, dct, arr):
        for i in range(8):
            for j in range(8):
                temp = 0
                for x in range(8):
                    for y in range(8):
                        temp += dct[x][y]*self.cos_t[x][i]*self.cos_t[y][j]*self.e[x][y]
                        tmp = 0
                        if temp > 255:
                            tmp = 255
                        elif temp < 0:
                            tmp = 0
                        else:
                            tmp = round(temp)
                        arr[i][j][2] = tmp
        return arr


    def text_to_xor(self):
        i = 0
        out = ""
        for char in self.text:
            if i == len(self.key) - 1:
                i = 0
            out += chr(ord(char) ^ ord(self.key[i]))
        self.text = out
    
    
    def encrypt(self):
        dct = [[0] * 8 for i in range(8)]
        temp = [[0] * 8 for i in range(8)]
        k = 0
        l = 0
        s = 0
        cipher = Fernet(self.key)
        self.text = cipher.encrypt(self.text)
        bytes = self.text_to_bits(self.text)

        for i in range(0, self.width - 1, 8):
            for j in range(0, self.height - 1, 8):
                if l >= len(bytes):
                    break
                for x in range(8):
                    for y in range(8):
                        temp[x][y] = [
                            self.pix[x+j, y+i][0],
                            self.pix[x+j, y+i][1],
                            self.pix[x+j, y+i][2]
                        ]
                dct = self.dct(dct, temp)
                k = abs(dct[3][4]) - abs(dct[4][3])
                if bytes[l] == '1':
                    if k <= 25:
                        dct[3][4] = (abs(dct[4][3]) + 150) if dct[3][4] >= 0 else -1 * (abs(dct[4][3]) + 150)
                else:
                    if k >= -25:
                        dct[4][3] = (abs(dct[3][4]) + 150) if dct[4][3] >= 0 else -1 * (abs(dct[3][4]) + 150)
                temp = self.idct(dct, temp)
                for x in range(8):
                    for y in range(8):
                        self.draw.point((x + j, y + i), (temp[x][y][0], temp[x][y][1], temp[x][y][2]))
                l+=1
            if l >= len(self.text)*8:
                break
        path = f"photo/encrypt/after/{datetime.datetime.today().strftime('%Y-%m-%d-%H.%M.%S') + 'crypto.png'}"
        self.image.save(path, "PNG")
        return path
    
    def decrypt(self):
        end = False
        bytes = ""
        dct = [[0] * 8 for i in range(8)]
        temp = [[0] * 8 for i in range(8)]
        for i in range(0, self.width - 1, 8):
            for j in range(0, self.height - 1, 8):
                for x in range(8):
                    for y in range(8):
                        temp[x][y] = [
                            self.pix[x+j, y+i][0],
                            self.pix[x+j, y+i][1],
                            self.pix[x+j, y+i][2]
                        ]
                dct = self.dct(dct, temp)
                k = abs(dct[3][4]) - abs(dct[4][3])
                if k >= 25:
                    bytes+="1"
                elif k <= -25:
                    bytes+="0"
                else:
                    end = True
                    break
            if end == True:
                break
        self.text = self.text_from_bits(bytes)
        cipher = Fernet(self.key)
        self.text = cipher.decrypt(self.text)
        return self.text
    
    def text_to_bits(self, text, encoding='utf-8', errors='surrogatepass'):
        bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
        return bits.zfill(8 * ((len(bits) + 7) // 8))

    def text_from_bits(self, bits, encoding='utf-8', errors='surrogatepass'):
        n = int(bits, 2)
        return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'

    def text_to_xor(self):
        i = 0
        out = ""
        for char in self.text:
            if i == len(self.key) - 1:
                i = 0
            out += chr(ord(char) ^ ord(self.key[i]))
        self.text = out


