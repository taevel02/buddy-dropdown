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
    QPushButton,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMarginsF
from PyQt6.QtGui import QTextDocument, QPageSize, QPageLayout
from PyQt6.QtPrintSupport import QPrinter
import markdown
from markitdown import MarkItDown


class ConversionWorker(QThread):
    progress_updated = pyqtSignal(int, int, str)  # current, total, filename
    finished = pyqtSignal(int)  # total processed
    error_occurred = pyqtSignal(str, str)  # filename, error message

    def __init__(self, file_paths, mode=0):
        super().__init__()
        self.file_paths = file_paths
        self.mode = mode
        self.markitdown = MarkItDown()

    def run(self):
        total_files = len(self.file_paths)
        for i, file_path in enumerate(self.file_paths):
            try:
                filename = os.path.basename(file_path)
                # Notify progress start for this file
                self.progress_updated.emit(i + 1, total_files, filename)

                if self.mode == 0:
                    # Convert PDF to MD using markitdown
                    result = self.markitdown.convert(file_path)

                    # Save MD file
                    md_path = Path(file_path).with_suffix(".md")
                    with open(md_path, "w", encoding="utf-8") as f:
                        f.write(result.text_content)
                else:
                    # Convert MD to PDF using markdown and QTextDocument
                    pdf_path = Path(file_path).with_suffix(".pdf")
                    with open(file_path, "r", encoding="utf-8") as f:
                        md_text = f.read()

                    html_content = markdown.markdown(
                        md_text, extensions=["tables", "fenced_code", "nl2br"]
                    )
                    html_doc = f"""
                    <html>
                    <head>
                    <style>
                        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; font-size: 11pt; }}
                        h1 {{ font-size: 16pt; margin-bottom: 12pt; }}
                        h2 {{ font-size: 14pt; margin-bottom: 10pt; }}
                        h3 {{ font-size: 12pt; margin-bottom: 8pt; }}
                        h4, h5, h6 {{ font-size: 11pt; margin-bottom: 6pt; font-weight: bold; }}
                        table {{ border-collapse: collapse; width: 100%; margin-bottom: 1rem; }}
                        th, td {{ border: 1px solid #ddd; padding: 6px; font-size: 10pt; }}
                        th {{ padding-top: 10px; padding-bottom: 10px; text-align: left; background-color: #f2f2f2; }}
                        pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; font-size: 10pt; }}
                        code {{ font-family: monospace; background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; font-size: 10pt; }}
                        blockquote {{ border-left: 4px solid #ddd; margin: 0; padding-left: 10px; color: #666; }}
                    </style>
                    </head>
                    <body>
                    {html_content}
                    </body>
                    </html>
                    """
                    doc = QTextDocument()
                    doc.setHtml(html_doc)
                    
                    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                    printer.setOutputFileName(str(pdf_path))
                    
                    # Set A4 size and margins
                    page_layout = printer.pageLayout()
                    page_layout.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
                    page_layout.setMargins(QMarginsF(15, 15, 15, 15)) # 15mm margins
                    printer.setPageLayout(page_layout)
                    
                    doc.print(printer)

            except Exception as e:
                self.error_occurred.emit(os.path.basename(file_path), str(e))

        self.finished.emit(total_files)


class DropZone(QLabel):
    files_dropped = pyqtSignal(list)

    def __init__(self):
        super().__init__("Drag & Drop .pdf")
        self.current_mode = 0
        self.setMinimumWidth(300)
        self.setMinimumHeight(200)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.default_style = """
            QLabel {
                border: 2px dashed #d2d2d7;
                border-radius: 16px;
                font-size: 18px;
                font-weight: 600;
                color: #86868b;
                background-color: #fafafa;
            }
            QLabel:hover {
                border: 2px dashed #1d1d1f;
                background-color: #f5f5f7;
                color: #1d1d1f;
            }
        """
        self.hover_style = """
            QLabel {
                border: 2px dashed #1d1d1f;
                border-radius: 16px;
                font-size: 18px;
                font-weight: 600;
                color: #1d1d1f;
                background-color: #f5f5f7;
            }
        """
        self.setStyleSheet(self.default_style)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_mode(self, mode):
        self.current_mode = mode
        if mode == 0:
            self.setText("Drag & Drop .pdf")
        else:
            self.setText("Drag & Drop .md")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            from PyQt6.QtWidgets import QFileDialog

            if self.current_mode == 0:
                filter_str = ".pdf Files (*.pdf)"
            else:
                filter_str = ".md Files (*.md *.markdown)"

            files, _ = QFileDialog.getOpenFileNames(
                self, "Select Files", "", filter_str
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

        # Mode Toggle Container
        self.toggle_container = QWidget()
        self.toggle_layout = QHBoxLayout()
        self.toggle_layout.setContentsMargins(0, 0, 0, 0)
        self.toggle_layout.setSpacing(0)
        self.toggle_container.setLayout(self.toggle_layout)

        self.btn_pdf_to_md = QPushButton(".pdf ➔ .md")
        self.btn_md_to_pdf = QPushButton(".md ➔ .pdf")

        self.btn_pdf_to_md.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_md_to_pdf.setCursor(Qt.CursorShape.PointingHandCursor)

        active_style_left = """
            QPushButton {
                background-color: #1d1d1f;
                color: white;
                font-size: 15px;
                font-weight: 600;
                padding: 10px 16px;
                border: 1px solid #1d1d1f;
                border-top-left-radius: 8px;
                border-bottom-left-radius: 8px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
            }
        """
        inactive_style_left = """
            QPushButton {
                background-color: #ffffff;
                color: #1d1d1f;
                font-size: 15px;
                font-weight: 600;
                padding: 10px 16px;
                border: 1px solid #d2d2d7;
                border-top-left-radius: 8px;
                border-bottom-left-radius: 8px;
                border-top-right-radius: 0px;
                border-bottom-right-radius: 0px;
            }
            QPushButton:hover {
                background-color: #f5f5f7;
            }
        """
        active_style_right = """
            QPushButton {
                background-color: #1d1d1f;
                color: white;
                font-size: 15px;
                font-weight: 600;
                padding: 10px 16px;
                border: 1px solid #1d1d1f;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """
        inactive_style_right = """
            QPushButton {
                background-color: #ffffff;
                color: #1d1d1f;
                font-size: 15px;
                font-weight: 600;
                padding: 10px 16px;
                border: 1px solid #d2d2d7;
                border-left: none;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            QPushButton:hover {
                background-color: #f5f5f7;
            }
        """

        self.btn_pdf_to_md.setStyleSheet(active_style_left)
        self.btn_md_to_pdf.setStyleSheet(inactive_style_right)

        self.btn_pdf_to_md.clicked.connect(lambda: self.set_mode(0))
        self.btn_md_to_pdf.clicked.connect(lambda: self.set_mode(1))

        # Store styles for later toggling
        self.styles = {
            "active_left": active_style_left,
            "inactive_left": inactive_style_left,
            "active_right": active_style_right,
            "inactive_right": inactive_style_right,
        }

        self.toggle_layout.addWidget(self.btn_pdf_to_md)
        self.toggle_layout.addWidget(self.btn_md_to_pdf)

        self.card_layout.addWidget(
            self.toggle_container, alignment=Qt.AlignmentFlag.AlignCenter
        )

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

    def set_mode(self, mode_index):
        if mode_index == 0:
            self.btn_pdf_to_md.setStyleSheet(self.styles["active_left"])
            self.btn_md_to_pdf.setStyleSheet(self.styles["inactive_right"])
        else:
            self.btn_pdf_to_md.setStyleSheet(self.styles["inactive_left"])
            self.btn_md_to_pdf.setStyleSheet(self.styles["active_right"])

        self.drop_zone.set_mode(mode_index)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if self.drop_zone.current_mode == 0:
                valid = any(url.toLocalFile().lower().endswith(".pdf") for url in urls)
            else:
                valid = any(
                    url.toLocalFile().lower().endswith((".md", ".markdown"))
                    for url in urls
                )

            if valid:
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
            if self.drop_zone.current_mode == 0:
                if file_path.lower().endswith(".pdf"):
                    files.append(file_path)
            else:
                if file_path.lower().endswith((".md", ".markdown")):
                    files.append(file_path)

        if files:
            self.start_conversion(files)

    def start_conversion(self, files):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(
                self, "Busy", "A conversion process is already running."
            )
            return

        self.worker = ConversionWorker(files, self.drop_zone.current_mode)
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
        mode = self.drop_zone.current_mode
        ext = ".md" if mode == 0 else ".pdf"
        QMessageBox.information(
            self,
            "Success",
            f"Successfully converted {total_files} file(s) to {ext}.",
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
