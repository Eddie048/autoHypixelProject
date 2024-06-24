import json
import os


class ImageReader:

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
