from PIL import Image
from operator import itemgetter
import configparser


def distance(tup_1, tup_2):
    return ((tup_1[0] - tup_2[0]) ** 2 + (tup_1[1] - tup_2[1]) ** 2 + (tup_1[2] - tup_2[2]) ** 2) ** .5


def remove_background(colors_list):
    for entry in colors_list:
        if entry[1][-1] == 0:
            colors_list.pop(colors_list.index(entry))
            return colors_list
    return colors_list


def find_closest(extra_color, colors):
    closest_match = None
    closest_distance = float('inf')
    for color in colors:
        if distance(color[1], extra_color[1]) < closest_distance:
            closest_match = color
            closest_distance = distance(color[1], extra_color[1])
    return closest_match


class Sprite:

    def __init__(self, dex_number):

        try:
            img = Image.open(f'sprites/{dex_number}.png').convert("RGBA")
            col = img.getcolors()
            col.sort(key=itemgetter(0), reverse=True)
            self.colors = remove_background(col)
            self.pixel_map = img.load()
        except FileNotFoundError:
            print(f'Invalid dex_number: {dex_number}')
            raise FileNotFoundError


class Swapper:

    def __init__(self, sprite_1, sprite_2):
        self.key = dict(zip([i[1] for i in sprite_1.colors], [i[1] for i in sprite_2.colors]))
        if len(sprite_1.colors) > len(sprite_2.colors):
            extras = sprite_1.colors[len(sprite_2.colors):]
            for extra in extras:
                closest = find_closest(extra, sprite_1.colors[:len(sprite_2.colors)])
                if closest:
                    self.key[extra[1]] = self.key[closest[1]]
                else:
                    self.key[extra[1]] = extra[1]

    def swap(self, pixel):
        if self.key.get(pixel):
            return self.key[pixel]
        else:
            return pixel


config = configparser.ConfigParser()
config.read('config.ini')


def main(original_sprite, swap_sprite):
    original = Sprite(original_sprite)
    new_palette = Sprite(swap_sprite)
    swap = Swapper(original, new_palette)
    im = Image.open(f"sprites/{original_sprite}.png").convert("RGBA")
    original_pixels = im.load()
    new_image = Image.new(im.mode, im.size)
    pixels = new_image.load()
    for x in range(im.size[0]):
        for y in range(im.size[1]):
            pixels[x, y] = swap.swap(original_pixels[x, y])
    new_image.show()
    if config['main']['save'].lower() == 'true':
        new_image.save(f"saves/{original_sprite}to{swap_sprite}.png")


def run():
    sprite_1 = config['main']['sprite_1']
    sprite_2 = config['main']['sprite_2']
    main(sprite_1, sprite_2)
    if config['main']['show_both'].lower() == 'true':
        main(sprite_2, sprite_1)
