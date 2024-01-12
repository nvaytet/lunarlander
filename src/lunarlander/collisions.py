# SPDX-License-Identifier: BSD-3-Clause

import numpy as np

from . import config


def collisions(players):
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
        p1.velocity = v1 - np.dot(v1 - v2, x1 - x2) / np.linalg.norm(x1 - x2) ** 2 * (
            x1 - x2
        )
        p2.velocity = v2 - np.dot(v2 - v1, x2 - x1) / np.linalg.norm(x2 - x1) ** 2 * (
            x2 - x1
        )
