from __future__ import annotations

from aqt.qt import QFrame, QLabel, QVBoxLayout


def title_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet("color: #1f2a20; font-size: 22px; font-weight: 700;")
    return label


def body_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet("color: #4d554d; font-size: 13px;")
    return label


def section_header(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet("color: #283528; font-size: 14px; font-weight: 700; margin-top: 4px;")
    return label


def section_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setFrameShape(QFrame.Shape.StyledPanel)
    label.setStyleSheet(
        "QLabel {"
        "background: #fbfaf5;"
        "border: 1px solid #e6dfd2;"
        "border-radius: 10px;"
        "color: #2f332d;"
        "padding: 9px 11px;"
        "font-size: 13px;"
        "}"
    )
    return label


def metric_card(label: str, value: str) -> QFrame:
    frame = QFrame()
    frame.setFrameShape(QFrame.Shape.StyledPanel)
    frame.setStyleSheet("background: #fbfaf5; border: 1px solid #e6dfd2; border-radius: 10px; padding: 5px;")
    layout = QVBoxLayout()
    layout.setSpacing(2)
    layout.setContentsMargins(8, 5, 8, 5)
    layout.addWidget(QLabel(f"<b>{value}</b>"))
    caption = QLabel(label)
    caption.setStyleSheet("color: #5f675e; font-size: 12px;")
    layout.addWidget(caption)
    frame.setLayout(layout)
    return frame
