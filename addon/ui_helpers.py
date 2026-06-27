from __future__ import annotations

from aqt.qt import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, Qt


def title_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    label.setStyleSheet("color: #1f2a20; font-size: 22px; font-weight: 700;")
    return label


def body_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
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


def panel_card(
    title: str,
    body: str = "",
    *,
    rows: tuple[tuple[str, str], ...] = (),
    actions: tuple[QPushButton, ...] = (),
    featured: bool = False,
    quiet: bool = False,
) -> QFrame:
    frame = QFrame()
    frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    frame.setFrameShape(QFrame.Shape.StyledPanel)
    border = "#cfddbd" if featured else "#ebe4d8" if quiet else "#e6dfd2"
    background = "#f7fbef" if featured else "#f7f4ec" if quiet else "#fbfaf5"
    frame.setStyleSheet(
        "QFrame {"
        f"background: {background};"
        f"border: 1px solid {border};"
        "border-radius: 13px;"
        "}"
    )
    layout = QVBoxLayout()
    margin_x = 18 if featured else 16
    margin_y = 15 if featured else 12
    layout.setContentsMargins(margin_x, margin_y, margin_x, margin_y)
    layout.setSpacing(9 if featured else 7)

    heading = QLabel(title)
    heading.setWordWrap(True)
    heading.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    heading_size = "13px" if quiet else "16px" if featured else "15px"
    heading.setStyleSheet(f"border: none; color: #1f2a20; font-size: {heading_size}; font-weight: 700;")
    layout.addWidget(heading)

    if body:
        content = QLabel(body)
        content.setWordWrap(True)
        content.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        content_size = "12px" if quiet else "13px"
        content.setStyleSheet(f"border: none; color: #3f473e; font-size: {content_size}; line-height: 120%;")
        layout.addWidget(content)
    for label, value in rows:
        layout.addLayout(_detail_row(label, value))
    if actions:
        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 8 if featured else 6, 0, 0)
        action_row.addStretch(1)
        for action in actions:
            action_row.addWidget(action)
        layout.addLayout(action_row)
    frame.setLayout(layout)
    return frame


def _detail_row(label: str, value: str) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(12)
    row.setContentsMargins(0, 0, 0, 0)

    label_widget = QLabel(label)
    label_widget.setFixedWidth(76)
    label_widget.setAlignment(Qt.AlignmentFlag.AlignTop)
    label_widget.setStyleSheet("border: none; color: #667064; font-size: 12px; font-weight: 600;")
    row.addWidget(label_widget)

    value_widget = QLabel(value)
    value_widget.setWordWrap(True)
    value_widget.setStyleSheet("border: none; color: #2f382f; font-size: 13px;")
    row.addWidget(value_widget, 1)
    return row


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


def secondary_button(text: str) -> QPushButton:
    button = QPushButton(text)
    button.setStyleSheet(
        "QPushButton {"
        "background: #fbfaf5;"
        "border: 1px solid #d8d0c2;"
        "border-radius: 8px;"
        "color: #2f382f;"
        "font-size: 13px;"
        "font-weight: 600;"
        "padding: 7px 14px;"
        "}"
        "QPushButton:hover { background: #f0eadf; }"
        "QPushButton:pressed { background: #e5ddcf; }"
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
