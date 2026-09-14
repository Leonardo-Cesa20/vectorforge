import cv2
import numpy as np
from vectorforge.core.models import VectorShape

def _limit_nodes(points, max_nodes):
    if len(points) <= max_nodes:
        return points

    indices = np.linspace(
        0, len(points)-1, max_nodes
    ).astype(int)
    return points[indices]

def vectorize(binary, settings):
    retrieval = cv2.RETR_TREE if settings.preserve_holes else cv2.RETR_EXTERNAL

    contours, hierarchy = cv2.findContours(
        binary, retrieval, cv2.CHAIN_APPROX_NONE
    )
    hierarchy_data = hierarchy[0] if hierarchy is not None else None

    shapes = []

    for index, contour in enumerate(contours):
        area = abs(cv2.contourArea(contour))
        if area < settings.min_area:
            continue

        perimeter = cv2.arcLength(contour, True)
        epsilon = max(
            0.00008,
            settings.simplify / 100.0
        ) * perimeter

        points = cv2.approxPolyDP(
            contour, epsilon, True
        ).reshape(-1,2).astype(float)

        points = _limit_nodes(
            points, settings.max_nodes_per_path
        )

        if len(points) < 3:
            continue

        hole = False
        if hierarchy_data is not None:
            hole = hierarchy_data[index][3] != -1

        shapes.append(VectorShape(
            kind="path",
            layer="Furos" if hole else "Contornos",
            points=points,
            closed=True,
            confidence=0.99,
            hole=hole,
            source_index=index,
        ))

    return shapes
