import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QProgressBar,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from markitdown import MarkItDown


class ConversionWorker(QThread):
    progress_updated = pyqtSignal(int, int, str)  # current, total, filename
    finished = pyqtSignal(int)  # total processed
    error_occurred = pyqtSignal(str, str)  # filename, error message

    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths
        self.markitdown = MarkItDown()

    def run(self):
        total_files = len(self.file_paths)
        for i, file_path in enumerate(self.file_paths):
            try:
                filename = os.path.basename(file_path)
                # Notify progress start for this file
                self.progress_updated.emit(i + 1, total_files, filename)

                # Convert PDF to MD using markitdown
                result = self.markitdown.convert(file_path)

                # Save MD file
                md_path = Path(file_path).with_suffix(".md")
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(result.text_content)

            except Exception as e:
                self.error_occurred.emit(os.path.basename(file_path), str(e))

        self.finished.emit(total_files)


class DropZone(QLabel):
    files_dropped = pyqtSignal(list)

    def __init__(self):
        super().__init__("Drag & Drop PDFs Here")
        self.setMinimumWidth(300)
        self.setMinimumHeight(200)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.default_style = """
            QLabel {
                border: 2px dashed #d2d2d7;
                border-radius: 16px;
                font-size: 16px;
                font-weight: 500;
                color: #86868b;
                background-color: #fafafa;
            }
            QLabel:hover {
                border: 2px dashed #007aff;
                background-color: #f0f8ff;
                color: #007aff;
            }
        """
        self.hover_style = """
            QLabel {
                border: 2px dashed #007aff;
                border-radius: 16px;
                font-size: 16px;
                font-weight: 500;
                color: #007aff;
                background-color: #e6f2ff;
            }
        """
        self.setStyleSheet(self.default_style)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            from PyQt6.QtWidgets import QFileDialog

            files, _ = QFileDialog.getOpenFileNames(
                self, "Select PDF Files", "", "PDF Files (*.pdf)"
            )
            if files:
                self.files_dropped.emit(files)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dropdown")
        self.setMinimumSize(450, 420)
        self.setAcceptDrops(True)

        # Apply general font and clean white background
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #f5f5f7;
            }
            QWidget {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }
        """
        )

        # Setup Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main Layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.central_widget.setLayout(self.main_layout)

        # Card Widget
        self.card = QWidget()
        self.card.setObjectName("Card")
        self.card.setStyleSheet(
            """
            QWidget#Card {
                background-color: #ffffff;
                border: 1px solid #e5e5ea;
                border-radius: 20px;
            }
        """
        )
        self.card_layout = QVBoxLayout()
        self.card_layout.setContentsMargins(30, 30, 30, 30)
        self.card_layout.setSpacing(15)
        self.card.setLayout(self.card_layout)
        self.main_layout.addWidget(self.card)

        # Header Title
        self.title_label = QLabel("PDF to Markdown")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(
            """
            color: #1d1d1f; 
            font-size: 26px; 
            font-weight: 800; 
            background: transparent;
            border: none;
        """
        )
        self.card_layout.addWidget(self.title_label)

        # Subtitle
        self.subtitle_label = QLabel(
            "Drop your documents below to magically convert them"
        )
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet(
            """
            color: #86868b; 
            font-size: 13px; 
            font-weight: 500;
            background: transparent;
            border: none;
        """
        )
        self.card_layout.addWidget(self.subtitle_label)

        # Drop Zone
        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self.start_conversion)
        self.card_layout.addWidget(self.drop_zone)

        # Status Label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            """
            color: #1d1d1f; 
            font-size: 14px; 
            font-weight: 500; 
            margin-top: 10px;
            background: transparent;
            border: none;
        """
        )
        self.card_layout.addWidget(self.status_label)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #d2d2d7;
                border-radius: 6px;
                background-color: #f5f5f7;
            }
            QProgressBar::chunk {
                background-color: #007aff;
                border-radius: 5px;
            }
        """
        )
        self.card_layout.addWidget(self.progress_bar)

        self.worker = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(url.toLocalFile().lower().endswith(".pdf") for url in urls):
                event.accept()
                self.drop_zone.setStyleSheet(self.drop_zone.hover_style)
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.drop_zone.setStyleSheet(self.drop_zone.default_style)

    def dropEvent(self, event):
        self.drop_zone.setStyleSheet(self.drop_zone.default_style)
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(".pdf"):
                files.append(file_path)

        if files:
            self.start_conversion(files)

    def start_conversion(self, files):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(
                self, "Busy", "A conversion process is already running."
            )
            return

        self.worker = ConversionWorker(files)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.error_occurred.connect(self.show_error)

        self.progress_bar.setMaximum(len(files))
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Starting conversion of {len(files)} file(s)...")

        self.worker.start()

    def update_progress(self, current, total, filename):
        self.progress_bar.setValue(current - 1)
        self.status_label.setText(f"Converting {current}/{total}: {filename}...")

    def conversion_finished(self, total_files):
        self.progress_bar.setValue(total_files)
        self.status_label.setText("Conversion complete!")
        QMessageBox.information(
            self,
            "Success",
            f"Successfully converted {total_files} file(s) to Markdown.",
        )
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready")

    def show_error(self, filename, error_msg):
        QMessageBox.critical(
            self, "Error", f"Failed to convert {filename}:\\n{error_msg}"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
