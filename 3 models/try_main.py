import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QFont

class ModelLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the UI with buttons and layout."""
        layout = QVBoxLayout()

        # Title Label
        title_label = QLabel("Model Launcher")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title_label)

        # Model Buttons with specified paths
        self.add_model_button(layout, "Model 1", r'C:\Users\shail\Downloads\Vizieye-main\Vizieye-main\DNN Project(1)\mainProject\final1.py')
        self.add_model_button(layout, "Model 2", r'C:\Users\shail\Downloads\Vizieye-main\Vizieye-main\DNN Project(1)\mainProject\final2.py')
        self.add_model_button(layout, "Model 3", r'C:\Users\shail\Downloads\Vizieye-main\Vizieye-main\DNN Project(1)\mainProject\final3.py')

        self.setLayout(layout)
        self.setWindowTitle("Model Launcher")
        self.setGeometry(400, 200, 400, 300)

    def add_model_button(self, layout, name, filepath):
        """Create a button and add it to the layout."""
        button = QPushButton(name)
        button.setFont(QFont("Arial", 12))
        button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button.clicked.connect(lambda: self.run_model(filepath))
        layout.addWidget(button)

    def run_model(self, filepath):
        """Launch the model in a new terminal window."""
        try:
            # Launch model in a new terminal window
            subprocess.Popen(f"start cmd /k python \"{filepath}\"", shell=True)
        except Exception as e:
            print(f"Failed to start model: {e}")

def main():
    app = QApplication(sys.argv)
    launcher = ModelLauncher()
    launcher.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
