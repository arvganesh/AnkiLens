from __future__ import annotations

from typing import Any

from aqt.qt import QApplication, QAbstractItemView, QDialog, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, Qt

from .analytics import (
    MissedCardSummary,
    summarize_content_patterns,
    summarize_deck_misses,
    summarize_tag_misses,
    summarize_terms,
)
from .browser_search import browser_search_for_card
from .copy_text import analytics_caption, content_pattern_caption, deck_concentration_caption, tag_concentration_caption, term_caption
from .formatting import format_review_date, priority_label


class MissedCardsDialog(QDialog):
    def __init__(
        self,
        summaries: list[MissedCardSummary],
        *,
        minimum_misses: int,
        result_limit: int,
        lookback_days: int,
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
        pattern_caption = content_pattern_caption(summarize_content_patterns(summaries))
        if pattern_caption:
            layout.addWidget(QLabel(pattern_caption))
        term_text = term_caption(summarize_terms(summaries))
        if term_text:
            layout.addWidget(QLabel(term_text))

        table = QTableWidget(len(summaries), 8, self)
        table.setHorizontalHeaderLabels(
            ["Card", "Deck", "Priority", "Signals", "Misses", "Reviews", "Miss rate", "Last missed"]
        )
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        for row, summary in enumerate(summaries):
            card_item = QTableWidgetItem(summary.card_label)
            card_item.setData(Qt.ItemDataRole.UserRole, summary.card_id)
            table.setItem(row, 0, card_item)
            table.setItem(row, 1, QTableWidgetItem(summary.deck_name))
            table.setItem(row, 2, QTableWidgetItem(priority_label(summary)))
            table.setItem(row, 3, QTableWidgetItem(_signals_label(summary)))
            table.setItem(row, 4, SortItem(str(summary.misses), summary.misses))
            table.setItem(row, 5, SortItem(str(summary.total_reviews), summary.total_reviews))
            table.setItem(row, 6, SortItem(f"{summary.miss_rate:.0%}", summary.miss_rate))
            table.setItem(row, 7, SortItem(format_review_date(summary.last_missed_at), summary.last_missed_at or 0))
        table.setSortingEnabled(True)
        table.selectRow(0)
        table.resizeColumnsToContents()

        layout.addWidget(table)
        button = QPushButton("Copy Browser search for selected card")
        status = QLabel("")
        button.clicked.connect(lambda _checked=False: _copy_selected_card_search(table, status))
        layout.addWidget(button)
        layout.addWidget(status)
        self.setLayout(layout)


class SortItem(QTableWidgetItem):
    def __init__(self, label: str, sort_value: Any) -> None:
        super().__init__(label)
        self.sort_value = sort_value

    def __lt__(self, other) -> bool:
        if isinstance(other, SortItem):
            return self.sort_value < other.sort_value
        return super().__lt__(other)


def _copy_selected_card_search(table: QTableWidget, status: QLabel) -> None:
    selected_rows = table.selectionModel().selectedRows()
    row = selected_rows[0].row() if selected_rows else 0
    item = table.item(row, 0)
    if item is None:
        return
    card_id = int(item.data(Qt.ItemDataRole.UserRole))
    query = browser_search_for_card(card_id)
    QApplication.clipboard().setText(query)
    status.setText(f"Copied: {query}")


def _signals_label(summary: MissedCardSummary) -> str:
    return ", ".join(summary.content_labels) if summary.content_labels else "No obvious pattern"
