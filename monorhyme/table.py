"""Tables for storing, sorting, and displaying information.

Tables are structured as follows:

    Key:
    - d: DIV
    - c: SEP_CORNER
    - s: SEP_DIV

    d <header> d ... d
    csssssssssscsssssc
    d <data>   d ... d

"""


import typing as T
from dataclasses import dataclass, field
from . import color

# Types are ignored as methods are generated.
# Failure to resolve is an import-time failure.
DIV: str = color.Foreground.cyan("|")  # type: ignore
"""The main table divider character. Used for table boarders and column separators."""

SEP_CORNER: str = DIV
"""The corner symbol from the table. Used for the corners for cells on the table separator line."""

SEP_DIV: str = color.Foreground.yellow("-")  # type: ignore
"""The separator divider. Used to fill separator cells."""


class Row:
    """A container for a row of data.

    Args:
        kwargs: Keyword arguments, meant to match the columns of a ``Table``.

    """

    def __init__(self, **kwargs):
        self.data = kwargs

    def __getitem__(self, attr_name: str):
        return self.data[attr_name]

    def __repr__(self) -> str:
        return repr(self.data)

    def get(self, columns: T.List["Column"]) -> T.Iterator[T.Tuple["Column", T.Any]]:
        """Get the column in the row in the order, specified by ``names``.

        Args:
            columns: The columns to get in the given order

        Returns:
            An iterator of the columns and their value

        """
        for column in columns:
            yield column, self.data[column.name]


@dataclass
class Column:
    """A renderable column of data.

    Attributes:
        name: The name of the column
        formatter: Format the column data for rendering

    """

    name: str
    formatter: T.Callable[[str], str] = field(default_factory=lambda: lambda s: str(s))

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: T.Any) -> bool:
        if isinstance(other, Column):
            return other.name == self.name
        return False


class Table:
    """A sortable table of data. For rendering to the console.

    Args:
        columns: The list of column names
        sort_by: The column that by which the table is sorted
        sort_map: A map to convert values when sorting. This is applied across all columns

    """

    def __init__(
        self, columns: T.List[Column], sort_by: str = None, sort_map: T.Optional[T.Dict[str, T.Any]] = None,
    ):
        self.columns = columns
        self._data: T.List[Row] = []
        self._sort_by = sort_by
        self.column_lengths = {k.name: len(k.name) for k in self.columns}
        self.sort_map = sort_map if sort_map is not None else {}

    def __repr__(self) -> str:
        if self._sort_by is not None:
            self._data = sorted(self._data, key=lambda r: self.sort_map.get(r[self._sort_by], r[self._sort_by]),)
        # Render the headers
        column_body = f" {DIV} ".join(col.name.ljust(self.column_lengths[col.name]) for col in self.columns)
        _repr = f"{DIV} {column_body} {DIV}\n"

        # Render the divider
        div_body = SEP_CORNER.join(SEP_DIV * (self.column_lengths[col.name] + 2) for col in self.columns)
        _repr += f"{SEP_CORNER}{div_body}{SEP_CORNER}\n"

        # Render the table body
        for row in self._data:
            row_body = f" {DIV} ".join(
                col.formatter(val).ljust(self.column_lengths[col.name]) for col, val in row.get(self.columns)
            )
            _repr += f"{DIV} {row_body} {DIV}\n"
        return _repr

    def add_row(self, **kwargs):
        """Add a row to the table. All of the ``kwargs`` must be in ``self.columns.``

        Args:
            kwargs: The column-named values to add to the table as a row

        """

        for kwarg in kwargs:
            value = kwargs[kwarg]
            self.column_lengths[kwarg] = max(
                # TODO Format the value before calculating it's length
                len(str(value)),
                self.column_lengths[kwarg],
            )
        self._data.append(Row(**kwargs))
