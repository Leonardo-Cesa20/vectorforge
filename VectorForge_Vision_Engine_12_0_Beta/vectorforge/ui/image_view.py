from PySide6.QtCore import Qt
from PySide6.QtGui import QImage,QPixmap
from PySide6.QtWidgets import QLabel,QScrollArea
import cv2
import numpy as np

class ImageView(QScrollArea):
    def __init__(self,text):
        super().__init__()
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background:#f5f5f5;color:#777")
        self.setWidget(self.label)
        self.setWidgetResizable(True)
        self.pixmap = None

    def set_image(self,image):
        array = np.asarray(image)

        if array.ndim == 2:
            array = np.ascontiguousarray(array)
            h,w = array.shape
            qimage = QImage(
                array.data,w,h,array.strides[0],
                QImage.Format_Grayscale8
            ).copy()
        else:
            rgb = np.ascontiguousarray(
                cv2.cvtColor(array,cv2.COLOR_BGR2RGB)
            )
            h,w,_ = rgb.shape
            qimage = QImage(
                rgb.data,w,h,rgb.strides[0],
                QImage.Format_RGB888
            ).copy()

        self.pixmap = QPixmap.fromImage(qimage)
        self.refresh()

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self.refresh()

    def refresh(self):
        if self.pixmap is not None:
            self.label.setPixmap(
                self.pixmap.scaled(
                    self.viewport().size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )
