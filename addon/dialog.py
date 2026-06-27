from __future__ import annotations

from collections.abc import Callable
from typing import Any

from aqt.qt import QAbstractItemView, QDialog, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, Qt

from .analytics import MissedCardSummary, summarize_deck_misses, summarize_tag_misses
from .copy_text import analytics_caption, deck_concentration_caption, tag_concentration_caption
from .formatting import format_review_date, priority_label


class MissedCardsDialog(QDialog):
    def __init__(
        self,
        summaries: list[MissedCardSummary],
        *,
        minimum_misses: int,
        result_limit: int,
        lookback_days: int,
        on_open_card: Callable[[int], None] | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Bonsai")
        self.resize(760, 420)

        layout = QVBoxLayout()
        layout.addWidget(
            QLabel(
                analytics_caption(
                    shown_count=len(summaries),
                    minimum_misses=minimum_misses,
                    result_limit=result_limit,
                    lookback_days=lookback_days,
                )
            )
        )
        if not summaries:
            self.setLayout(layout)
            return

        layout.addWidget(QLabel(deck_concentration_caption(summarize_deck_misses(summaries))))
        tag_caption = tag_concentration_caption(summarize_tag_misses(summaries))
        if tag_caption:
            layout.addWidget(QLabel(tag_caption))

        table = QTableWidget(len(summaries), 7, self)
        table.setHorizontalHeaderLabels(
            ["Card", "Deck", "Priority", "Misses", "Reviews", "Miss rate", "Last missed"]
        )
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        for row, summary in enumerate(summaries):
            card_item = QTableWidgetItem(summary.card_label)
            card_item.setData(Qt.ItemDataRole.UserRole, summary.card_id)
            table.setItem(row, 0, card_item)
            table.setItem(row, 1, QTableWidgetItem(summary.deck_name))
            table.setItem(row, 2, QTableWidgetItem(priority_label(summary)))
            table.setItem(row, 3, SortItem(str(summary.misses), summary.misses))
            table.setItem(row, 4, SortItem(str(summary.total_reviews), summary.total_reviews))
            table.setItem(row, 5, SortItem(f"{summary.miss_rate:.0%}", summary.miss_rate))
            table.setItem(row, 6, SortItem(format_review_date(summary.last_missed_at), summary.last_missed_at or 0))
        table.setSortingEnabled(True)
        table.resizeColumnsToContents()

        layout.addWidget(table)
        if on_open_card:
            button = QPushButton("Open selected card in Browser")
            button.clicked.connect(lambda: _open_selected_card(table, on_open_card))
            layout.addWidget(button)
        self.setLayout(layout)


class SortItem(QTableWidgetItem):
    def __init__(self, label: str, sort_value: Any) -> None:
        super().__init__(label)
        self.sort_value = sort_value

    def __lt__(self, other) -> bool:
        if isinstance(other, SortItem):
            return self.sort_value < other.sort_value
        return super().__lt__(other)


def _open_selected_card(table: QTableWidget, on_open_card: Callable[[int], None]) -> None:
    selected_rows = table.selectionModel().selectedRows()
    if not selected_rows:
        return
    item = table.item(selected_rows[0].row(), 0)
    if item is None:
        return
    on_open_card(int(item.data(Qt.ItemDataRole.UserRole)))
