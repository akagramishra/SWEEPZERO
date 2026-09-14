from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QFrame

from theme import framed, mono, INK, INK_DIM, INK_FAINT, CYAN, GREEN, AMBER


# kind -> colour of the marker and the message text
KINDS = {
    "new":   CYAN,     # band detected for the very first time
    "hit":   GREEN,    # detection on a band we have not locked yet
    "track": GREEN,    # detection on a band whose period we are predicting
    "lock":  AMBER,    # period just became trustworthy
    "info":  INK_DIM,
}

NBSP = "&#160;"


def _pad(text, width):
    """Pad to a fixed column width using non-breaking spaces, since HTML
    collapses ordinary runs of whitespace."""
    return text + NBSP * max(0, width - len(text))


class ActionLogPanel(QWidget):
    # older lines are dropped past this, so a long mission cannot grow forever
    MAX_LINES = 500

    def __init__(self, title="Action Log", subtitle=None):
        super().__init__()

        self.view = QPlainTextEdit()
        self.view.setObjectName("logView")
        self.view.setReadOnly(True)
        self.view.setFrameStyle(QFrame.NoFrame)
        self.view.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.view.setMaximumBlockCount(self.MAX_LINES)
        self.view.setCursorWidth(0)
        self.view.setFont(mono(11))
        self.view.setPlaceholderText("awaiting first detection\u2026")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.document().setDocumentMargin(2)

        # kept so existing callers that poked at .content still find a widget
        self.content = self.view

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(framed(self.view, title, subtitle))

    def log(self, timestep, band, message, kind="info"):
        """Append one line to the bottom of the feed."""
        colour = KINDS.get(kind, INK_DIM)

        html = (
            f'<span style="color:{colour};">&#9679;</span>{NBSP * 2}'
            f'<span style="color:{INK_FAINT};">{_pad(f"T+{timestep:05d}", 9)}</span>'
            f'<span style="color:{INK};">{_pad(f"BAND {band}", 9)}</span>'
            f'<span style="color:{colour};">{message}</span>'
        )

        # only follow the feed if the reader is already at the bottom —
        # scrolling back through history should not get yanked away
        bar = self.view.verticalScrollBar()
        following = bar.value() >= bar.maximum() - 4

        self.view.appendHtml(html)

        if following:
            bar.setValue(bar.maximum())

    def clear(self):
        self.view.clear()
