# SPDX-License-Identifier: BSD-3-Clause

import uuid
from itertools import chain
from typing import Any, Iterator, Tuple

from matplotlib.colors import hex2color
import numpy as np
from PIL import Image
import pyglet

from . import config
from .base import Base

# from .game_map import MapView
from .tools import recenter_image, string_to_color, text_to_raw_image


class Player:
    def __init__(
        self,
        # ai: Any,
        # location: Tuple[int, int],
        # number: int,
        team: str,
        batch: Any,
        # game_map: np.ndarray,
        # score: int,
        # base_locations: np.ndarray,
        # high_contrast: bool = False,
    ):
        # self.x = 100
        # self.y = config.ny - 100
        self.thruster_on = False
        self.velocity = np.array([20.0, 0.0])

        self._rotate_left = False
        self._rotate_right = False
        # self._ay = 0
        # self.vx0 = 10
        # self.vy0 = 0
        print(team)
        self.color = string_to_color(team)
        print(self.color)
        self.make_avatar(batch=batch)
        self.heading = 0
        self.dead = False

    def make_avatar(self, batch):
        img = Image.open(config.resources / f"lem.png")
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
        self.avatar = pyglet.sprite.Sprite(
            img=recenter_image(imd),
            x=100,
            y=config.ny - 100,
            batch=batch,
        )

    @property
    def x(self):
        return self.avatar.x

    @x.setter
    def x(self, value):
        self.avatar.x = value

    @property
    def y(self):
        return self.avatar.y

    @y.setter
    def y(self, value):
        self.avatar.y = value

    @property
    def heading(self):
        return -self.avatar.rotation

    @heading.setter
    def heading(self, value):
        self.avatar.rotation = -value

    def get_thrust(self):
        h = np.radians(self.heading + 90.0)
        thrust_vector = np.array([np.cos(h), np.sin(h)])
        return (config.thrust * self.thruster_on) * thrust_vector

    def move(self, dt):
        if self.dead:
            return
        acceleration = config.gravity + self.get_thrust()

        self.velocity += acceleration * dt

        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt

        self.x = self.x % config.nx

        if self._rotate_left:
            self.heading += config.rotation_speed * dt
        if self._rotate_right:
            self.heading -= config.rotation_speed * dt

    def crash(self):
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

    def land(self):
        self.dead = True

        # # Update vertical velocity based on vertical acceleration
        # self.vertical_velocity += self.vertical_acceleration * time_step

        # # Apply terminal velocity in the downward direction
        # if self.vertical_velocity > self.max_vertical_speed:
        #     self.vertical_velocity = self.max_vertical_speed

        # # Update horizontal velocity based on horizontal acceleration
        # self.horizontal_velocity += self.horizontal_acceleration * time_step

        # # Update position based on velocities
        # # (adjust for your game's needs)
        # self.position_x += self.horizontal_velocity * time_step
        # self.position_y += self.vertical_velocity * time_step

    # def update_player_map(self, x: float, y: float):
    #     r = config.view_radius
    #     slices = self.game_map.view_slices(x=x, y=y, dx=r, dy=r)
    #     for s in slices:
    #         self.game_map.array[s[0], s[1]] = self.original_map_array[s[0], s[1]]

    # def build_base(self, x: float, y: float):
    #     uid = uuid.uuid4().hex
    #     self.bases[uid] = Base(
    #         x=x,
    #         y=y,
    #         team=self.team,
    #         number=self.number,
    #         batch=self.batch,
    #         owner=self,
    #         uid=uid,
    #         high_contrast=self.high_contrast,
    #     )
    #     self.base_locations[int(y), int(x)] = 1
    #     return uid

    # def init_dt(self):
    #     self.transformed_ships.clear()

    # def execute_ai(self, t: float, dt: float, info: dict, safe: bool = False):
    #     if safe:
    #         try:
    #             self.ai.run(t=t, dt=dt, info=info, game_map=self.game_map.array)
    #         except:
    #             pass
    #     else:
    #         self.ai.run(t=t, dt=dt, info=info, game_map=self.game_map.array)

    # def collect_transformed_ships(self):
    #     for uid in self.transformed_ships:
    #         del self.ships[uid]

    # @property
    # def children(self) -> Iterator:
    #     """
    #     All the players's vehicles, bases and mines
    #     """
    #     mines = [base.mines.values() for base in self.bases.values()]
    #     return chain(self.army, *mines)

    # @property
    # def vehicles(self) -> Iterator:
    #     """
    #     All the players's vehicles
    #     """
    #     return chain(self.tanks.values(), self.ships.values(), self.jets.values())

    # @property
    # def army(self) -> Iterator:
    #     """
    #     All the players's vehicles and bases
    #     """
    #     return chain(self.bases.values(), self.vehicles)

    # def remove(self, uid: str):
    #     if uid in self.tanks:
    #         self.tanks[uid].delete()
    #         del self.tanks[uid]
    #     elif uid in self.ships:
    #         self.ships[uid].delete()
    #         del self.ships[uid]
    #     elif uid in self.jets:
    #         self.jets[uid].delete()
    #         del self.jets[uid]
    #     else:
    #         for base in self.bases.values():
    #             if uid in base.mines:
    #                 del base.mines[uid]
    #                 base.make_avatar()

    # def remove_base(self, uid: str):
    #     self.bases[uid].delete()
    #     del self.bases[uid]

    # def economy(self) -> int:
    #     return int(sum([base.crystal for base in self.bases.values()]))

    # def make_avatar_base_image(self):
    #     self.avatar_base_image = Image.new("RGBA", (100, 24), (0, 0, 0, 0))
    #     key = "skull" if self.dead else "player"
    #     self.avatar_base_image.paste(config.images[f"{key}_{self.number}"], (0, 0))
    #     self.avatar_base_image.paste(
    #         text_to_raw_image(
    #             self.team[:10], width=70, height=24, font=config.medium_font
    #         ),
    #         (30, 0),
    #     )

    # def update_score(self, score: int):
    #     self.score_this_round += score
    #     self.global_score += score

    # def make_avatar(self, ind):
    #     self.score_position = ind
    #     img = Image.new("RGBA", (200, 24), (0, 0, 0, 0))
    #     img.paste(self.avatar_base_image, (0, 0))
    #     img.paste(
    #         text_to_raw_image(
    #             f"  {'  ' if self.score_position < 9 else ''}"
    #             f"{self.score_position + 1}.   "
    #             f"{self.global_score}[{self.score_this_round}]",
    #             width=100,
    #             height=24,
    #             font=config.medium_font,
    #         ),
    #         (100, 0),
    #     )

    #     imd = pyglet.image.ImageData(
    #         width=img.width,
    #         height=img.height,
    #         fmt="RGBA",
    #         data=img.tobytes(),
    #         pitch=-img.width * 4,
    #     )
    #     if self.avatar is not None:
    #         self.avatar.delete()
    #     self.avatar = pyglet.sprite.Sprite(
    #         img=imd,
    #         x=(config.nx * config.scaling) + 4,
    #         y=(config.ny * config.scaling) - 100 - 35 * self.score_position,
    #         batch=self.batch,
    #     )

    # def rip(self):
    #     for v in self.vehicles:
    #         v.delete()
    #     self.tanks.clear()
    #     self.ships.clear()
    #     self.jets.clear()
    #     self.dead = True
    #     self.make_avatar_base_image()

    # def dump_map(self):
    #     im = Image.fromarray(
    #         np.flipud((self.game_map.array.astype(np.uint8) + 1) * 127)
    #     )
    #     im.save(f"{self.team}_map.png")

    # def init_cross_animation(self):
    #     self.animate_cross = 8
    #     self.cross_x = np.linspace(
    #         self.avatar.x, (config.nx / 2) * config.scaling, self.animate_cross
    #     )
    #     self.cross_y = np.linspace(
    #         self.avatar.y, (config.ny / 2) * config.scaling, self.animate_cross
    #     )
    #     self.cross_s = np.linspace(1, 30, self.animate_cross)
    #     self.cross_o = [255] + ([128] * (self.animate_cross - 1))
    #     ind = self.animate_cross - 1
    #     self.avatar.x = self.cross_x[ind]
    #     self.avatar.y = self.cross_y[ind]
    #     self.avatar.opacity = self.cross_o[ind]
    #     self.avatar.scale = self.cross_s[ind]

    # def cross_animate(self):
    #     self.animate_cross -= 1
    #     self.avatar.x = self.cross_x[self.animate_cross]
    #     self.avatar.y = self.cross_y[self.animate_cross]
    #     self.avatar.scale = self.cross_s[self.animate_cross]
    #     self.avatar.opacity = self.cross_o[self.animate_cross]
