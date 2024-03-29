# SPDX-License-Identifier: BSD-3-Clause

from typing import Optional, Union

import numpy as np
import pyglet
from matplotlib.colors import hex2color
from PIL import Image

from . import config
from .tools import Instructions, image_to_sprite, recenter_image, text_to_raw_image


class Player:
    def __init__(
        self,
        number: int,
        team: str,
        color: str,
        avatar: Union[int, str],
        position: float,
        back_batch: pyglet.graphics.Batch,
        main_batch: pyglet.graphics.Batch,
    ):
        self.team = team
        self.number = number
        self.score = 0
        self.score_text = None
        self._main_thruster = False
        self._left_thruster = False
        self._right_thruster = False
        self.fuel = config.max_fuel
        self.velocity = np.array([40.0, 0.0])

        self._rotate_left = False
        self._rotate_right = False
        self.color = color
        self.make_avatar(
            avatar=avatar,
            position=position,
            back_batch=back_batch,
            main_batch=main_batch,
        )
        self.heading = 90
        self.dead = False
        self.landed = False

    def make_avatar(
        self,
        avatar: Union[int, str],
        position: float,
        back_batch: pyglet.graphics.Batch,
        main_batch: pyglet.graphics.Batch,
    ):
        # Dark background
        bkg = pyglet.image.load(config.resources / "lem-background.png")
        self.avatar_background = pyglet.sprite.Sprite(
            img=recenter_image(bkg),
            x=position,
            y=config.ny - 100,
            batch=back_batch,
        )
        self.avatar_background.width = config.avatar_size[0]
        self.avatar_background.height = config.avatar_size[1]

        # Avatar foreground
        if isinstance(avatar, str):
            img = Image.open(avatar).resize(config.avatar_size).convert("RGBA")
        else:
            img = Image.open(config.resources / "avatars" / f"{avatar}.png")
            img = img.resize(config.avatar_size).convert("RGBA")
            data = img.getdata()
            array = np.array(data).reshape(img.height, img.width, 4)
            # rgb = hex2color(self.color)
            for i in range(3):
                array[..., i] = int(round(self.color[i] * 255))
            img = Image.fromarray(array.astype(np.uint8))
        self.avatar = image_to_sprite(
            img=img,
            x=position,
            y=config.ny - 100,
            batch=main_batch,
        )
        self.score_avatar = image_to_sprite(
            img=img,
            x=config.nx + 30,
            y=config.ny - 100 - 75 * self.number,
            batch=main_batch,
        )

        # Main flame
        flame_img = Image.open(config.resources / "flame.png")
        s = 0.75
        main_flame_img = flame_img.resize(
            (int(config.avatar_size[0] * s), int(config.avatar_size[1] * s))
        )
        self.main_flame = image_to_sprite(
            img=main_flame_img,
            x=self.avatar.x,
            y=self.avatar.y,
            batch=main_batch,
            anchor=[main_flame_img.width // 2, config.avatar_size[1]],
        )
        self.main_flame.opacity = 0

        # Left flame
        s = 0.5
        left_flame_img = flame_img.resize(
            (int(config.avatar_size[0] * s), int(config.avatar_size[1] * s))
        ).rotate(-90)
        self.left_flame = image_to_sprite(
            img=left_flame_img,
            x=self.avatar.x,
            y=self.avatar.y,
            batch=main_batch,
            anchor=[
                (config.avatar_size[0] // 2) + left_flame_img.width,
                int(0.75 * left_flame_img.height),
            ],
        )
        self.left_flame.opacity = 0

        # Right flame
        right_flame_img = flame_img.resize(
            (int(config.avatar_size[0] * s), int(config.avatar_size[1] * s))
        ).rotate(90)
        self.right_flame = image_to_sprite(
            img=right_flame_img,
            x=self.avatar.x,
            y=self.avatar.y,
            batch=main_batch,
            anchor=[-config.avatar_size[0] // 2, int(0.75 * right_flame_img.height)],
        )
        self.right_flame.opacity = 0

    @property
    def x(self) -> float:
        return self.avatar.x

    @x.setter
    def x(self, value: float):
        self.avatar.x = value
        self.avatar_background.x = value
        self.main_flame.x = value
        self.left_flame.x = value
        self.right_flame.x = value

    @property
    def y(self) -> float:
        return self.avatar.y

    @y.setter
    def y(self, value: float):
        self.avatar.y = value
        self.avatar_background.y = value
        self.main_flame.y = value
        self.left_flame.y = value
        self.right_flame.y = value

    @property
    def position(self) -> np.ndarray:
        return np.array([self.x, self.y])

    @property
    def heading(self) -> float:
        angle = -self.avatar.rotation
        return ((angle + 180) % 360) - 180

    @heading.setter
    def heading(self, value: float):
        value = (value + 360) % 360
        self.avatar.rotation = -value
        self.main_flame.rotation = -value
        self.left_flame.rotation = -value
        self.right_flame.rotation = -value

    @property
    def main_thruster(self) -> bool:
        return self._main_thruster

    @main_thruster.setter
    def main_thruster(self, value: bool):
        self._main_thruster = value
        self.main_flame.opacity = 255 * value

    @property
    def left_thruster(self) -> bool:
        return self._left_thruster

    @left_thruster.setter
    def left_thruster(self, value: bool):
        self._left_thruster = value
        self.left_flame.opacity = 255 * value

    @property
    def right_thruster(self) -> bool:
        return self._right_thruster

    @right_thruster.setter
    def right_thruster(self, value: bool):
        self._right_thruster = value
        self.right_flame.opacity = 255 * value

    @property
    def flying(self) -> bool:
        return (self.fuel > 0) and (not self.dead)

    def get_thrust(self) -> np.ndarray:
        h = np.radians(self.heading + 90.0)
        vector = np.array([np.cos(h), np.sin(h)])
        return (config.thrust * self.main_thruster * (self.fuel > 0)) * vector

    def move(self, dt: float):
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

    def crash(self, reason: str):
        self.dead = True
        # x, y = self.x, self.y
        img = Image.open(config.resources / "skull.png")
        img = img.resize(config.avatar_size).convert("RGBA")
        data = img.getdata()
        array = np.array(data).reshape(img.height, img.width, 4)
        rgb = hex2color(self.color)
        for i in range(3):
            array[..., i] = int(round(rgb[i] * 255))

        av_image = Image.fromarray(array.astype(np.uint8))
        batch = self.avatar.batch
        self.avatar.delete()
        self.avatar = image_to_sprite(
            img=av_image,
            x=self.x,
            y=self.y,
            batch=batch,
        )
        self.score_avatar.delete()
        self.score_avatar = image_to_sprite(
            img=av_image,
            x=config.nx + 30,
            y=config.ny - 100 - 75 * self.number,
            batch=batch,
        )
        print(f"Player {self.team} crashed! Reason: {reason}.")

    def land(
        self, time_left: float, landing_site_width: int, flag: Optional[str] = None
    ):
        self.landed = True
        score_breakdown = {
            "landing": config.score_landing_bonus,
            "site width": config.score_landing_site_bonus
            * (config.avatar_size[0] / landing_site_width),
            "time": config.score_time_bonus * (time_left / config.time_limit),
            "fuel": config.score_fuel_bonus * (self.fuel / config.max_fuel),
        }
        self.score = int(round(sum(score_breakdown.values())))
        print(
            f"Player {self.team} landed! Score={self.score}: "
            + ", ".join([f"{k}={v:.1f}" for k, v in score_breakdown.items()])
        )
        if flag is not None:
            try:
                img = Image.open(config.resources / "flags" / f"{flag}.png")
            except FileNotFoundError:
                img = Image.open(flag)
            width = int(config.avatar_size[0] / 1.5)
            height = int(width * (img.height / img.width))
            img = img.resize((width, height)).convert("RGBA")
            dx = config.avatar_size[0] // 5

            batch = self.avatar.batch
            self.flag = image_to_sprite(
                img=img,
                x=self.avatar.x + dx,
                y=self.avatar.y + dx,
                batch=batch,
                recenter=False,
            )
            self.score_flag = image_to_sprite(
                img=img,
                x=self.score_avatar.x + dx,
                y=self.score_avatar.y + dx,
                batch=batch,
                recenter=False,
            )

    def execute_bot_instructions(self, instructions: Optional[Instructions]):
        if instructions is None:
            return
        self.main_thruster = instructions.main and self.flying
        self.left_thruster = instructions.left and self.flying
        self.right_thruster = instructions.right and self.flying

    def update_scoreboard(self, batch: pyglet.graphics.Batch):
        img = Image.new("RGBA", (150, 54), (0, 0, 0, 0))
        texts = [
            f"Team {self.team}",
            f"x={self.x:.1f}, y={self.y:.1f}",
            f"v=[{self.velocity[0]:.1f}, {self.velocity[1]:.1f}]",
            f"θ={self.heading:.1f}, fuel={self.fuel:.1f}",
        ]
        for i, text in enumerate(texts):
            img.paste(
                text_to_raw_image(
                    text,
                    width=150,
                    height=24,
                    font=config.medium_font,
                ),
                (0, 14 * i),
            )

        if self.score_text is not None:
            self.score_text.delete()
        self.score_text = image_to_sprite(
            img=img,
            x=config.nx + 55,
            y=config.ny - 120 - 75 * self.number,
            batch=batch,
            recenter=False,
        )

    def to_dict(self) -> dict:
        return {
            "team": self.team,
            "position": (self.position[0], self.position[1]),
            "velocity": (self.velocity[0], self.velocity[1]),
            "heading": self.heading,
            "fuel": self.fuel,
            "dead": self.dead,
            "landed": self.landed,
        }
