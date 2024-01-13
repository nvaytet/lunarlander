# SPDX-License-Identifier: BSD-3-Clause

from typing import Optional

from matplotlib.colors import hex2color
import numpy as np
from PIL import Image
import pyglet

from . import config
from .core import Instructions

from .tools import recenter_image, string_to_color, text_to_raw_image


class Player:
    def __init__(
        self,
        number: int,
        team: str,
        position: float,
        batch: pyglet.graphics.Batch,
    ):
        self.team = team
        self.number = number
        self.score_text = None
        self._main_thruster = False
        self._left_thruster = False
        self._right_thruster = False
        self.fuel = config.max_fuel
        self.velocity = np.array([40.0, 0.0])

        self._rotate_left = False
        self._rotate_right = False
        self.color = string_to_color(team)
        self.make_avatar(position=position, batch=batch)
        self.heading = 90
        self.dead = False

    def make_avatar(self, position, batch):
        img = Image.open(config.resources / f"lem.png")
        img = img.resize(config.avatar_size).convert("RGBA")
        data = img.getdata()
        array = np.array(data).reshape(img.height, img.width, 4)
        rgb = hex2color(self.color)
        # print("where", np.where(array[..., 0] > 0))
        for i in range(3):
            array[..., i] = int(round(rgb[i] * 255))
            # array[..., i] = np.where(array[..., 0] > 0, int(round(rgb[i] * 255)), 0)
        # print("min, max", array[..., 3].min(), array[..., 3].max())

        imd = pyglet.image.ImageData(
            width=img.width,
            height=img.height,
            fmt="RGBA",
            data=Image.fromarray(array.astype(np.uint8)).tobytes(),
            pitch=-img.width * 4,
        )
        self.avatar = pyglet.sprite.Sprite(
            img=recenter_image(imd),
            x=position,
            y=config.ny - 100,
            batch=batch,
        )
        self.score_avatar = pyglet.sprite.Sprite(
            img=recenter_image(imd),
            x=config.nx + 30,
            y=config.ny - 100 - 75 * self.number,
            batch=batch,
        )

        # Main flame
        flame_img = Image.open(config.resources / f"flame.png")
        s = 0.75
        main_flame_img = flame_img.resize(
            (int(config.avatar_size[0] * s), int(config.avatar_size[1] * s))
        )
        imd = pyglet.image.ImageData(
            width=main_flame_img.width,
            height=main_flame_img.height,
            fmt="RGBA",
            data=main_flame_img.tobytes(),
            pitch=-main_flame_img.width * 4,
        )
        imd.anchor_x = main_flame_img.width // 2
        imd.anchor_y = config.avatar_size[1]
        self.main_flame = pyglet.sprite.Sprite(
            img=imd,
            x=self.avatar.x,
            y=self.avatar.y,
            batch=batch,
        )
        self.main_flame.opacity = 0

        # Left flame
        s = 0.5
        left_flame_img = flame_img.resize(
            (int(config.avatar_size[0] * s), int(config.avatar_size[1] * s))
        ).rotate(-90)
        imd = pyglet.image.ImageData(
            width=left_flame_img.width,
            height=left_flame_img.height,
            fmt="RGBA",
            data=left_flame_img.tobytes(),
            pitch=-left_flame_img.width * 4,
        )
        imd.anchor_x = (config.avatar_size[0] // 2) + left_flame_img.width
        imd.anchor_y = int(0.75 * left_flame_img.height)
        self.left_flame = pyglet.sprite.Sprite(
            img=imd,
            x=self.avatar.x,
            y=self.avatar.y,
            batch=batch,
        )
        self.left_flame.opacity = 0

        # Right flame
        right_flame_img = flame_img.resize(
            (int(config.avatar_size[0] * s), int(config.avatar_size[1] * s))
        ).rotate(90)
        imd = pyglet.image.ImageData(
            width=right_flame_img.width,
            height=right_flame_img.height,
            fmt="RGBA",
            data=right_flame_img.tobytes(),
            pitch=-right_flame_img.width * 4,
        )
        imd.anchor_x = -config.avatar_size[0] // 2
        imd.anchor_y = int(0.75 * right_flame_img.height)
        self.right_flame = pyglet.sprite.Sprite(
            img=imd,
            x=self.avatar.x,
            y=self.avatar.y,
            batch=batch,
        )
        self.right_flame.opacity = 0

    @property
    def x(self):
        return self.avatar.x

    @x.setter
    def x(self, value):
        self.avatar.x = value
        self.main_flame.x = value
        self.left_flame.x = value
        self.right_flame.x = value

    @property
    def y(self):
        return self.avatar.y

    @y.setter
    def y(self, value):
        self.avatar.y = value
        self.main_flame.y = value
        self.left_flame.y = value
        self.right_flame.y = value

    @property
    def position(self):
        return np.array([self.x, self.y])

    @property
    def heading(self):
        angle = -self.avatar.rotation
        return ((angle + 180) % 360) - 180

    @heading.setter
    def heading(self, value):
        value = (value + 360) % 360
        self.avatar.rotation = -value
        self.main_flame.rotation = -value
        self.left_flame.rotation = -value
        self.right_flame.rotation = -value

    @property
    def main_thruster(self):
        return self._main_thruster

    @main_thruster.setter
    def main_thruster(self, value):
        self._main_thruster = value
        self.main_flame.opacity = 255 * value

    @property
    def left_thruster(self):
        return self._left_thruster

    @left_thruster.setter
    def left_thruster(self, value):
        self._left_thruster = value
        self.left_flame.opacity = 255 * value

    @property
    def right_thruster(self):
        return self._right_thruster

    @right_thruster.setter
    def right_thruster(self, value):
        self._right_thruster = value
        self.right_flame.opacity = 255 * value

    @property
    def flying(self):
        return (self.fuel > 0) and (not self.dead)

    def get_thrust(self):
        h = np.radians(self.heading + 90.0)
        vector = np.array([np.cos(h), np.sin(h)])
        return (config.thrust * self.main_thruster * (self.fuel > 0)) * vector

    def move(self, dt):
        if self.dead:
            return
        acceleration = config.gravity + self.get_thrust()

        self.velocity += acceleration * dt

        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt

        self.x = self.x % config.nx

        if self.left_thruster and (self.fuel > 0):
            self.heading += config.rotation_speed * dt
        if self.right_thruster and (self.fuel > 0):
            self.heading -= config.rotation_speed * dt

        if self.fuel > 0:
            if self.main_thruster:
                self.fuel -= config.main_engine_burn_rate * dt
            if self.left_thruster or self.right_thruster:
                self.fuel -= config.rotation_engine_burn_rate * dt

    def crash(self, reason):
        self.dead = True
        x, y = self.x, self.y
        img = Image.open(config.resources / f"skull.png")
        img = img.resize(config.avatar_size).convert("RGBA")
        data = img.getdata()
        array = np.array(data).reshape(img.height, img.width, 4)
        rgb = hex2color(self.color)
        for i in range(3):
            array[..., i] = int(round(rgb[i] * 255))

        imd = pyglet.image.ImageData(
            width=img.width,
            height=img.height,
            fmt="RGBA",
            data=Image.fromarray(array.astype(np.uint8)).tobytes(),
            pitch=-img.width * 4,
        )
        batch = self.avatar.batch
        self.avatar.delete()
        self.avatar = pyglet.sprite.Sprite(
            img=recenter_image(imd),
            x=x,
            y=y,
            batch=batch,
        )

        self.score_avatar.delete()
        self.score_avatar = pyglet.sprite.Sprite(
            img=recenter_image(imd),
            x=config.nx + 30,
            y=config.ny - 100 - 75 * self.number,
            batch=batch,
        )
        print(f"Player {self.team} crashed! Reason: {reason}.")

    def land(self):
        self.dead = True

    def execute_bot_instructions(self, instructions: Optional[Instructions]):
        if instructions is None:
            return
        self.main_thruster = instructions.main and self.flying
        self.left_thruster = instructions.left and self.flying
        self.right_thruster = instructions.right and self.flying

    def update_scoreboard(self, batch):
        img = Image.new("RGBA", (150, 54), (0, 0, 0, 0))
        img.paste(
            text_to_raw_image(
                f"{self.team}",
                width=150,
                height=24,
                font=config.medium_font,
            ),
            (0, 0),
        )
        img.paste(
            text_to_raw_image(
                f"x={self.x:.1f}, y={self.y:.1f}",
                width=150,
                height=24,
                font=config.medium_font,
            ),
            (0, 14),
        )
        img.paste(
            text_to_raw_image(
                f"v=[{self.velocity[0]:.1f}, {self.velocity[1]:.1f}]",
                width=150,
                height=24,
                font=config.medium_font,
            ),
            (0, 28),
        )
        img.paste(
            text_to_raw_image(
                f"θ={self.heading:.1f}, fuel={self.fuel:.1f}",
                width=150,
                height=24,
                font=config.medium_font,
            ),
            (0, 42),
        )

        imd = pyglet.image.ImageData(
            width=img.width,
            height=img.height,
            fmt="RGBA",
            data=img.tobytes(),
            pitch=-img.width * 4,
        )
        if self.score_text is not None:
            self.score_text.delete()
        self.score_text = pyglet.sprite.Sprite(
            img=imd,
            x=config.nx + 55,
            y=config.ny - 120 - 75 * self.number,
            batch=batch,
        )
