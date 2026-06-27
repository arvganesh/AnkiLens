from __future__ import annotations

from aqt.qt import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout

from .analytics import MissedCardSummary


class MissedCardsDialog(QDialog):
    def __init__(self, summaries: list[MissedCardSummary], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Cards Needing Attention")
        self.resize(760, 420)

        table = QTableWidget(len(summaries), 5, self)
        table.setHorizontalHeaderLabels(["Card", "Deck", "Misses", "Reviews", "Miss rate"])
        for row, summary in enumerate(summaries):
            table.setItem(row, 0, QTableWidgetItem(summary.card_label))
            table.setItem(row, 1, QTableWidgetItem(summary.deck_name))
            table.setItem(row, 2, QTableWidgetItem(str(summary.misses)))
            table.setItem(row, 3, QTableWidgetItem(str(summary.total_reviews)))
            table.setItem(row, 4, QTableWidgetItem(f"{summary.miss_rate:.0%}"))

        layout = QVBoxLayout()
        layout.addWidget(table)
        self.setLayout(layout)
