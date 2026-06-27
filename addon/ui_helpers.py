from __future__ import annotations

from aqt.qt import QFrame, QLabel, QVBoxLayout


def title_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet("font-size: 22px; font-weight: 700;")
    return label


def body_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet("color: #333; font-size: 13px;")
    return label


def section_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setFrameShape(QFrame.Shape.StyledPanel)
    label.setStyleSheet(
        "QLabel {"
        "background: #f7f7f7;"
        "border: 1px solid #dddddd;"
        "border-radius: 8px;"
        "padding: 10px;"
        "font-size: 13px;"
        "}"
    )
    return label


def metric_card(label: str, value: str) -> QFrame:
    frame = QFrame()
    frame.setFrameShape(QFrame.Shape.StyledPanel)
    frame.setStyleSheet("background: #fbfbfb; border: 1px solid #dddddd; border-radius: 8px; padding: 8px;")
    layout = QVBoxLayout()
    layout.addWidget(QLabel(f"<b>{value}</b>"))
    layout.addWidget(QLabel(label))
    frame.setLayout(layout)
    return frame
