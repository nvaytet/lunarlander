# SPDX-License-Identifier: BSD-3-Clause

import importlib
import glob

import lunarlander


bots = []
for repo in glob.glob("*_bot"):
    module = importlib.import_module(f"{repo}")
    bots.append(module.Bot())

start = None
# start = vg.Location(longitude=-68.004373, latitude=18.180470)

lunarlander.play(
    bots=bots,  # List of bots to use
    manual=True,  # Set to True to play manually
)


# # SPDX-License-Identifier: BSD-3-Clause

# # import simple_ai

# # import my_ai

# from dataclasses import dataclass


# # names = [
# #     "John",
# #     "Dave",
# #     "Anna",
# #     "Greg",
# #     "Lisa",
# #     "Simon",
# #     "Tobias",
# #     "Isobel",
# #     "Oliver",
# # ]

# # players = {name: simple_ai for name in names}
# # # players[my_ai.CREATOR] = my_ai


# @dataclass
# class Bot:
#     team: str


# bots = [Bot("neil")]

# lunarlander.start(
#     bots=bots,
#     manual=True,
#     # time_limit=8 * 60,  # Time limit in seconds
#     # fullscreen=False,  # Set to True for fullscreen
#     # seed=None,  # Set seed to always generate the same map
#     # high_contrast=False,  # Set to True for high contrast mode
#     # crystal_boost=1,  # Set to > 1 to artificially increase crystal production
# )
