from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainterPath, QPen, QBrush
from PySide6.QtWidgets import (
    QGraphicsScene, QGraphicsItem,
    QGraphicsEllipseItem, QGraphicsPathItem
)

FLAGS = (
    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
    QGraphicsItem.GraphicsItemFlag.ItemIsMovable
)

class VectorScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.layer_items = {}

    def load_document(self, document):
        self.clear()
        self.layer_items = {}

        for index, shape in enumerate(document.shapes):
            item = self._create_item(shape)
            if item is None:
                continue

            item.vector_index = index
            item.vector_kind = shape.kind
            item.vector_layer = shape.layer
            item.setFlags(FLAGS)
            item.setPen(QPen(Qt.GlobalColor.black, 1.0))
            item.setBrush(QBrush(Qt.BrushStyle.NoBrush))

            self.addItem(item)
            self.layer_items.setdefault(
                shape.layer, []
            ).append(item)

        bounds = self.itemsBoundingRect()
        if not bounds.isNull():
            self.setSceneRect(
                bounds.adjusted(-20,-20,20,20)
            )

    def _create_item(self, shape):
        if shape.kind == "circle":
            return QGraphicsEllipseItem(
                shape.center[0]-shape.radius,
                shape.center[1]-shape.radius,
                shape.radius*2,
                shape.radius*2
            )

        if shape.points is None or len(shape.points) == 0:
            return None

        path = QPainterPath()
        path.moveTo(
            float(shape.points[0][0]),
            float(shape.points[0][1])
        )

        for x, y in shape.points[1:]:
            path.lineTo(float(x), float(y))

        if shape.closed:
            path.closeSubpath()

        return QGraphicsPathItem(path)

    def delete_selected(self):
        for item in list(self.selectedItems()):
            self.removeItem(item)

    def set_layer_visible(self, layer, visible):
        for item in self.layer_items.get(layer, []):
            item.setVisible(visible)

    def export_geometry(self):
        geometry = []

        for item in self.items():
            if not item.isVisible():
                continue

            layer = getattr(item, "vector_layer", "VECTOR")
            transform = item.sceneTransform()

            if isinstance(item, QGraphicsEllipseItem):
                rect = item.rect()
                center = transform.map(rect.center())
                edge = transform.map(QPointF(
                    rect.center().x()+rect.width()/2,
                    rect.center().y()
                ))
                radius = (
                    (edge.x()-center.x())**2 +
                    (edge.y()-center.y())**2
                ) ** 0.5

                geometry.append({
                    "kind":"circle",
                    "layer":layer,
                    "center":(center.x(),center.y()),
                    "radius":radius,
                    "closed":True,
                })
                continue

            if isinstance(item, QGraphicsPathItem):
                path = item.path()
                points = []

                for index in range(path.elementCount()):
                    element = path.elementAt(index)
                    point = transform.map(
                        QPointF(element.x, element.y)
                    )
                    points.append((point.x(),point.y()))

                geometry.append({
                    "kind":"path",
                    "layer":layer,
                    "points":points,
                    "closed":True,
                })

        return geometry
