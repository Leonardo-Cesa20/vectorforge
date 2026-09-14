import cv2
import numpy as np

def auto_crop(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    background = cv2.GaussianBlur(gray, (0,0), 25)
    darkness = cv2.subtract(background, gray)
    darkness = cv2.normalize(darkness, None, 0, 255, cv2.NORM_MINMAX)

    _, mask = cv2.threshold(
        darkness, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    points = cv2.findNonZero(mask)
    h, w = gray.shape

    if points is None:
        return image.copy(), (0,0,w,h)

    x, y, cw, ch = cv2.boundingRect(points)
    pad = max(12, int(max(cw, ch) * 0.05))
    x1, y1 = max(0, x-pad), max(0, y-pad)
    x2, y2 = min(w, x+cw+pad), min(h, y+ch+pad)

    return image[y1:y2, x1:x2].copy(), (x1,y1,x2-x1,y2-y1)

def normalize_image(image, denoise=1, edge_protection=0.65):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clip_limit = 1.6 + max(0.0, min(1.0, edge_protection)) * 1.8
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8,8))
    l = clahe.apply(l)

    normalized = cv2.cvtColor(
        cv2.merge([l, a, b]),
        cv2.COLOR_LAB2BGR
    )

    if denoise > 0:
        strength = 3 + int(denoise) * 2
        normalized = cv2.fastNlMeansDenoisingColored(
            normalized, None, strength, strength, 7, 21
        )

    return normalized
