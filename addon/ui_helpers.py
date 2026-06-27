from __future__ import annotations

from aqt.qt import QFrame, QLabel, QPushButton, QVBoxLayout


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


def panel_card(title: str, body: str, *, featured: bool = False) -> QFrame:
    frame = QFrame()
    frame.setFrameShape(QFrame.Shape.StyledPanel)
    border = "#cfddbd" if featured else "#e6dfd2"
    background = "#f7fbef" if featured else "#fbfaf5"
    frame.setStyleSheet(
        "QFrame {"
        f"background: {background};"
        f"border: 1px solid {border};"
        "border-radius: 13px;"
        "}"
    )
    layout = QVBoxLayout()
    layout.setContentsMargins(14, 12, 14, 12)
    layout.setSpacing(5)

    heading = QLabel(title)
    heading.setWordWrap(True)
    heading.setStyleSheet("border: none; color: #1f2a20; font-size: 15px; font-weight: 700;")
    layout.addWidget(heading)

    content = QLabel(body)
    content.setWordWrap(True)
    content.setStyleSheet("border: none; color: #3f473e; font-size: 13px; line-height: 120%;")
    layout.addWidget(content)
    frame.setLayout(layout)
    return frame


def primary_button(text: str) -> QPushButton:
    button = QPushButton(text)
    button.setStyleSheet(
        "QPushButton {"
        "background: #2f6f3e;"
        "border: 1px solid #275f34;"
        "border-radius: 8px;"
        "color: white;"
        "font-size: 13px;"
        "font-weight: 600;"
        "padding: 7px 14px;"
        "}"
        "QPushButton:hover { background: #285f35; }"
        "QPushButton:pressed { background: #214f2c; }"
    )
    return button


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
