"""File export (SRP from Lab 1). Adding a format means adding a class."""

from __future__ import annotations

import csv
import json
from abc import ABC, abstractmethod
from typing import Sequence

from wealth.valuation.calculator import Position

FIELDS = ["group", "symbol", "kind", "quantity", "value", "net_value"]


class PortfolioExporter(ABC):
    extension = ""

    @abstractmethod
    def export(self, positions: Sequence[Position], path: str) -> None:
        """Writes `positions` to `path`."""


class CsvExporter(PortfolioExporter):
    extension = ".csv"

    def export(self, positions: Sequence[Position], path: str) -> None:
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(FIELDS)
            for p in positions:
                writer.writerow([p.group, p.symbol, p.kind, str(p.quantity),
                                 str(p.value), str(p.net_value)])


class JsonExporter(PortfolioExporter):
    extension = ".json"

    def export(self, positions: Sequence[Position], path: str) -> None:
        payload = [{name: str(getattr(p, name)) for name in FIELDS} for p in positions]
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
