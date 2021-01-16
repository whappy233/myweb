from django.shortcuts import render_to_response
from PIL import Image, ImageDraw, ImageFont
import random


class Picture(object):
    def __init__(self):
        self.width = 100
        self.height = 50

    def star(self):
        im = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        # 创建Draw对象:
        draw = ImageDraw.Draw(im)
        # 创建Font对象:
        font = ImageFont.truetype('/Users/tdesmtfa09/myweb/static/font/MONACO.TTF', 40)

        for i in range(0, 100):
            xy = (random.randrange(0, self.width), random.randrange(0, self.height))
            draw.point(xy, fill=(255, (random.randint(0, 255)), (random.randint(0, 255))))  # 填充每个像素

        s = ''
        for t in range(4):
            a = chr((random.randint(65, 90)))
            s = s + a
            draw.text((5+20*t,  2), a, font=font, fill=(255, (random.randint(0, 255)), (random.randint(0, 255))))
        del draw
        im.save("验证码.jpg")
        print(s)
        return s


def home(request):
    s = Picture().star()
    z = {}
    for i in s:
        z[i] = i
    print(z)
    return render_to_response('home.html')


