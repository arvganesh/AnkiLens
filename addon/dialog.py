from __future__ import annotations

from aqt.qt import QDialog, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout

from .analytics import MissedCardSummary, summarize_deck_misses
from .copy_text import analytics_caption, deck_concentration_caption


class MissedCardsDialog(QDialog):
    def __init__(
        self,
        summaries: list[MissedCardSummary],
        *,
        minimum_misses: int,
        result_limit: int,
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
                )
            )
        )
        if not summaries:
            self.setLayout(layout)
            return

        layout.addWidget(QLabel(deck_concentration_caption(summarize_deck_misses(summaries))))

        table = QTableWidget(len(summaries), 5, self)
        table.setHorizontalHeaderLabels(["Card", "Deck", "Misses", "Reviews", "Miss rate"])
        for row, summary in enumerate(summaries):
            table.setItem(row, 0, QTableWidgetItem(summary.card_label))
            table.setItem(row, 1, QTableWidgetItem(summary.deck_name))
            table.setItem(row, 2, QTableWidgetItem(str(summary.misses)))
            table.setItem(row, 3, QTableWidgetItem(str(summary.total_reviews)))
            table.setItem(row, 4, QTableWidgetItem(f"{summary.miss_rate:.0%}"))

        layout.addWidget(table)
        self.setLayout(layout)
