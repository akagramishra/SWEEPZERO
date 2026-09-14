import sys
import os
from PySide6.QtWidgets import QApplication



from window import MainWindow
from theme import APP_QSS, ui


if __name__ == '__main__':
    
    if os.name == 'nt':
        import ctypes
       
        myappid = 'sweepzero.qtapp.v1.0' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    

    app = QApplication(sys.argv)

    app.setApplicationName("SweepZero")

    # One global stylesheet + one default face for the whole app, so no panel
    # has to carry its own background or font rules.
    app.setStyle("Fusion")
    app.setFont(ui(13))
    app.setStyleSheet(APP_QSS)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
