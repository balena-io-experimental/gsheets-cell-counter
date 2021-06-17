"""Utilities to parse the usage-related information."""
import string


class Cell:
    """Class to manage the indexing of values within spreadsheets."""
    alphabet = string.ascii_uppercase

    def __init__(self, row_count: int, col_count: int) -> None:
        """Initialize a Cell with its row and column indices."""
        self.row = row_count - 1 if row_count else 0
        self.col = col_count - 1 if col_count else 0

    @staticmethod
    def to_number(value: int) -> int:
        """Convert value to its 1-based index."""
        return value + 1

    @staticmethod
    def to_letter(value: int) -> str:
        """Convert value to its alphabetical index."""
        divisor, remainder = divmod(value, len(Cell.alphabet))
        return Cell.to_letter(divisor - 1) + Cell.alphabet[remainder] if divisor else Cell.alphabet[remainder]

    @property
    def count(self) -> int:
        """Count the cells up to the current position."""
        return (self.row + 1) * (self.col + 1)

    @property
    def index(self) -> str:
        """Convert cell position to A1 notation."""
        return f'{Cell.to_letter(self.col)}{Cell.to_number(self.row)}'

    def __eq__(self, other: 'Cell') -> bool:
        """Compare two instances of Cell."""
        return self.__dict__ == other.__dict__
