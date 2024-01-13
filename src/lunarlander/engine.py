# SPDX-License-Identifier: BSD-3-Clause

import time

import numpy as np
import pyglet

from . import config
from .asteroid import Asteroid
from .graphics import Graphics
from .player import Player
from .scores import read_scores
from .terrain import Terrain


def add_key_actions(window, player):
    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.UP:
            if player.flying:
                player.main_thruster = True
        elif symbol == pyglet.window.key.LEFT:
            if player.flying:
                player.left_thruster = True
        elif symbol == pyglet.window.key.RIGHT:
            if player.flying:
                player.right_thruster = True

    @window.event
    def on_key_release(symbol, modifiers):
        if symbol == pyglet.window.key.UP:
            player.main_thruster = False
        elif symbol == pyglet.window.key.LEFT:
            player.left_thruster = False
        elif symbol == pyglet.window.key.RIGHT:
            player.right_thruster = False


class Engine:
    def __init__(
        self,
        bots,
        safe=False,
        # high_contrast=False,
        test=True,
        seed=None,
        fullscreen=False,
        manual=False,
    ):
        if seed is not None:
            np.random.seed(seed)

        self.nx = config.nx
        self.ny = config.ny
        self.start_time = None
        self._manual = manual
        self.asteroids = []
        # self.scores = self.read_scores(players=players, test=test)
        # self.high_contrast = high_contrast
        self.safe = safe
        self.exiting = False
        self.time_of_last_scoreboard_update = 0
        self.time_of_last_asteroid = 0

        self.game_map = Terrain()
        self.graphics = Graphics(game_map=self.game_map, fullscreen=fullscreen)

        self.bots = {bot.team: bot for bot in bots}

        starting_positions = self.make_starting_positions(nplayers=len(self.bots))

        self.players = {}
        for i, (name, pos) in enumerate(zip(self.bots, starting_positions)):
            self.players[name] = Player(
                team=name,
                number=i,
                position=pos,
                back_batch=self.graphics.background_batch,
                main_batch=self.graphics.main_batch,
            )

        self.scores = read_scores(players=self.players, test=test)

        if self._manual:
            add_key_actions(
                window=self.graphics.window, player=list(self.players.values())[0]
            )

        pyglet.clock.schedule_interval(self.update, 1 / config.fps)
        pyglet.app.run()

    # def read_scores(self, players: dict, test: bool) -> Dict[str, int]:
    #     scores = {}
    #     fname = "scores.txt"
    #     if os.path.exists(fname) and (not test):
    #         with open(fname, "r") as f:
    #             contents = f.readlines()
    #         for line in contents:
    #             name, score = line.split(":")
    #             scores[name] = int(score.strip())
    #     else:
    #         scores = {p: 0 for p in players}
    #     print("Scores:", scores)
    #     return scores

    def make_starting_positions(self, nplayers: int) -> list:
        random_origin = np.random.uniform(0, config.nx)
        step = config.nx / nplayers
        return [int(random_origin + i * step) % config.nx for i in range(nplayers)]

    def exit(self, message: str):
        self.exiting = True
        self.exit_time = time.time() + 1
        print(message)
        # score_left = len(self.dead_players)
        # for name, p in self.players.items():
        #     if not p.dead:
        #         p.update_score(score_left)
        # self.make_player_avatars()
        # sorted_scores = [
        #     (p.team, p.global_score)
        #     for p in sorted(
        #         self.players.values(), key=lambda x: x.global_score, reverse=True
        #     )
        # ]
        # fname = "scores.txt"
        # with open(fname, "w") as f:
        #     for name, p in self.players.items():
        #         f.write(f"{name}: {p.global_score}\n")
        # for i, (name, score) in enumerate(sorted_scores):
        #     print(f"{i + 1}. {name}: {score}")

    def undead_players(self):
        return (p for p in self.players.values() if not p.dead)

    def execute_player_bot(self, player, t: float, dt: float):
        instructions = None
        args = {
            "t": t,
            "dt": dt,
            "x": player.x,
            "y": player.y,
            "heading": player.heading,
            "vx": player.velocity[0],
            "vy": player.velocity[1],
            "fuel": player.fuel,
            "terrain": self.game_map.terrain,
        }
        if self.safe:
            try:
                instructions = self.bots[player.team].run(**args)
            except:  # noqa
                pass
        else:
            instructions = self.bots[player.team].run(**args)
        return instructions

    def call_player_bots(self, t: float, dt: float):
        players = list(self.undead_players())
        for player in players[int(self._manual) :]:
            if self.safe:
                try:
                    player.execute_bot_instructions(
                        self.execute_player_bot(player=player, t=t, dt=dt)
                    )
                except:  # noqa
                    pass
            else:
                player.execute_bot_instructions(
                    self.execute_player_bot(player=player, t=t, dt=dt)
                )

    def move_players(self, dt: float):
        for player in self.undead_players():
            player.move(dt=dt * 2)

    def check_landing(self, t: float):
        for player in self.undead_players():
            # if (not player.dead) and (player.y < config.ny - 1):
            # if (not player.dead) and (player.y < config.ny - 1):
            lem_floor = int(player.y - config.avatar_size[1] / 2)
            y_values = self.game_map.terrain[
                # int(player.y - config.avatar_size[1] / 2),
                int(player.x - config.avatar_size[0] / 2) : int(
                    player.x + config.avatar_size[0] / 2
                ),
            ]
            if any(y_values >= lem_floor):
                print("speed", np.linalg.norm(player.velocity))
                print("angle", player.heading)
                # uneven_terrain = any(pixels == 0)
                uneven_terrain = any(y_values < lem_floor)
                too_fast = np.linalg.norm(player.velocity) > config.max_landing_speed
                # landing_angle = np.abs(((player.heading + 180) % 360) - 180)
                landing_angle = np.abs(player.heading)
                bad_angle = landing_angle > config.max_landing_angle
                if any([uneven_terrain, too_fast, bad_angle]):
                    reason = []
                    if uneven_terrain:
                        print(y_values, lem_floor)
                        reason.append("uneven terrain")
                    if too_fast:
                        reason.append(f"velocity={player.velocity}")
                    if bad_angle:
                        reason.append(f"landing angle={landing_angle}")
                    player.crash(reason=", ".join(reason))
                else:
                    player.land(t)
                    print(f"Player {player.team} landed!")

    def compute_collisions(self):
        players = list(self.undead_players())
        n = len(players)
        x = np.array([p.x for p in players])
        y = np.array([p.y for p in players])
        xpos1 = np.broadcast_to(x, (n, n))
        xpos2 = xpos1.T
        ypos1 = np.broadcast_to(y, (n, n))
        ypos2 = ypos1.T
        dist = np.tril(np.sqrt((xpos2 - xpos1) ** 2 + (ypos2 - ypos1) ** 2))
        lems1, lems2 = np.where((dist < config.collision_radius) & (dist > 0))
        for i, j in zip(lems1, lems2):
            p1 = players[i]
            p2 = players[j]
            x1 = p1.position
            v1 = p1.velocity
            x2 = p2.position
            v2 = p2.velocity
            p1.velocity = v1 - np.dot(v1 - v2, x1 - x2) / np.linalg.norm(
                x1 - x2
            ) ** 2 * (x1 - x2)
            p2.velocity = v2 - np.dot(v2 - v1, x2 - x1) / np.linalg.norm(
                x2 - x1
            ) ** 2 * (x2 - x1)

    def update_asteroids(self, t, dt):
        delay = (
            1.0 - config.asteroid_delay
        ) / config.time_limit * t + config.asteroid_delay
        if (t - self.time_of_last_asteroid) > delay:
            self.asteroids.append(
                Asteroid(
                    x=np.random.uniform(0, config.nx),
                    y=config.ny + 100,
                    v=np.random.uniform(100, 200),
                    heading=np.random.uniform(-25, -155),
                    size=72,
                    batch=self.graphics.main_batch,
                )
            )
            self.time_of_last_asteroid = t
        for asteroid in self.asteroids:
            asteroid.move(dt=dt)
            tip = asteroid.tip()
            tip_size = asteroid.size * 0.2
            for player in self.players.values():
                if not player.dead:
                    d = np.sqrt((player.x - tip[0]) ** 2 + (player.y - tip[1]) ** 2)
                    if d < tip_size:
                        player.crash(reason="asteroid collision")
            if tip[1] <= self.game_map.terrain[int(tip[0])]:
                self.game_map.make_crater(x=int(tip[0]))
                asteroid.avatar.delete()
                self.asteroids.remove(asteroid)

    def update(self, dt: float):
        if self.start_time is None:
            self.start_time = time.time()
        t = time.time() - self.start_time

        if self.exiting:
            if self.graphics.exit_message is None:
                self.graphics.show_exit_message()
            return

        if t > config.time_limit:
            self.exit(message="Time limit reached!")
            return

        if abs(t - self.time_of_last_scoreboard_update) > 0.3:
            self.time_of_last_scoreboard_update = t
            self.graphics.update_scoreboard(t=config.time_limit - t)
            for player in [p for p in self.players.values() if not p.dead]:
                player.update_scoreboard(batch=self.graphics.main_batch)
        # if True:  # not self._manual:
        self.call_player_bots(t, dt)
        self.move_players(dt=dt)
        self.check_landing(t=t)
        self.compute_collisions()
        self.update_asteroids(t, dt)
        self.graphics.update_stars(t)

        number_of_alive_players = sum(
            not player.dead for player in self.players.values()
        )
        if number_of_alive_players == 0:
            self.exit(message="All players have either crashed or landed!")

        return
