import cv2
import numpy as np
from vectorforge.core.models import VisionCandidate

def _niblack(gray, window=31, k=-0.2):
    mean = cv2.boxFilter(gray.astype(np.float32), -1, (window,window))
    sqmean = cv2.boxFilter(
        (gray.astype(np.float32) ** 2), -1, (window,window)
    )
    std = np.sqrt(np.maximum(sqmean - mean*mean, 0))
    threshold = mean + k * std
    return np.where(gray.astype(np.float32) < threshold, 255, 0).astype(np.uint8)

def _sauvola(gray, window=31, k=0.22, r=128.0):
    mean = cv2.boxFilter(gray.astype(np.float32), -1, (window,window))
    sqmean = cv2.boxFilter(
        (gray.astype(np.float32) ** 2), -1, (window,window)
    )
    std = np.sqrt(np.maximum(sqmean - mean*mean, 0))
    threshold = mean * (1 + k * (std/r - 1))
    return np.where(gray.astype(np.float32) < threshold, 255, 0).astype(np.uint8)

def _wolf(gray, window=31, k=0.35):
    mean = cv2.boxFilter(gray.astype(np.float32), -1, (window,window))
    sqmean = cv2.boxFilter(
        (gray.astype(np.float32) ** 2), -1, (window,window)
    )
    std = np.sqrt(np.maximum(sqmean - mean*mean, 0))
    min_gray = float(gray.min())
    max_std = float(std.max()) or 1.0
    threshold = mean - k * (1 - std/max_std) * (mean - min_gray)
    return np.where(gray.astype(np.float32) < threshold, 255, 0).astype(np.uint8)

def _local_darkness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    background = cv2.GaussianBlur(gray, (0,0), 25)
    darkness = cv2.subtract(background, gray)
    return cv2.normalize(darkness, None, 0, 255, cv2.NORM_MINMAX)

def build_candidates(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    candidates = []

    _, otsu = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    candidates.append(("Otsu", otsu))

    adaptive = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        41, 7
    )
    candidates.append(("Adaptive", adaptive))

    candidates.append(("Sauvola", _sauvola(gray, 31, 0.22)))
    candidates.append(("Wolf", _wolf(gray, 31, 0.35)))
    candidates.append(("Niblack", _niblack(gray, 31, -0.18)))

    dark = _local_darkness(image)
    for threshold in (18, 28, 38, 50, 65, 80):
        _, candidate = cv2.threshold(
            dark, threshold, 255, cv2.THRESH_BINARY
        )
        candidates.append((f"Local {threshold}", candidate))

    for percentile in (5, 10, 15, 20, 25):
        threshold = int(np.percentile(gray, percentile))
        _, candidate = cv2.threshold(
            gray, threshold, 255, cv2.THRESH_BINARY_INV
        )
        candidates.append((f"Percentile {percentile}", candidate))

    return candidates

def _border_noise(binary):
    h, w = binary.shape
    border = np.concatenate([
        binary[0,:], binary[-1,:], binary[:,0], binary[:,-1]
    ])
    return float(np.count_nonzero(border) / max(len(border),1))

def _compactness(contours):
    values = []
    for contour in contours:
        area = abs(cv2.contourArea(contour))
        perimeter = cv2.arcLength(contour, True)
        if area > 4 and perimeter > 0:
            values.append(4*np.pi*area/(perimeter*perimeter))
    return float(np.mean(values)) if values else 0.0

def evaluate_candidate(name, binary, art_type="logo"):
    coverage = float(np.count_nonzero(binary) / binary.size)
    contours, hierarchy = cv2.findContours(
        binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    meaningful = [
        c for c in contours if abs(cv2.contourArea(c)) >= 8
    ]
    components = len(meaningful)
    holes = 0
    if hierarchy is not None:
        holes = int(sum(1 for row in hierarchy[0] if row[3] != -1))

    border = _border_noise(binary)
    compact = _compactness(meaningful)

    if coverage < 0.001 or coverage > 0.72:
        score = -1e9
    else:
        target = 0.17 if art_type == "logo" else 0.10
        score = 100.0
        score -= abs(coverage - target) * 190
        score -= border * 85
        score += min(components, 120) * 0.05
        score += min(holes, 80) * 0.08
        score += compact * 3.0

        if art_type == "logo":
            if components > 180:
                score -= (components - 180) * 0.08
            if holes > 120:
                score -= (holes - 120) * 0.05

    return VisionCandidate(
        name=name,
        binary=binary,
        score=float(score),
        coverage=coverage,
        components=components,
        holes=holes,
        border_noise=border,
        compactness=compact,
    )

def rank_candidates(image, art_type="logo"):
    ranked = [
        evaluate_candidate(name, binary, art_type)
        for name, binary in build_candidates(image)
    ]
    return sorted(ranked, key=lambda item: item.score, reverse=True)
