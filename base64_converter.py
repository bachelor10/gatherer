import base64 as b64
import re
from PIL import Image
from io import BytesIO
import re, time, json
from tinydb import TinyDB, Query

# Inspo https://stackoverflow.com/questions/41957490/send-canvas-image-data-uint8clampedarray-to-flask-server-via-ajax

# this method turns transparent pixels white and saves as BMP file
def image_to_bitmap(image):

    image.convert("RGBA")  # Convert this to RGBA if possible

    pixel_data = image.load()

    if image.mode == "RGBA":
        # If the image has an alpha channel, convert it to white
        # Otherwise we'll get weird pixels
        for y in range(image.size[1]):  # For each row ...
            for x in range(image.size[0]):  # Iterate through each column ...
                # Check if it's opaque
                if pixel_data[x, y][3] < 255:
                    # Replace the pixel data with the colour white
                    pixel_data[x, y] = (255, 255, 255, 255)


    image.convert("RGB")
    return image


# this method converts a base 64 string to an image
# img_string is an string representation of an image
def convertToImg(img_string, equation):
    img_data = b64.standard_b64decode(re.sub('^data:image/.+;base64,', '', img_string))

    ms = str(int(round(time.time() * 1000)))

    file = './bitmap_data/' + ms + '.png'

    im = Image.open(BytesIO(img_data))

    im = image_to_bitmap(im)

    im.save(file)

    

    with TinyDB('solutions.json') as db:
        db.insert({
            ms: equation
        })

    
