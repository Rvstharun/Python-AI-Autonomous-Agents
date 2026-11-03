import re
from schemas import Table


def _to_number(text: str) -> float | None:
    """'$12,500' -> 12500.0. Returns None if it isn't a plain number."""
    cleaned = re.sub(r"[^\d.\-]", "", text)
    try:
        return float(cleaned)
    except ValueError:
        return None


def add_total_row(table: Table) -> Table:
    """Tool: sums the last column and appends a Total row.
    Does nothing if any value in that column isn't numeric."""
    if not table.rows:
        return table
    values = [_to_number(row[-1]) for row in table.rows]
    if any(v is None for v in values):
        return table
    symbol = "$" if "$" in table.rows[0][-1] else ""
    total_row = [""] * len(table.headers)
    total_row[0] = "Total"
    total_row[-1] = f"{symbol}{sum(values):,.0f}"
    table.rows.append(total_row)
    return table