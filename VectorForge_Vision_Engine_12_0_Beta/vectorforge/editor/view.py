from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QGraphicsView

class VectorView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setRenderHints(
            QPainter.Antialiasing |
            QPainter.SmoothPixmapTransform
        )
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(
            QGraphicsView.AnchorUnderMouse
        )

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1/1.15
            self.scale(factor, factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def fit_document(self):
        if self.scene():
            self.fitInView(
                self.scene().itemsBoundingRect(),
                Qt.KeepAspectRatio
            )
