import pandas as pd
from slash import App as SlashApp

from scout._home import Home
from scout._source import DataSource


class App:
    """Main class for a Scout application.

    Args:
        data: Data source.
        cols: Number of grid columns.
        rows: Number of grid rows.
    """

    def __init__(
        self,
        data: pd.DataFrame | DataSource,
        *,
        cols: int = 6,
        rows: int = 5,
    ) -> None:
        self._data = data
        self._cols = cols
        self._rows = rows

    def run(self) -> None:
        """Runs the application."""
        app = SlashApp()
        app.add_route("/", self._home)
        app.run()

    def _home(self) -> Home:
        return Home(self._data, cols=self._cols, rows=self._rows)
