import cv2

from vectorforge.core.models import Document
from vectorforge.vision.normalize import auto_crop, normalize_image
from vectorforge.vision.candidates import rank_candidates
from vectorforge.vision.reconstruct import reconstruct
from vectorforge.vector.contours import vectorize
from vectorforge.vector.geometry import optimize

class VisionPipeline:
    def process(self, path, settings):
        original = cv2.imread(path, cv2.IMREAD_COLOR)
        if original is None:
            raise ValueError("Não foi possível abrir a imagem.")

        if settings.auto_crop:
            work, crop_rect = auto_crop(original)
        else:
            work = original.copy()
            crop_rect = (0,0,original.shape[1],original.shape[0])

        normalized = normalize_image(
            work,
            denoise=settings.denoise,
            edge_protection=settings.edge_protection,
        )

        candidates = rank_candidates(
            normalized,
            art_type=settings.art_type,
        )

        if not candidates:
            raise ValueError("Nenhuma segmentação válida foi gerada.")

        if settings.candidate_mode == "auto":
            selected = candidates[0]
        else:
            selected = next(
                (candidate for candidate in candidates
                 if candidate.name == settings.candidate_mode),
                candidates[0]
            )

        binary = reconstruct(selected.binary, settings)
        shapes = vectorize(binary, settings)
        shapes = optimize(shapes, settings)

        preview = render_preview(work.shape, shapes)

        diagnostics = {
            "art_type": settings.art_type,
            "profile": settings.profile,
            "selected_candidate": selected.name,
            "candidate_score": round(selected.score, 3),
            "coverage": round(selected.coverage, 4),
            "components": int(selected.components),
            "holes_detected": int(selected.holes),
            "border_noise": round(selected.border_noise, 4),
            "shapes": int(len(shapes)),
            "holes": int(sum(bool(shape.hole) for shape in shapes)),
            "nodes": int(sum(
                len(shape.points) if shape.points is not None else 1
                for shape in shapes
            )),
            "crop_rect": crop_rect,
        }

        h, w = binary.shape

        return Document(
            image_size=(w,h),
            original_bgr=work,
            normalized_bgr=normalized,
            binary=binary,
            preview_bgr=preview,
            candidates=candidates,
            shapes=shapes,
            diagnostics=diagnostics,
        )

def render_preview(shape, shapes):
    import numpy as np

    preview = np.full(shape, 255, dtype=np.uint8)

    for vector in shapes:
        if vector.kind == "circle":
            center = tuple(int(round(v)) for v in vector.center)
            cv2.circle(
                preview,
                center,
                int(round(vector.radius)),
                (0,0,0),
                1,
                cv2.LINE_AA
            )
        elif vector.points is not None and len(vector.points) >= 2:
            points = vector.points.astype("int32").reshape(-1,1,2)
            cv2.polylines(
                preview,
                [points],
                vector.closed,
                (0,0,0),
                1,
                cv2.LINE_AA
            )

    return preview
