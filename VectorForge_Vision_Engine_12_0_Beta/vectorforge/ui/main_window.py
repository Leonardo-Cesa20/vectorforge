import traceback
from pathlib import Path
import cv2

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction,QKeySequence
from PySide6.QtWidgets import (
    QMainWindow,QWidget,QFileDialog,QMessageBox,QDoubleSpinBox,
    QSpinBox,QCheckBox,QComboBox,QFormLayout,QVBoxLayout,
    QGroupBox,QTabWidget,QStatusBar,QLabel,QSplitter,
    QListWidget,QListWidgetItem,QToolBar,QTableWidget,
    QTableWidgetItem,QHeaderView
)

from vectorforge.core.models import Settings
from vectorforge.core.presets import PRESETS
from vectorforge.vision.pipeline import VisionPipeline
from vectorforge.editor.scene import VectorScene
from vectorforge.editor.view import VectorView
from vectorforge.exporters.svg import export_svg
from vectorforge.exporters.dxf import export_dxf
from .image_view import ImageView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VectorForge Vision Engine 12.0 Beta")
        self.resize(1720,980)

        self.pipeline = VisionPipeline()
        self.source_path = None
        self.document = None

        self.scene = VectorScene()
        self.vector_view = VectorView(self.scene)

        self._build_toolbar()
        self._build_ui()
        self._apply_preset("logo_clean")

    def _build_toolbar(self):
        toolbar = QToolBar("Principal")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        for text,handler in [
            ("Importar",self.import_image),
            ("Processar",self.process_image),
            ("Ajustar à tela",self.vector_view.fit_document),
            ("Excluir selecionados",self.scene.delete_selected),
            ("Exportar SVG",self.save_svg),
            ("Exportar DXF",self.save_dxf)
        ]:
            action = QAction(text,self)
            action.triggered.connect(handler)
            toolbar.addAction(action)

        delete_action = QAction(self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.scene.delete_selected)
        self.addAction(delete_action)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)

        splitter = QSplitter(Qt.Horizontal)
        outer.addWidget(splitter,1)

        left = QWidget()
        left.setMinimumWidth(450)
        left.setMaximumWidth(570)
        layout = QVBoxLayout(left)

        box = QGroupBox("Vision Engine")
        form = QFormLayout(box)

        self.preset = QComboBox()
        self.preset.addItem("Logo limpo", "logo_clean")
        self.preset.addItem("Logo com ruído", "logo_noisy")
        self.preset.addItem("Desenho técnico", "technical")
        self.preset.currentIndexChanged.connect(
            lambda: self._apply_preset(self.preset.currentData())
        )

        self.art_type = QComboBox()
        self.art_type.addItem("Logo / Ícone", "logo")
        self.art_type.addItem("Desenho técnico", "technical")

        self.profile = QComboBox()
        self.profile.addItem("Gravação", "engraving")
        self.profile.addItem("Corte", "cut")

        self.candidate = QComboBox()
        self.candidate.addItem("Automático", "auto")

        self.width = QDoubleSpinBox()
        self.width.setRange(1,600)
        self.width.setValue(100)
        self.width.setSuffix(" mm")

        self.min_area = QSpinBox()
        self.min_area.setRange(1,5000)

        self.denoise = QSpinBox()
        self.denoise.setRange(0,8)

        self.close = QSpinBox()
        self.close.setRange(0,8)

        self.simplify = QDoubleSpinBox()
        self.simplify.setRange(0.01,2.0)
        self.simplify.setSingleStep(0.01)

        self.max_nodes = QSpinBox()
        self.max_nodes.setRange(40,3000)

        self.edge_protection = QDoubleSpinBox()
        self.edge_protection.setRange(0.0,1.0)
        self.edge_protection.setSingleStep(0.05)

        self.crop = QCheckBox("Recortar automaticamente")
        self.crop.setChecked(True)

        self.holes = QCheckBox("Preservar furos internos")
        self.holes.setChecked(True)

        self.preserve_original = QCheckBox("Nunca substituir caminhos do logo")
        self.preserve_original.setChecked(True)

        self.remove_border = QCheckBox("Remover ruído encostado nas bordas")
        self.remove_border.setChecked(True)

        self.fill_holes = QCheckBox("Preencher pequenos buracos de ruído")
        self.fill_holes.setChecked(False)

        for label,widget in [
            ("Preset:",self.preset),
            ("Tipo de arte:",self.art_type),
            ("Perfil:",self.profile),
            ("Segmentação:",self.candidate),
            ("Largura final:",self.width),
            ("Área mínima:",self.min_area),
            ("Ruído:",self.denoise),
            ("Fechar falhas:",self.close),
            ("Simplificação:",self.simplify),
            ("Máximo de nós/caminho:",self.max_nodes),
            ("Proteção de bordas:",self.edge_protection),
        ]:
            form.addRow(label,widget)

        form.addRow(self.crop)
        form.addRow(self.holes)
        form.addRow(self.preserve_original)
        form.addRow(self.remove_border)
        form.addRow(self.fill_holes)
        layout.addWidget(box)

        candidates_box = QGroupBox("Diagnóstico das segmentações")
        candidates_layout = QVBoxLayout(candidates_box)
        self.candidate_table = QTableWidget(0,5)
        self.candidate_table.setHorizontalHeaderLabels(
            ["Método","Nota","Cobertura","Objetos","Ruído borda"]
        )
        self.candidate_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.candidate_table.setAlternatingRowColors(True)
        self.candidate_table.cellClicked.connect(
            self._candidate_clicked
        )
        candidates_layout.addWidget(self.candidate_table)
        layout.addWidget(candidates_box,1)

        layers_box = QGroupBox("Camadas")
        layers_layout = QVBoxLayout(layers_box)
        self.layers = QListWidget()
        self.layers.itemChanged.connect(self._layer_changed)
        layers_layout.addWidget(self.layers)
        layout.addWidget(layers_box)

        self.info = QLabel("Nenhuma imagem processada.")
        self.info.setWordWrap(True)
        layout.addWidget(self.info)

        splitter.addWidget(left)

        self.tabs = QTabWidget()
        self.original = ImageView("Importe uma imagem")
        self.normalized = ImageView("Imagem normalizada")
        self.binary = ImageView("Segmentação escolhida")
        self.preview = ImageView("Prévia vetorial")
        self.tabs.addTab(self.original,"Original")
        self.tabs.addTab(self.normalized,"Normalizada")
        self.tabs.addTab(self.binary,"Segmentação")
        self.tabs.addTab(self.preview,"Prévia")
        self.tabs.addTab(self.vector_view,"Editor vetorial")
        splitter.addWidget(self.tabs)
        splitter.setSizes([500,1220])

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Pronto.")

    def _apply_preset(self,preset_name):
        if preset_name not in PRESETS:
            return

        preset = PRESETS[preset_name]

        def select_data(combo,value):
            index = combo.findData(value)
            if index >= 0:
                combo.setCurrentIndex(index)

        select_data(self.art_type,preset["art_type"])
        select_data(self.profile,preset["profile"])
        self.min_area.setValue(preset["min_area"])
        self.denoise.setValue(preset["denoise"])
        self.close.setValue(preset["close_gaps"])
        self.simplify.setValue(preset["simplify"])
        self.holes.setChecked(preset["preserve_holes"])
        self.preserve_original.setChecked(
            preset["preserve_original_paths"]
        )
        self.max_nodes.setValue(preset["max_nodes_per_path"])
        self.remove_border.setChecked(
            preset["remove_border_noise"]
        )
        self.fill_holes.setChecked(
            preset["fill_small_holes"]
        )
        self.edge_protection.setValue(
            preset["edge_protection"]
        )

    def settings(self):
        return Settings(
            art_type=self.art_type.currentData(),
            profile=self.profile.currentData(),
            width_mm=self.width.value(),
            min_area=self.min_area.value(),
            denoise=self.denoise.value(),
            close_gaps=self.close.value(),
            simplify=self.simplify.value(),
            auto_crop=self.crop.isChecked(),
            preserve_holes=self.holes.isChecked(),
            preserve_original_paths=self.preserve_original.isChecked(),
            max_nodes_per_path=self.max_nodes.value(),
            candidate_mode=self.candidate.currentData(),
            remove_border_noise=self.remove_border.isChecked(),
            fill_small_holes=self.fill_holes.isChecked(),
            edge_protection=self.edge_protection.value(),
        )

    def import_image(self):
        path,_ = QFileDialog.getOpenFileName(
            self,"Selecionar imagem","",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.webp)"
        )

        if not path:
            return

        image = cv2.imread(path)

        if image is None:
            QMessageBox.critical(self,"Erro","Imagem inválida.")
            return

        self.source_path = Path(path)
        self.document = None
        self.original.set_image(image)
        self.tabs.setCurrentWidget(self.original)
        self.status.showMessage(f"Imagem: {self.source_path.name}")

    def process_image(self):
        if not self.source_path:
            QMessageBox.warning(
                self,"Atenção","Importe uma imagem primeiro."
            )
            return

        try:
            self.status.showMessage("Analisando segmentações...")
            self.document = self.pipeline.process(
                str(self.source_path),
                self.settings()
            )

            self.normalized.set_image(
                self.document.normalized_bgr
            )
            self.binary.set_image(
                self.document.binary
            )
            self.preview.set_image(
                self.document.preview_bgr
            )
            self.scene.load_document(
                self.document
            )
            self.vector_view.fit_document()
            self.tabs.setCurrentWidget(self.preview)

            self._update_candidates()
            self._update_layers()

            d = self.document.diagnostics
            self.info.setText(
                f"Segmentação escolhida: {d['selected_candidate']}\n"
                f"Nota: {d['candidate_score']}\n"
                f"Cobertura: {d['coverage']}\n"
                f"Objetos: {d['components']}\n"
                f"Ruído nas bordas: {d['border_noise']}\n"
                f"Formas vetoriais: {d['shapes']}\n"
                f"Furos: {d['holes']}\n"
                f"Nós: {d['nodes']}"
            )

            self.status.showMessage("Processamento concluído.")

        except Exception as error:
            Path("vectorforge_error.log").write_text(
                traceback.format_exc(),
                encoding="utf-8"
            )
            QMessageBox.critical(
                self,"Erro",
                f"{error}\n\nDetalhes em vectorforge_error.log."
            )

    def _update_candidates(self):
        self.candidate.blockSignals(True)
        current = self.candidate.currentData()
        self.candidate.clear()
        self.candidate.addItem("Automático","auto")

        for candidate in self.document.candidates:
            self.candidate.addItem(
                candidate.name,
                candidate.name
            )

        index = self.candidate.findData(current)
        self.candidate.setCurrentIndex(
            index if index >= 0 else 0
        )
        self.candidate.blockSignals(False)

        self.candidate_table.setRowCount(
            len(self.document.candidates)
        )

        for row,candidate in enumerate(self.document.candidates):
            values = [
                candidate.name,
                f"{candidate.score:.2f}",
                f"{candidate.coverage:.3f}",
                str(candidate.components),
                f"{candidate.border_noise:.3f}",
            ]

            for col,value in enumerate(values):
                self.candidate_table.setItem(
                    row,col,QTableWidgetItem(value)
                )

    def _candidate_clicked(self,row,column):
        if not self.document:
            return

        if row < 0 or row >= len(self.document.candidates):
            return

        name = self.document.candidates[row].name
        index = self.candidate.findData(name)

        if index >= 0:
            self.candidate.setCurrentIndex(index)
            self.process_image()

    def _update_layers(self):
        self.layers.blockSignals(True)
        self.layers.clear()

        for layer in sorted({
            shape.layer
            for shape in self.document.shapes
        }):
            item = QListWidgetItem(layer)
            item.setFlags(
                item.flags() | Qt.ItemIsUserCheckable
            )
            item.setCheckState(Qt.Checked)
            self.layers.addItem(item)

        self.layers.blockSignals(False)

    def _layer_changed(self,item):
        self.scene.set_layer_visible(
            item.text(),
            item.checkState() == Qt.Checked
        )

    def save_svg(self):
        if not self.document:
            return

        path,_ = QFileDialog.getSaveFileName(
            self,"Salvar SVG","","SVG (*.svg)"
        )

        if path:
            export_svg(
                path if path.lower().endswith(".svg") else path+".svg",
                self.scene.export_geometry(),
                self.width.value()
            )
            QMessageBox.information(
                self,"Concluído","SVG exportado."
            )

    def save_dxf(self):
        if not self.document:
            return

        path,_ = QFileDialog.getSaveFileName(
            self,"Salvar DXF","","DXF (*.dxf)"
        )

        if path:
            export_dxf(
                path if path.lower().endswith(".dxf") else path+".dxf",
                self.scene.export_geometry(),
                self.width.value()
            )
            QMessageBox.information(
                self,"Concluído","DXF exportado."
            )
