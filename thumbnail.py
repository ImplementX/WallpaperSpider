#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import glob
from PIL import Image
from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

SYSTEM_SEPARATOR = os.path.sep


def thumbnail_pic(file_path):
    a = glob.glob(file_path + '**/*.jpg', recursive=True)

    for x in a:
        # 跳过缩略图文件夹
        if x.find('thumbnail') != -1:
            continue
        print("x is " + x)
        try:
            im = Image.open(x)
        except OSError:
            print("***********ERROR*************")
            print("can't open file " + x)
            print("*****************************")
            continue

        im.thumbnail((270, 480))
        print(im.format, im.size, im.mode)
        index = x.rfind(SYSTEM_SEPARATOR)
        save_folder = x[0:index + 1] + "thumbnail" + SYSTEM_SEPARATOR
        save_name = x[index + 1:len(x)]
        save_path = save_folder + save_name
        print("save as " + save_path)
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)

        # if not os.path.exists(x):
        try:
            im.save(save_path, 'JPEG')
        except OSError:
            im.mode = "RGB"
            im.save(save_path, 'JPEG')

    print('Thumbnail Generated !')


if __name__ == '__main__':
    path = 'wallpaper' + SYSTEM_SEPARATOR
    thumbnail_pic(path)
