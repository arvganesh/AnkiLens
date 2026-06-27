from __future__ import annotations

from aqt.qt import QDialog, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout

from .analytics import MissedCardSummary


class MissedCardsDialog(QDialog):
    def __init__(self, summaries: list[MissedCardSummary], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Bonsai")
        self.resize(760, 420)

        layout = QVBoxLayout()
        if not summaries:
            layout.addWidget(
                QLabel(
                    "No repeated misses found yet.\n\n"
                    "When cards need another pass more than once, Bonsai will show them here."
                )
            )
            self.setLayout(layout)
            return

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
