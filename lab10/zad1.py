import time
from PIL import Image, ImageDraw, ImageFont, ImageOps
import busio
import board
import adafruit_bme280.advanced as adafruit_bme280
import lib.oled.SSD1331 as SSD1331
import os

def bme280_config():
    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)
    bme280.sea_level_pressure = 1013.25
    bme280.standby_period = adafruit_bme280.STANDBY_TC_500
    bme280.iir_filter = adafruit_bme280.IIR_FILTER_X16
    return bme280

def bme280_read(bme):
    bme.overscan_pressure = adafruit_bme280.OVERSCAN_X16
    bme.overscan_humidity = adafruit_bme280.OVERSCAN_X1
    bme.overscan_temperature = adafruit_bme280.OVERSCAN_X2
    return {
        "temperature": round(bme.temperature, 2),
        "humidity": round(bme.humidity, 2),
        "pressure": round(bme.pressure, 2),
        "altitude": round(bme.altitude, 2)
    }

def display_on_oled(disp, parameters, index):
    #disp.clear()
    image = Image.new("RGB", (disp.width, disp.height), "BLACK")
    draw = ImageDraw.Draw(image)
    
    fontLarge = ImageFont.truetype("./lib/oled/Font.ttf", 20)
    fontSmall = ImageFont.truetype("./lib/oled/Font.ttf", 12)

    icons = {
        "temperature": Image.open("./lib/oled/pic.jpg").resize((20, 20)),
        "humidity": Image.open("./lib/oled/pic.jpg").resize((20, 20)),
        "pressure": Image.open("./lib/oled/pic.jpg").resize((20, 20)),
        "altitude": Image.open("./lib/oled/pic.jpg").resize((20, 20))
    }

    keys = list(parameters.keys())
    param1 = keys[index % len(keys)]
    param2 = keys[(index + 1) % len(keys)]

    image.paste(icons[param1], (5, 5))
    draw.text((30, 5), f"{parameters[param1]} {param1}", font=fontSmall, fill="WHITE")

    image.paste(icons[param2], (5, 35))
    draw.text((30, 35), f"{parameters[param2]} {param2}", font=fontSmall, fill="WHITE")

    disp.ShowImage(image, 0, 0)

if __name__ == "__main__":
    disp = SSD1331.SSD1331()
    disp.Init()
    disp.clear()
    bme = bme280_config()
    os.system('sudo systemctl stop ip-oled.service')
    
    index = 0
    
    while True:
        try:
            parameters = bme280_read(bme)

            display_on_oled(disp, parameters, index)
            index += 1

            # Wydruk do konsoli (opcjonalnie)
            print("odczyt z czujnika BME280:")
            print(f"temperatura: {parameters['temperature']}°C")
            print(f"wilgotność: {parameters['humidity']}%")
            print(f"ciśnienie: {parameters['pressure']} hPa")
            print(f"wysokość: {parameters['altitude']} m\n")

            time.sleep(2)
        except KeyboardInterrupt:
            print("keyboard interrupt")
            break