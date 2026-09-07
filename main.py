import sys
import os
from PySide6.QtWidgets import QApplication

from window import MainWindow


if __name__ == '__main__':
    
    if os.name == 'nt': #xclusive for windows os
        import ctypes
       
        myappid = 'sweepzero.qtapp.v1.0' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
