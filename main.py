import cv2
import os
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QFileDialog, QMessageBox, QLineEdit, 
                             QWidget, QCheckBox)
from PyQt6.QtCore import Qt
from PIL import Image
import datetime
import os

class VideoConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image to Video Converter")
        self.setGeometry(100, 100, 600, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        input_layout = QHBoxLayout()
        input_label = QLabel("Input Folder:")
        self.input_folder_path = QLineEdit()
        input_browse_btn = QPushButton("Browse")
        input_browse_btn.clicked.connect(self.browse_input_folder)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_folder_path)
        input_layout.addWidget(input_browse_btn)
        main_layout.addLayout(input_layout)

        output_layout = QHBoxLayout()
        output_label = QLabel("Output Folder:")
        self.output_folder_path = QLineEdit()
        output_browse_btn = QPushButton("Browse")
        output_browse_btn.clicked.connect(self.browse_output_folder)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_folder_path)
        output_layout.addWidget(output_browse_btn)
        main_layout.addLayout(output_layout)

        fps_layout = QHBoxLayout()
        fps_label = QLabel("FPS:")
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["5", "15", "30", "60", "Custom"])
        self.fps_combo.currentTextChanged.connect(self.toggle_custom_fps)
        self.custom_fps_input = QLineEdit()
        self.custom_fps_input.setPlaceholderText("Enter custom FPS")
        self.custom_fps_input.setVisible(False)
        fps_layout.addWidget(fps_label)
        fps_layout.addWidget(self.fps_combo)
        fps_layout.addWidget(self.custom_fps_input)
        main_layout.addLayout(fps_layout)

        resolution_layout = QHBoxLayout()
        resolution_label = QLabel("Resolution:")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["1080x720", "1920x1080", "Custom"])
        self.resolution_combo.currentTextChanged.connect(self.toggle_custom_resolution)
        self.custom_width_input = QLineEdit()
        self.custom_width_input.setPlaceholderText("Width")
        self.custom_width_input.setVisible(False)
        self.custom_height_input = QLineEdit()
        self.custom_height_input.setPlaceholderText("Height")
        self.custom_height_input.setVisible(False)
        resolution_layout.addWidget(resolution_label)
        resolution_layout.addWidget(self.resolution_combo)
        resolution_layout.addWidget(self.custom_width_input)
        resolution_layout.addWidget(self.custom_height_input)
        main_layout.addLayout(resolution_layout)

        sort_layout = QHBoxLayout()
        sort_label = QLabel("Sort Images By:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name", "Date", "Size", "Resolution"])
        self.order_checkbox = QCheckBox("Descending")
        sort_layout.addWidget(sort_label)
        sort_layout.addWidget(self.sort_combo)
        sort_layout.addWidget(self.order_checkbox)
        main_layout.addLayout(sort_layout)

        convert_btn = QPushButton("Convert to Video")
        convert_btn.clicked.connect(self.convert_to_video)
        main_layout.addWidget(convert_btn)

    def browse_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        self.input_folder_path.setText(folder)

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        self.output_folder_path.setText(folder)

    def toggle_custom_fps(self):
        self.custom_fps_input.setVisible(self.fps_combo.currentText() == "Custom")

    def toggle_custom_resolution(self):
        is_custom = self.resolution_combo.currentText() == "Custom"
        self.custom_width_input.setVisible(is_custom)
        self.custom_height_input.setVisible(is_custom)

    def get_fps(self):
        fps_text = self.fps_combo.currentText()
        if fps_text == "Custom":
            try:
                return int(self.custom_fps_input.text())
            except ValueError:
                QMessageBox.warning(self, "Invalid FPS", "Please enter a valid FPS number.")
                return None
        return int(fps_text)

    def get_resolution(self):
        resolution_text = self.resolution_combo.currentText()
        if resolution_text == "Custom":
            try:
                width = int(self.custom_width_input.text())
                height = int(self.custom_height_input.text())
                return (width, height)
            except ValueError:
                QMessageBox.warning(self, "Invalid Resolution", "Please enter valid width and height.")
                return None
        
        if resolution_text == "1080x720":
            return (1080, 720)
        return (1920, 1080)

    def sort_images(self, images):
        method = self.sort_combo.currentText()
        reverse = self.order_checkbox.isChecked()
        
        if method == "Name":
            return sorted(images, reverse=reverse)
        
        if method == "Date":
            return sorted(images, key=lambda x: os.path.getctime(x), reverse=reverse)
        
        if method == "Size":
            return sorted(images, key=lambda x: os.path.getsize(x), reverse=reverse)
        
        if method == "Resolution":
            return sorted(images, key=lambda x: Image.open(x).size[0] * Image.open(x).size[1], reverse=reverse)

    def convert_to_video(self):
        input_folder = self.input_folder_path.text()
        output_folder = self.output_folder_path.text()
        
        if not input_folder or not output_folder:
            QMessageBox.warning(self, "Folder Error", "Please select input and output folders.")
            return

        fps = self.get_fps()
        resolution = self.get_resolution()
        
        if fps is None or resolution is None:
            return

        supported_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']
        images = [
            os.path.join(input_folder, img) for img in os.listdir(input_folder) 
            if any(img.lower().endswith(ext) for ext in supported_extensions)
        ]

        if not images:
            QMessageBox.warning(self, "No Images", "No supported images found in the input folder.")
            return

        images = self.sort_images(images)
        video_path = os.path.join(output_folder, 'output_video.mp4')

        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video = cv2.VideoWriter(video_path, fourcc, fps, resolution)

            for image_path in images:
                img = cv2.imread(image_path)
                if img is None:
                    print(f"Warning: Could not read image {image_path}")
                    continue

                resized_img = cv2.resize(img, resolution)
                video.write(resized_img)

            video.release()
            QMessageBox.information(self, "Success", f"Video created successfully at {video_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = VideoConverterApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()