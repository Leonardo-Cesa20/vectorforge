import math
import cv2
import numpy as np
from vectorforge.core.models import VectorShape

def circle_fit(points):
    if len(points) < 10:
        return 1e9, None, None

    x = points[:,0]
    y = points[:,1]
    matrix = np.column_stack([2*x, 2*y, np.ones(len(points))])
    target = x*x + y*y

    try:
        solution, *_ = np.linalg.lstsq(matrix, target, rcond=None)
    except Exception:
        return 1e9, None, None

    cx, cy, c = solution
    radius_sq = c + cx*cx + cy*cy

    if radius_sq <= 0:
        return 1e9, None, None

    radius = math.sqrt(radius_sq)
    distances = np.sqrt((x-cx)**2 + (y-cy)**2)
    error = float(
        np.mean(np.abs(distances-radius)) / max(radius,1e-6)
    )

    return error, (float(cx), float(cy)), float(radius)

def optimize(shapes, settings):
    if settings.preserve_original_paths and settings.art_type == "logo":
        return shapes

    strength = max(0.0, min(1.0, settings.geometry_strength))

    if settings.art_type == "logo":
        strength *= 0.18
    elif settings.art_type == "technical":
        strength = max(strength, 0.80)

    if strength <= 0.05:
        return shapes

    result = []

    for shape in shapes:
        if shape.points is None or len(shape.points) < 4:
            result.append(shape)
            continue

        error, center, radius = circle_fit(shape.points)

        if error <= 0.008 * strength:
            result.append(VectorShape(
                kind="circle",
                layer="Círculos",
                center=center,
                radius=radius,
                closed=True,
                confidence=max(0.88, 1-error*30),
                hole=shape.hole,
                source_index=shape.source_index,
            ))
        else:
            result.append(shape)

    return result
