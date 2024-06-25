import json
import os
from PIL import Image


class ImageReader:

    # takes in an image, returns a list of the lines of text in the image
    def get_text_from_image(self, img_str, pixel_size):
        img = Image.open(img_str)

        # Calculate size of box of usernames in tab menu
        max_width = (8 + 1 + 8 + 16 * (1 + 5) + 3 + 10 + 1) * pixel_size
        max_height = (16 * (8 + 1) - 1) * pixel_size
        x_offset = int(img.width / 2 - max_width / 2)
        y_offset = 20 * pixel_size

        # Crop screenshot to be just player usernames
        img = img.crop((x_offset, y_offset, x_offset + max_width, y_offset + max_height))

        ign_return_list = []

        # repeats 16 times as that is the maximum number of players in a lobby
        for x in range(16):
            temp_img = img.crop(box=(0, 9 * pixel_size * x, img.width, 9 * pixel_size * (x + 1) - pixel_size))

            arr = []

            for i in range(int(temp_img.width / pixel_size)):
                arr.append([])
                for k in range(int(temp_img.height / pixel_size)):
                    # plus ones move to the center roughly
                    px = temp_img.getpixel(xy=(i * pixel_size + 1, k * pixel_size + 1))

                    # the 4 rank colors, all of which may appear in tab
                    acceptable_colors = [(255, 170, 0), (85, 255, 255), (85, 255, 85), (170, 170, 170)]

                    # if the given pixel is one of these colors, it is part of a character
                    if acceptable_colors.__contains__(px):
                        arr[i].append(1)
                    else:
                        arr[i].append(0)

            # strings of length 0 aren't usernames
            temp_ign = self.read_string(arr)
            if len(temp_ign) > 0:
                ign_return_list.append(temp_ign)

        return ign_return_list

    def __init__(self):
        # reading the key from a file
        self.char_code = None
        with open(str(os.path.dirname(os.path.abspath(__file__))) + '/char_code.json') as f:
            data = f.read()

        # reconstructing the data as a dictionary
        self.char_code = json.loads(data)

    def get_char(self, char_arr):
        """takes in a small 2D boolean array and returns the character it represents, if any"""
        # check for a matching character
        for val in self.char_code:
            if char_arr == self.char_code[val]:
                return val

        return None

    def read_string(self, str_arr):
        """takes in a 2D boolean array and returns the string it represents"""
        blank_col = [0, 0, 0, 0, 0, 0, 0, 0]

        index = 0
        prev_blank_index = -1

        # initializing string to be built up
        result_ign = ""

        for col in str_arr:
            # on a black column, add a new character to the string
            if col == blank_col:
                if index - prev_blank_index > 1:

                    temp_char = self.get_char(str_arr[prev_blank_index + 1: index])

                    if temp_char is not None:
                        result_ign += temp_char

                prev_blank_index = index

            index += 1

        return result_ign
