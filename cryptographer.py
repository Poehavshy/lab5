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

