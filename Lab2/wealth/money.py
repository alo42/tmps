"""Money helpers. Monetary values are always Decimal, never float."""

from decimal import ROUND_HALF_UP, Decimal
from typing import Union

CENTS = Decimal("0.01")
ZERO = Decimal("0")

Number = Union[Decimal, int, str, float]


def money(value: Decimal) -> Decimal:
    """Round a raw Decimal to 2 places using commercial rounding."""
    return value.quantize(CENTS, rounding=ROUND_HALF_UP)


def to_decimal(value: Number) -> Decimal:
    """
    Converts user input to Decimal. Floats go through str() first, so 0.35
    becomes Decimal("0.35") instead of 0.34999999999999997779553950749686919152736663818359375.
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        return Decimal(str(value))
    return Decimal(value)
