"""Text rendering of a dashboard summary (presentation only)."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from wealth.dashboard import DashboardSummary

WIDTH = 66


def _amount(value) -> str:
    return "{:,}".format(value)


def render_summary(summary: DashboardSummary) -> str:
    lines: List[str] = []
    rule = "-" * WIDTH
    lines.append("PERSONAL WEALTH DASHBOARD".ljust(WIDTH - 32)
                 + ("prices: " + summary.data_source).rjust(32))
    lines.append("=" * WIDTH)

    lines.append("Portfolio structure")
    for depth, name, value in summary.breakdown:
        label = "  " * depth + name
        lines.append("  {:<44} {:>19}".format(label, _amount(value)))
    lines.append("")

    lines.append("{:<16} {:<20} {:>13} {:>13}".format(
        "Holding", "Group", "Market value", "If sold"))
    lines.append(rule)
    for p in summary.positions:
        lines.append("{:<16} {:<20} {:>13} {:>13}".format(
            p.symbol, p.group, _amount(p.value), _amount(p.net_value)))
    lines.append(rule)
    lines.append("{:<37} {:>13}".format("NET WORTH", _amount(summary.net_worth)))
    lines.append("{:<37} {:>13} {:>13}".format(
        "LIQUIDATION VALUE", "", _amount(summary.liquidation_value)))
    lines.append("{:<37} {:>27}".format(
        "  cost of selling everything", "-" + _amount(summary.selling_cost)))
    lines.append("")

    lines.append("Allocation by asset class")
    for kind, percent in sorted(summary.allocation.items(), key=lambda kv: -kv[1]):
        lines.append("  {:<14} {:>6}%".format(kind, percent))
    return "\n".join(lines)
