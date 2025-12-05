import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLineEdit
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from utils.image_utils import *
from utils.pcb_utils import *

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PCB Viewer")
        self.resize(1000, 600)

        # Zustand: Fiducials angezeigt oder nicht?
        self.sens_fiducials_shown = False
        self.dut_fiducials_shown = False

        # Hauptlayout → horizontal
        main_layout = QHBoxLayout(self)

        # Linker Bereich: Bild
        img_layout = QVBoxLayout()
        main_layout.addLayout(img_layout, stretch=4)

        # Rechter Bereich: Buttons
        control_layout = QVBoxLayout()
        control_layout.addStretch(1)
        main_layout.addLayout(control_layout, stretch=1)

        # === Bildlabel ===
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_layout.addWidget(self.image_label)

        # === Button rechts ===
        self.btn_toggle_sens_fiducials = QPushButton("Zeige Sensor Transform")
        self.btn_toggle_sens_fiducials.clicked.connect(self.toggle_sens_fiducials)
        control_layout.addWidget(self.btn_toggle_sens_fiducials)

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("PCB Pfad auswählen...")
        control_layout.addWidget(self.path_edit)

        # === Button rechts ===
        self.btn_toggle_dut_fiducials = QPushButton("Zeige DUT Transform")
        self.btn_toggle_dut_fiducials.clicked.connect(self.toggle_dut_fiducials)
        control_layout.addWidget(self.btn_toggle_dut_fiducials)

        control_layout.addStretch(4)

        # Bild laden
        self.image_path = "images/fid_test_3.png"
        self.original_image = cv2.imread(self.image_path)

        # Platzhalter für fiducial-Bild
        self.fiducial_image = None

        self.display_image(self.original_image)

    # ---------------------------------------------------------
    # Bildanzeige
    # ---------------------------------------------------------
    def display_image(self, cv_img):
        if cv_img is None:
            return

        img_rgb = cv_img.copy()
        img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB)

        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w

        qt_image = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        # skalieren
        pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.image_label.setPixmap(pixmap)

    # ---------------------------------------------------------
    # Button-Toggle
    # ---------------------------------------------------------
    def toggle_sens_fiducials(self):
        if not self.sens_fiducials_shown:
            # Fiducials anzeigen
            self.detect_sens_fiducials()
            self.btn_toggle_sens_fiducials.setText("Verberge Sensor Transform")
            self.sens_fiducials_shown = True
        else:
            # Originalbild wiederherstellen
            self.display_image(self.original_image)
            self.btn_toggle_sens_fiducials.setText("Zeige Sensor Transform")
            self.sens_fiducials_shown = False

    def toggle_dut_fiducials(self):
        if not self.dut_fiducials_shown:
            # Fiducials anzeigen
            self.detect_dut_fiducials()
            self.btn_toggle_dut_fiducials.setText("Verberge DUT Transform")
            self.dut_fiducials_shown = True
        else:
            # Originalbild wiederherstellen
            self.display_image(self.original_image)
            self.btn_toggle_dut_fiducials.setText("Zeige DUT Transform")
            self.dut_fiducials_shown = False

    # ---------------------------------------------------------
    # Fiducials erkennen (Template Matching Beispiel)
    # ---------------------------------------------------------
    def detect_dut_fiducials(self):
        if self.original_image is None:
            return

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Datei auswählen",
            "",
            "Alle Dateien (*.*)"  # optional Filter
        )

        if path:
            self.path_edit.setText(path)
            print("Ausgewählter Pfad:", path)

            image = self.original_image.copy()

            EXTERNAL_DIAMETER_DUT = 20
            INTERNAL_DIAMETER_DUT = 7

            EXTERNAL_COLOR = 100
            INTERNAL_COLOR = 240
            MAX_MATCHS = 3

            DUT_BOTTOM_DIST_MM = 38
            DUT_RIGHT_DIST_MM = 26

            # Find fiducial points in image

            pattern_dut = create_pattern(EXTERNAL_DIAMETER_DUT, INTERNAL_DIAMETER_DUT, EXTERNAL_COLOR, INTERNAL_COLOR)
            grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            match_img_dut = cv2.matchTemplate(grey_image, pattern_dut, cv2.TM_CCOEFF_NORMED)
            found_points_dut = find_points(match_img_dut, MAX_MATCHS)

            paint_matched_points(image, found_points_dut, EXTERNAL_DIAMETER_DUT, (255,0,0))

            segments = get_lines(path)
            fiducials = get_fiducials(path)

            draw_ltr(image, segments, found_points_dut, fiducials,
                     DUT_BOTTOM_DIST_MM, DUT_RIGHT_DIST_MM, EXTERNAL_DIAMETER_DUT)

            # Zwischenergebnis speichern
            self.fiducial_image = image
            self.display_image(image)

    def detect_sens_fiducials(self):
        if self.original_image is None:
            return

        image = self.original_image.copy()

        EXTERNAL_DIAMETER_SENSOR = 40
        INTERNAL_DIAMETER_SENSOR = 20

        EXTERNAL_COLOR = 100
        INTERNAL_COLOR = 240
        MAX_MATCHS = 3

        SENSOR_BOTTOM_DIST_MM = 65
        SENSOR_LEFT_DIST_MM = 46

        # Find fiducial points in image

        pattern_sensor = create_pattern(EXTERNAL_DIAMETER_SENSOR, INTERNAL_DIAMETER_SENSOR, EXTERNAL_COLOR,
                                        INTERNAL_COLOR)
        grey_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        match_img_sensor = cv2.matchTemplate(grey_image, pattern_sensor, cv2.TM_CCOEFF_NORMED)
        found_points_sensor = find_points(match_img_sensor, MAX_MATCHS)

        paint_matched_points(image, found_points_sensor, EXTERNAL_DIAMETER_SENSOR, (0,0,255))

        draw_magsens_pos(image, found_points_sensor, SENSOR_BOTTOM_DIST_MM, SENSOR_LEFT_DIST_MM)

        # Zwischenergebnis speichern
        self.fiducial_image = image
        self.display_image(image)

    # ---------------------------------------------------------
    # Bild mitskalieren
    # ---------------------------------------------------------
    def resizeEvent(self, event):
        if self.sens_fiducials_shown and self.fiducial_image and self.dut_fiducials_shown is not None:
            self.display_image(self.fiducial_image)
        else:
            self.display_image(self.original_image)
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
