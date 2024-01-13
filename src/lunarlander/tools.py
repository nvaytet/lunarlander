# SPDX-License-Identifier: BSD-3-Clause

from typing import Optional, Tuple
import hashlib

from PIL import Image, ImageDraw
import pyglet

from . import config


def text_to_raw_image(text, width, height, font=None):
    if font is None:
        font = config.large_font
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text(
        (0, 0),
        text,
        fill=(255, 255, 255),
        font=font,
    )
    return img


def text_to_image(text, width, height, font=None):
    img = text_to_raw_image(text, width, height, font=font)
    return pyglet.image.ImageData(
        width=img.width,
        height=img.height,
        fmt="RGBA",
        data=img.tobytes(),
        pitch=-img.width * 4,
    )


def string_to_color(input_string: str) -> str:
    hash_object = hashlib.md5(input_string.encode())
    hex_hash = hash_object.hexdigest()
    return "#" + hex_hash[:6]


def recenter_image(img: pyglet.image.ImageData) -> pyglet.image.ImageData:
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2
    return img


def image_to_sprite(
    img: Image,
    x: float,
    y: float,
    batch: pyglet.graphics.Batch,
    recenter: bool = True,
    anchor: Optional[Tuple[float, float]] = None,
) -> pyglet.sprite.Sprite:
    imd = pyglet.image.ImageData(
        width=img.width,
        height=img.height,
        fmt="RGBA",
        data=img.tobytes(),
        pitch=-img.width * 4,
    )
    if anchor is not None:
        imd.anchor_x = anchor[0]
        imd.anchor_y = anchor[1]
    elif recenter:
        imd = recenter_image(imd)
    return pyglet.sprite.Sprite(img=imd, x=x, y=y, batch=batch)
