import os.path
from pathlib import Path
from PIL import Image
import colorsys

def gora_dol(imgs,pure_list):
    rotator=[0 for i in imgs]
    for i in range(len(imgs)):
        imgs[i] = imgs[i].convert('L')
        imgs[i] = imgs[i].point(lambda x: 0 if x < 128 else 255, '1')
        hsv_im = imgs[i].convert('HSV')
        width, height = imgs[i].size
        if width > height:
            imgs[i] = imgs[i].rotate(90,expand=True)
            rotator[i] += 90

        h2 = height / 2


        suma1 = 0
        suma2 = 0
        iter1 = 0
        iter2 = 0
        for w in range(width):
            for h in range(height):
                r, g, b = hsv_im.getpixel((w, h))
                v, s, h3 = colorsys.rgb_to_hsv(r, g, b)

                if h > h2:
                    suma1 += v
                    iter1 += 1
                elif h<h2:
                    suma2 += v
                    iter2 += 1
        if (suma1/iter1) >(suma2/iter2):
            pass
        else:
            rotator[i]+=180
    return(rotator)


def main():
    pure_list = []
    save_path_pure = Path('pure/')
    for filename in os.listdir(save_path_pure):
        pure_list.append(filename)

    imgs = [Image.open(os.path.join(save_path_pure, Path(i))) for i in pure_list]

    rotator=gora_dol(imgs.copy(),pure_list)

    for i in range(len(imgs)):
        imgs[i] = imgs[i].rotate(rotator[i], expand=True)
        imgs[i].save(os.path.join(save_path_pure,pure_list[i]))
main()