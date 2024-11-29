import sys
from PyQt5.QtWidgets import QApplication
from app.ui.windows import MainWindow  

def create_main_window():
    app = QApplication(sys.argv)
    # Set taskbar icon for Windows specifically
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("TradingWithPy")  # Replace with a unique app ID
        
    window = MainWindow()
    window.show()


    sys.exit(app.exec_())


if __name__ == "__main__":
    create_main_window()