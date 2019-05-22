import os
from PIL import Image


for filename in os.listdir('.'):
    if filename.endswith('.png'):
        Image.open(filename).save('../bmptextures/{}.bmp'.format(filename[:-4]))