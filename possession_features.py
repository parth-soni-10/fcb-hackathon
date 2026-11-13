"""Small, dependency-free geometry helpers used by the possession notebook.

The tracking has no player identities, so these helpers deliberately operate on
the 46 anonymous slots and only return team-level evidence.
"""

import numpy as np


def central_velocity(position, fps):
    """Central-difference velocity; edges and non-finite positions stay NaN."""
    position = np.asarray(position, dtype=float)
    velocity = np.full_like(position, np.nan)
    if position.ndim == 1:
        if position.size > 2:
            velocity[1:-1] = (position[2:] - position[:-2]) * (fps / 2.0)
        return velocity
    if position.shape[0] > 2:
        velocity[1:-1] = (position[2:] - position[:-2]) * (fps / 2.0)
    return velocity


def safe_cosine(ax, ay, bx, by):
    """Cosine of two 2-D vectors, with a neutral 0 for zero-length vectors."""
    ax, ay, bx, by = (np.asarray(v, dtype=float) for v in (ax, ay, bx, by))
    na = np.hypot(ax, ay)
    nb = np.hypot(bx, by)
    out = np.zeros(np.broadcast(ax, ay, bx, by).shape, dtype=float)
    ok = np.isfinite(na) & np.isfinite(nb) & (na > 0.2) & (nb > 0.2)
    out[ok] = (ax[ok] * bx[ok] + ay[ok] * by[ok]) / (na[ok] * nb[ok])
    return np.clip(out, -1.0, 1.0)


def alignment_evidence(px, py, bx, by, team_of_slot, fps):
    """Return the nearest-player velocity alignment for each team.

    For every frame the closest visible player in each team is selected and its
    velocity is compared with the ball's velocity.  The result is high when the
    nearest player is running with the ball, low when running against it, and
    exactly neutral when the ball is stationary or missing.  This is a bounded
    supporting cue, never a possession label.
    """
    px = np.asarray(px, dtype=float)
    py = np.asarray(py, dtype=float)
    bx = np.asarray(bx, dtype=float)
    by = np.asarray(by, dtype=float)
    n = len(bx)
    zeros = np.zeros(n, dtype=float)
    if n == 0 or px.ndim != 2 or px.shape[0] != n:
        return {"cos_home": zeros, "cos_away": zeros, "diff": zeros}

    team_of_slot = np.asarray(team_of_slot, dtype=int)
    vx = central_velocity(px, fps)
    vy = central_velocity(py, fps)
    bvx = central_velocity(bx, fps)
    bvy = central_velocity(by, fps)
    bspeed = np.hypot(bvx, bvy)
    if not np.isfinite(bx).any():
        return {"cos_home": zeros, "cos_away": zeros, "diff": zeros}

    cos = []
    for team in (0, 1):
        sel = team_of_slot == team
        if not np.any(sel):
            cos.append(zeros)
            continue
        dx = px[:, sel] - bx[:, None]
        dy = py[:, sel] - by[:, None]
        distance = np.sqrt(dx * dx + dy * dy)
        distance = np.where(np.isfinite(distance), distance, np.inf)
        nearest = np.argmin(distance, axis=1)
        slots = np.flatnonzero(sel)[nearest]
        row = np.arange(n)
        cos.append(safe_cosine(vx[row, slots], vy[row, slots], bvx, bvy))

    # A stationary ball has no meaningful movement direction; a missing ball
    # already has NaN ball velocity and is caught by safe_cosine.  Keep both
    # cases neutral rather than letting tracker jitter create a vote.
    active = np.isfinite(bspeed) & (bspeed > 1.0)
    diff = np.where(active, cos[0] - cos[1], 0.0)
    return {"cos_home": cos[0], "cos_away": cos[1], "diff": np.clip(diff, -1.0, 1.0)}
