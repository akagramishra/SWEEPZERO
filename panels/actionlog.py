from PySide6.QtWidgets import QWidget, QVBoxLayout

from theme import framed


class ActionLogPanel(QWidget):
    def __init__(self, title="Action Log"):
        super().__init__()

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(2)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(framed(self.content, title))
