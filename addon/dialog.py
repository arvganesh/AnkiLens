from __future__ import annotations

from aqt.qt import QDialog, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout

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
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSortingEnabled(True)
        for row, summary in enumerate(summaries):
            table.setItem(row, 0, QTableWidgetItem(summary.card_label))
            table.setItem(row, 1, QTableWidgetItem(summary.deck_name))
            table.setItem(row, 2, QTableWidgetItem(priority_label(summary)))
            table.setItem(row, 3, QTableWidgetItem(str(summary.misses)))
            table.setItem(row, 4, QTableWidgetItem(str(summary.total_reviews)))
            table.setItem(row, 5, QTableWidgetItem(f"{summary.miss_rate:.0%}"))
            table.setItem(row, 6, QTableWidgetItem(format_review_date(summary.last_missed_at)))
        table.resizeColumnsToContents()

        layout.addWidget(table)
        self.setLayout(layout)
