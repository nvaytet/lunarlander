# SPDX-License-Identifier: BSD-3-Clause

import hashlib
from typing import Any, Iterator, Tuple

import numpy as np
from PIL import Image, ImageDraw
import pyglet

from . import config


def wrap_position(x: float, y: float) -> Tuple[float, float]:
    x = x % config.nx
    y = y % config.ny
    if np.isscalar(x):
        if x < 0:
            x = config.nx + x
        if y < 0:
            y = config.ny + y
    else:
        x = np.where(x < 0, x + config.nx, x)
        y = np.where(y < 0, y + config.ny, y)
    return x, y


def distance_on_plane(xa: float, ya: float, xb: float, yb: float) -> float:
    return np.sqrt((xb - xa) ** 2 + (yb - ya) ** 2)


def distance_on_torus(xa: float, ya: float, xb: float, yb: float) -> float:
    dx = np.abs(xb - xa)
    dy = np.abs(yb - ya)
    return np.sqrt(
        np.minimum(dx, config.nx - dx) ** 2 + np.minimum(dy, config.ny - dy) ** 2
    )


def periodic_distances(
    xa: float, ya: float, xb: float, yb: float
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    xc = xa + config.nx
    yc = ya + config.ny
    xl = np.array([xb, xb + config.nx, xb + 2 * config.nx] * 3)
    yl = np.array([yb] * 3 + [yb + config.ny] * 3 + [yb + 2 * config.ny] * 3)
    d = np.sqrt((xl - xc) ** 2 + (yl - yc) ** 2)
    return d, xl, yl


class ReadOnly:
    def __init__(self, props: dict):
        self._data = props
        for key, item in props.items():
            setattr(self, key, item)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def keys(self) -> Iterator:
        return self._data.keys()

    def values(self) -> Iterator:
        return self._data.values()

    def items(self) -> Iterator:
        return self._data.items()


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
