import time
import math

def default_callback():
    print("aosdoasfo")

class EncoderLock:
    def __init__(self, pixels, correct_solution, tolerance=10):
        self.pixels = pixels
        self.correct_solution = correct_solution
        self.tolerance = tolerance
        self.current_index = 0  # index aktualnie edytowanej diody
        self.hue_values = [0] * len(correct_solution)  # obecne wartości HUE dla każdej diody
        self.brightness = 0.5  # domyślna jasność mignięcia
        self.direction = 1  # kierunek migania (1 = rośnie, -1 = maleje)
        self.running = False
        self.confirm_callback = default_callback

    def hue_to_rgb(self, hue, saturation=1.0, brightness=1.0):
        h = hue # 0-360
        s = saturation
        v = brightness

        c = v * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = v - c

        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)

    def update_leds(self):
        #print("update leds")
        for i in range(len(self.hue_values)):
            if i < self.current_index:
                r, g, b = self.hue_to_rgb(self.hue_values[i], brightness=.75)
            elif i == self.current_index:
                r, g, b = self.hue_to_rgb(self.hue_values[i], brightness=self.brightness)
            else:
                r, g, b = self.hue_to_rgb(self.hue_values[i], brightness=.25)
            self.pixels[i] = (r, g, b)
        self.pixels.show()

    def encoder_left_callback(self):
        self.hue_values[self.current_index] = (self.hue_values[self.current_index] - 1) % 360
        self.update_leds()

    def encoder_right_callback(self):
        print("right callback")
        self.hue_values[self.current_index] = (self.hue_values[self.current_index] + 1) % 360
        self.update_leds()

    def green_button_callback(self):
        print("green callback")
        print("current index: ", self.current_index)
        print("len(hue_values): ", len(self.hue_values))
        if self.current_index < len(self.hue_values) - 1:
            self.current_index += 1
            self.update_leds()
        else:
            print("sss")
            self.confirm_callback()

    def red_button_callback(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_leds()
            
    def assign_confirm_callback(self, callback):
        self.confirm_callback = callback

    def confirm_solution(self):
        for i, (hue, correct) in enumerate(zip(self.hue_values, self.correct_solution)):
            if abs(hue - correct) > self.tolerance:
                return False
        return True

    def run(self):
        self.running = True
        while self.running:
            self.brightness += 0.01 * self.direction
            if self.brightness >= 1.0:
                self.brightness = 1.0
                self.direction = -1
            elif self.brightness <= 0.5:
                self.brightness = 0.5
                self.direction = 1

            self.update_leds()
            time.sleep(0.05)
