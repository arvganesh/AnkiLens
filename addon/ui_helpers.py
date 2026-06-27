from __future__ import annotations

from aqt.qt import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout, Qt

SPACE_1 = 4
SPACE_2 = 8
SPACE_3 = 12
SPACE_4 = 16
SPACE_5 = 20


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
    label.setStyleSheet("color: #283528; font-size: 14px; font-weight: 700; margin-top: 6px;")
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
    margin_x = 20 if featured else 14 if quiet else 17
    margin_y = 16 if featured else 10 if quiet else 13
    layout.setContentsMargins(margin_x, margin_y, margin_x, margin_y)
    layout.setSpacing(SPACE_3 if featured else SPACE_1 if quiet else SPACE_2)

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
        layout.addLayout(_detail_block(label, value))
    if actions:
        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, SPACE_3 if featured else SPACE_2, 0, 0)
        action_row.addStretch(1)
        for action in actions:
            action_row.addWidget(action)
        layout.addLayout(action_row)
    frame.setLayout(layout)
    return frame


def recommendation_card(
    title: str,
    *,
    confidence: str,
    evidence: str,
    next_step: str,
    check: str,
    actions: tuple[QPushButton, ...] = (),
) -> QFrame:
    frame = QFrame()
    frame.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    frame.setFrameShape(QFrame.Shape.StyledPanel)
    frame.setStyleSheet(
        "QFrame {"
        "background: #f7fbef;"
        "border: 1px solid #cfddbd;"
        "border-radius: 15px;"
        "}"
    )
    layout = QVBoxLayout()
    layout.setContentsMargins(24, SPACE_5, 24, 22)
    layout.setSpacing(0)

    eyebrow = QLabel("Recommended next check")
    eyebrow.setStyleSheet("border: none; color: #64705f; font-size: 11px; font-weight: 700;")
    layout.addWidget(eyebrow)
    layout.addSpacing(SPACE_1)

    heading = QLabel(title)
    heading.setWordWrap(True)
    heading.setStyleSheet("border: none; color: #1f2a20; font-size: 18px; font-weight: 700;")
    layout.addWidget(heading)

    layout.addSpacing(SPACE_4)
    layout.addWidget(_next_step_callout(next_step, actions=actions))
    layout.addSpacing(SPACE_3)
    layout.addLayout(_detail_block("Why", f"{confidence}: {evidence}"))
    layout.addSpacing(SPACE_2)
    layout.addLayout(_detail_block("Double-check", check, quiet=True))
    frame.setLayout(layout)
    return frame


def _plain_text(text: str, color: str, size: str, *, weight: int = 400) -> QLabel:
    label = QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet(f"border: none; color: {color}; font-size: {size}; font-weight: {weight}; line-height: 125%;")
    return label


def _next_step_callout(text: str, *, actions: tuple[QPushButton, ...] = ()) -> QFrame:
    frame = QFrame()
    frame.setFrameShape(QFrame.Shape.StyledPanel)
    frame.setStyleSheet(
        "QFrame {"
        "background: #eef6e6;"
        "border: 1px solid #d7e7ca;"
        "border-radius: 10px;"
        "}"
    )
    layout = QVBoxLayout()
    layout.setSpacing(SPACE_1)
    layout.setContentsMargins(14, 12, 14, 12)
    label = QLabel("Next")
    label.setAlignment(Qt.AlignmentFlag.AlignTop)
    label.setStyleSheet("border: none; color: #4f674a; font-size: 12px; font-weight: 700;")
    layout.addWidget(label)
    layout.addWidget(_plain_text(text, "#263726", "14px", weight=700))
    if actions:
        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, SPACE_2, 0, 0)
        for action in actions:
            action.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            action_row.addWidget(action, 0, Qt.AlignmentFlag.AlignLeft)
        action_row.addStretch(1)
        layout.addLayout(action_row)
    frame.setLayout(layout)
    return frame


def _detail_block(label: str, value: str, *, quiet: bool = False) -> QVBoxLayout:
    row = QVBoxLayout()
    row.setSpacing(SPACE_1)
    row.setContentsMargins(0, SPACE_1, 0, SPACE_1)

    label_widget = QLabel(label)
    label_widget.setAlignment(Qt.AlignmentFlag.AlignTop)
    label_widget.setStyleSheet("border: none; color: #667064; font-size: 12px; font-weight: 600;")
    row.addWidget(label_widget)

    value_widget = QLabel(value)
    value_widget.setWordWrap(True)
    value_color = "#5a6358" if quiet else "#2f382f"
    value_size = "12px" if quiet else "13px"
    value_widget.setStyleSheet(f"border: none; color: {value_color}; font-size: {value_size}; line-height: 125%;")
    row.addWidget(value_widget)
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


def tertiary_button(text: str) -> QPushButton:
    button = QPushButton(text)
    button.setStyleSheet(
        "QPushButton {"
        "background: transparent;"
        "border: none;"
        "color: #5f675e;"
        "font-size: 12px;"
        "font-weight: 600;"
        "padding: 4px 2px;"
        "text-decoration: underline;"
        "}"
        "QPushButton:hover { color: #2f382f; }"
        "QPushButton:pressed { color: #1f2a20; }"
    )
    return button


def metric_card(label: str, value: str) -> QFrame:
    frame = QFrame()
    frame.setFrameShape(QFrame.Shape.StyledPanel)
    frame.setStyleSheet("QFrame { background: #fbfaf5; border: 1px solid #e6dfd2; border-radius: 10px; }")
    layout = QVBoxLayout()
    layout.setSpacing(4)
    layout.setContentsMargins(13, 10, 13, 10)
    value_label = QLabel(f"<b>{value}</b>")
    value_label.setStyleSheet("border: none; background: transparent; color: #1f2a20; font-size: 14px;")
    layout.addWidget(value_label)
    caption = QLabel(label)
    caption.setStyleSheet("border: none; background: transparent; color: #5f675e; font-size: 12px;")
    layout.addWidget(caption)
    frame.setLayout(layout)
    return frame
