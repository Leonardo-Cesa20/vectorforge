import cv2
import numpy as np

def remove_border_components(binary):
    count, labels, stats, _ = cv2.connectedComponentsWithStats(binary, 8)
    h, w = binary.shape
    output = np.zeros_like(binary)

    for index in range(1, count):
        x, y, cw, ch, area = stats[index]
        touches = x == 0 or y == 0 or x+cw >= w or y+ch >= h
        if not touches:
            output[labels == index] = 255
        else:
            # Preserva objetos grandes que apenas encostam no limite.
            if area > binary.size * 0.03:
                output[labels == index] = 255

    return output

def remove_small_components(binary, min_area):
    count, labels, stats, _ = cv2.connectedComponentsWithStats(binary, 8)
    output = np.zeros_like(binary)

    for index in range(1, count):
        if stats[index, cv2.CC_STAT_AREA] >= max(1, int(min_area)):
            output[labels == index] = 255

    return output

def fill_small_holes(binary, max_area=80):
    inverse = cv2.bitwise_not(binary)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(inverse, 8)
    output = binary.copy()
    h, w = binary.shape

    for index in range(1, count):
        x, y, cw, ch, area = stats[index]
        touches = x == 0 or y == 0 or x+cw >= w or y+ch >= h
        if not touches and area <= max_area:
            output[labels == index] = 255

    return output

def reconstruct(binary, settings):
    output = binary.copy()

    if settings.remove_border_noise:
        output = remove_border_components(output)

    output = remove_small_components(output, settings.min_area)

    if settings.close_gaps > 0:
        size = settings.close_gaps * 2 + 1
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (size, size)
        )
        output = cv2.morphologyEx(output, cv2.MORPH_CLOSE, kernel)

    if settings.fill_small_holes:
        output = fill_small_holes(
            output,
            max_area=max(40, settings.min_area * 8)
        )

    return output
