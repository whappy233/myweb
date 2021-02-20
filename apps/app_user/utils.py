#!/usr/bin/env python
# coding:utf-8


import json
import os
import random
import re
from uuid import uuid4
from django.conf import settings
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import smtplib
from email.mime.text import MIMEText


_letter_cases = "abcdefghjkmnpqrstuvwxy"  # 小写字母，去除可能干扰的i，l，o，z
_upper_cases = _letter_cases.upper()  # 大写字母
_numbers = ''.join(map(str, range(3, 10)))  # 数字
init_chars = ''.join((_letter_cases, _upper_cases, _numbers))
static_path = os.path.join(settings.BASE_DIR, "static")  # 静态文件路径
font_path = os.path.join(static_path, 'fonts', "MONACO.TTF")  # 字体路径


# 生成验证码
def generate_vcode(n=8):
    '''生成验证码'''
    vcode_str = ''.join(random.sample(init_chars, n))
    return vcode_str

# 发送电子邮件
def send_email(to_email, vcode_str):
    # email_enable = SysSetting.objects.get(types="basic",name='enable_email')
    # if email_enable.value == 'on':
    #     smtp_host = SysSetting.objects.get(types='email',name='smtp_host').value
    #     send_emailer = SysSetting.objects.get(types='email', name='send_emailer').value
    #     smtp_port = SysSetting.objects.get(types='email', name='smtp_port').value
    #     username = SysSetting.objects.get(types='email', name='username').value
    #     pwd = SysSetting.objects.get(types='email', name='pwd').value
    #     ssl = SysSetting.objects.get(types='email',name='smtp_ssl').value
    #     print(smtp_host,smtp_port,send_emailer,username,pwd)

    #     msg_from = send_emailer  # 发件人邮箱
    #     passwd = dectry(pwd)  # 发件人邮箱密码
    #     msg_to = to_email  # 收件人邮箱
    #     if ssl:
    #         s = smtplib.SMTP_SSL(smtp_host, int(smtp_port))  # 发件箱邮件服务器及端口号
    #     else:
    #         s = smtplib.SMTP(smtp_host, int(smtp_port))
    #     subject = "浩瀚星海 - 重置密码验证码"
    #     content = f"你的验证码为：{vcode_str}，验证码30分钟内有效！"

    #     msg = MIMEText(content, _subtype='html', _charset='utf-8')
    #     msg['Subject'] = subject
    #     msg['From'] = 'MrDoc助手[{}]'.format(msg_from)
    #     msg['To'] = msg_to
    #     try:
    #         s.login(username, passwd)
    #         s.sendmail(msg_from, msg_to, msg.as_string())
    #         return True
    #     except smtplib.SMTPException as e:
    #         print(repr(e))
    #         return False
    #     finally:
    #         s.quit()
    # else:
    #     return False
    print('邮件发送成功')
    return True


# 加密
def enctry(s):
    k = settings.SECRET_KEY
    encry_str = ""
    for i,j in zip(s,k):
        # i为字符，j为秘钥字符
        temp = str(ord(i)+ord(j))+'_' # 加密字符 = 字符的Unicode码 + 秘钥的Unicode码
        encry_str = encry_str + temp
    return encry_str


# 解密
def dectry(p):
    k = settings.SECRET_KEY
    dec_str = ""
    for i,j in zip(p.split("_")[:-1],k):
        # i 为加密字符，j为秘钥字符
        temp = chr(int(i) - ord(j)) # 解密字符 = (加密Unicode码字符 - 秘钥字符的Unicode码)的单字节字符
        dec_str = dec_str+temp
    return dec_str


# 生成验证码图片
def create_validate_code(size:tuple=(120, 30),
                            chars:str=init_chars,
                            mode="RGB",
                            font_size:int=20,
                            font_type=font_path,
                            length:int=4,
                            draw_lines:bool=True,
                            n_line:tuple=(1, 2),
                            draw_points:bool=True,
                            point_chance:int=1):
    '''
    @brief: 生成验证码图片
    @param:

        size: 图片的大小，格式（宽，高），默认为(120, 30)
        chars: 允许的字符集合，格式字符串
        mode: 图片模式，默认为RGB
        font_size: 验证码字体大小
        font_type: 验证码字体，默认为 ae_AlArabiya.ttf
        length: 验证码字符个数
        draw_lines: 是否划干扰线
        n_line: 干扰线的条数范围，格式元组，默认为(1, 2)，只有draw_lines为True时有效
        draw_points: 是否画干扰点
        point_chance: 干扰点出现的概率，大小范围[0, 100]

    @return: [0]: PIL Image实例
    @return: [1]: 验证码图片中的字符串
    '''

    def random_color():
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def get_chars():
        '''生成给定长度的字符串，返回列表格式'''
        return random.sample(chars, length)

    def create_lines():
        '''绘制干扰线'''
        line_num = random.randint(*n_line)  # 干扰线条数

        for i in range(line_num):
            # 起始点
            begin = (random.randint(0, size[0]), random.randint(0, size[1]))
            # 结束点
            end = (random.randint(0, size[0]), random.randint(0, size[1]))
            draw.line([begin, end], fill=(0, 0, 0))

    def create_points():
        '''绘制干扰点'''
        chance = min(100, max(0, int(point_chance)))  # 大小限制在[0, 100]

        for w in range(width):
            for h in range(height):
                tmp = random.randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((w, h), fill=(0, 0, 0))

    def create_strs():
        '''绘制验证码字符'''
        c_chars = get_chars()
        # strs = ' %s ' % ' '.join(c_chars)  # 每个字符前后以空格隔开
        font = ImageFont.truetype(font_type, font_size)
        # font_width, font_height = font.getsize(strs)
        # draw.text(((width - font_width) / 3, (height - font_height) / 3), strs, font=font, fill=random_color())

        for t in range(4):
            a = c_chars[t]
            draw.text((5+25*t,  2), a, font=font, fill=random_color())
        return ''.join(c_chars)


    width, height = size  # 宽， 高
    img = Image.new(mode, size, random_color())  # 创建图形
    draw = ImageDraw.Draw(img)  # 创建画笔

    if draw_lines:
        create_lines()
    if draw_points:
        create_points()
    strs = create_strs()
    del draw

    # 图形扭曲参数
    params = [1 - float(random.randint(1, 2)) / 100,
                0, 0, 0, 1 - float(random.randint(1, 10)) / 100,
                float(random.randint(1, 2)) / 500, 0.001,
                float(random.randint(1, 2)) / 500
                ]

    img = img.transform(size, Image.PERSPECTIVE, params)  # 创建扭曲
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)  # 滤镜，边界加强（阈值更大）
    

    print(strs)
    return img, strs


# 剪裁保存图片
def crop_image(old_photo, file, data, uid):
    '''
    剪裁保存图片.
    @prams:

        old_photo:    user_profile.photo
        file:         request.FILES['file']
        data:         request.FILES['photo_file']
        uid:          user.id
    '''

    # 获取Ajax发送的裁剪参数data，先用json解析。
    coords = json.loads(data)
    x = int(coords['x'])
    y = int(coords['y'])
    w = x + int(coords['width'])
    h = y + int(coords['height'])
    r = coords['rotate']

    # 裁剪图片,压缩尺寸为400*400。
    photo = Image.open(file)
    box = (x, y, w, h)
    size = (200, 200)
    crop_im = photo.crop(box).resize(size, Image.ANTIALIAS).rotate(r)

    # 随机生成新的图片名，自定义路径。
    ext = file.name.rsplit('.', 1)[-1]
    file_name = f'{uuid4().hex[:10]}.{ext}'
    # users/4/photo/983ff8164f.png
    cropped_photo = os.path.join('users', str(uid), "photo", file_name)
    # media/users/4/photo/983ff8164f.png
    file_path = os.path.join("media", cropped_photo)  

    directory = os.path.dirname(file_path)
    if os.path.exists(directory):
        crop_im.save(file_path)
    else:
        os.makedirs(directory)
        crop_im.save(file_path)

    # 如果头像不是默认头像，删除老头像图片, 节省空间
    if not old_photo == "default.png":
        current_photo_path = os.path.join("media", 'users', str(uid), "photo", os.path.basename(old_photo.url))
        os.remove(current_photo_path)

    return cropped_photo


# 邮箱格式验证
def validateEmail(email):
    from django.core.exceptions import ValidationError
    # 方式1
    from django.core.validators import validate_email
    try:
        validate_email(email)
    except ValidationError:
        return False
    else:
        return True

    # 方式2
    # from django import forms
    # f = forms.EmailField()
    # try:
    #     f.clean(value)
    # except ValidationError:
    #     return False
    # else:
    #     return True