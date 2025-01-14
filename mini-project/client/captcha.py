import cv2
import numpy as np
from PIL import Image
from modules.oled_display import display_image

class Captcha:
    def __init__(self, image_path="modules/lib/oled/cat.png", missing_piece_size=(20, 20), canvas_size=(96, 64)):
        self.image_path = image_path
        self.missing_piece_size = missing_piece_size
        self.canvas_size = canvas_size
        self.axis = 'x'
        self.offset = [0, 0]
        self.original_position = None
        self.base_image, self.missing_piece, self.masked_image = self._prepare_images()
        # self.update_display()

    def _prepare_images(self):
        image = cv2.imread(self.image_path)
        image = cv2.resize(image, self.canvas_size)

        # create the missing piece
        x, y = np.random.randint(0, self.canvas_size[0] - self.missing_piece_size[0]), np.random.randint(0, self.canvas_size[1] - self.missing_piece_size[1])
        self.original_position = (x, y)
        piece = image[y:y + self.missing_piece_size[1], x:x + self.missing_piece_size[0]].copy()

        # create a masked version of the image
        masked_image = image.copy()
        masked_image[y:y + self.missing_piece_size[1], x:x + self.missing_piece_size[0]] = 0  # make the piece black

        # add white border around the black square
        masked_image[y:y + self.missing_piece_size[1], x] = 255  # left border
        masked_image[y:y + self.missing_piece_size[1], x + self.missing_piece_size[0] - 1] = 255  # right border
        masked_image[y, x:x + self.missing_piece_size[0]] = 255  # top border
        masked_image[y + self.missing_piece_size[1] - 1, x:x + self.missing_piece_size[0]] = 255  # bottom border

        return image, piece, masked_image

    def translate_piece(self, delta):
        if self.axis == 'x':
            self.offset[0] = max(0, min(self.offset[0] + delta, self.canvas_size[0] - self.missing_piece_size[0] - 4))
        elif self.axis == 'y':
            self.offset[1] = max(0, min(self.offset[1] + delta, self.canvas_size[1] - self.missing_piece_size[1] - 4))
        self.update_display()

    def switch_axis(self):
        self.axis = 'y' if self.axis == 'x' else 'x'

    def confirm_position(self):
        tolerance = 2  # allowable margin of error in pixels
        original_x, original_y = self.original_position

        if abs(original_x - self.offset[0] - 2) <= tolerance and abs(original_y - self.offset[1] - 2) <= tolerance:
            print("Captcha solved correctly!")
            return True
        else:
            print("Captcha failed!")
            return False

    def get_combined_image(self):
        combined_image = self.masked_image.copy()
        x, y = self.offset
        piece_with_border = self._add_border_to_piece()
        piece_h, piece_w = piece_with_border.shape[:2]
        combined_image[y:y + piece_h, x:x + piece_w] = piece_with_border
        return combined_image

    def _add_border_to_piece(self):
        # add a black and white border to the missing piece
        piece_with_border = cv2.copyMakeBorder(
            self.missing_piece, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[255, 255, 255]
        )
        piece_with_border = cv2.copyMakeBorder(
            piece_with_border, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=[0, 0, 0]
        )
        return piece_with_border

    def update_display(self):
        combined_image = self.get_combined_image()
        rgb_image = cv2.cvtColor(combined_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        display_image(pil_image)

if __name__ == "__main__":
    captcha = Captcha("modules/lib/oled/cat.png")

    # example of controlling Captcha using functions
    captcha.translate_piece(10)  # move right
    captcha.switch_axis()        # switch to vertical axis
    captcha.translate_piece(-5)  # move up
    captcha.confirm_position()   # confirm position
