from collections.abc import Callable

import pandas as pd
from slash.basic import Loading, Tooltip
from slash.core import Elem, Session
from slash.html import Button, Dialog, Div, Option, Select, Span
from slash.layout import Column, Row

from scout._layout import Layout
from scout._source import DataSource
from scout.components.select_grid import SelectGrid
from scout.icons import icon_filter, icon_scatter, icon_table, icon_theme
from scout.utils import Box


class Home(Div):
    def __init__(
        self,
        source: pd.DataFrame | DataSource,
        *,
        cols: int,
        rows: int,
    ) -> None:
        super().__init__()

        self._source = source
        self._cols = cols
        self._rows = rows

        self._setup()

    def _setup(self) -> None:
        if isinstance(self._source, DataSource):
            self.append(SelectData(self._source, self._set_data))

        self._layout = Layout(cols=self._cols, rows=self._rows)
        self.append(Column(self._layout).style({"gap": "32px", "align-items": "center", "padding-top": "32px"}))

        self._menu = Menu(self._layout)
        self.append(self._menu)

        if isinstance(self._source, pd.DataFrame):
            self._set_data(self._source)

    def _set_data(self, data: pd.DataFrame) -> None:
        should_set_state = self._layout._data is None

        # Pass data to layout
        self._layout.set_data(data)

        # Refresh menu
        self._menu.refresh()

        if should_set_state:
            # Load state
            self._layout._load_state()


class Menu(Column):
    def __init__(self, layout: Layout) -> None:
        super().__init__()

        self._layout = layout

        self._setup()

    def _setup(self) -> None:
        self.style(
            {
                "position": "fixed",
                "left": "0px",
                "top": "0px",
                "gap": "8px",
                "z-index": "10",
                "margin-left": "8px",
                "height": "100dvh",
                "justify-content": "center",
            }
        )

        self._button_table = self._button(icon_table().style({"width": "20px"}), title="Add table").onclick(
            lambda: self._add_view("TableView", "table")
        )

        self._button_scatter = self._button(icon_scatter().style({"width": "20px"}), title="Add scatter").onclick(
            lambda: self._add_view("ScatterView", "scatter")
        )

        self._button_filter = self._button(icon_filter().style({"width": "20px"}), title="Add filter").onclick(
            lambda: self._add_view("FilterView", "filter")
        )

        self._button_theme = self._button(icon_theme().style({"width": "20px"}), title="Toggle theme").onclick(
            lambda: self._toggle_theme()
        )

        self.append(self._button_table)
        self.append(self._button_scatter)
        self.append(self._button_filter)
        self.append(self._button_theme)

        self.refresh()

    def refresh(self) -> None:
        disabled = self._layout._data is None

        self._button_table.set_disabled(disabled)
        self._button_scatter.set_disabled(disabled)
        self._button_filter.set_disabled(disabled)

    def _button(self, icon: Elem, *, title: str | None = None) -> Button:
        button = Button(icon).style(
            {
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
                "width": "48px",
                "height": "48px",
                "min-width": "48px",
                "border-radius": "24px",
            }
        )

        if title is not None:
            button.append(Tooltip(title, target=button).style({"white-space": "nowrap"}))

        return button

    def _add_view(self, view_type: str, name: str) -> None:
        dialog = Dialog(
            Column(
                Span(f"Place {name}").style({"font-weight": "bold"}),
                SelectGrid(
                    cols=self._layout.cols,
                    rows=self._layout.rows,
                ).onchange(lambda box: actually_add_view(box)),
            ).style({"gap": "16px", "align-items": "center"})
        ).style({"outline": "none"})
        dialog.mount()
        dialog.show_modal()

        def actually_add_view(box: Box) -> None:
            dialog.unmount()
            self._layout.add_view(box, view_type)

    def _toggle_theme(self) -> None:
        theme = Session.require().get_theme()
        Session.require().set_theme("dark" if theme == "light" else "light")


class SelectData(Row):
    def __init__(self, source: DataSource, set_data: Callable[[pd.DataFrame], None]) -> None:
        super().__init__()
        self._source = source
        self._set_data = set_data
        self._setup()

    def _setup(self) -> None:
        self.style(
            {
                "gap": "16px",
                "align-items": "center",
                "justify-content": "center",
                "background": "var(--bg)",
                "padding": "16px",
                "border-bottom": "1px solid var(--border-muted)",
            }
        )

        self.append(Span("Select data").style({"font-weight": "bold"}))

        self.append(self._separator())

        selects: dict[str, Select] = {}
        for name, options in self._source.params().items():
            self.append(
                Row(
                    Span(name).style({"font-weight": "bold"}),
                    select := Select([Option(option) for option in options]),
                ).style({"gap": "16px", "align-items": "center"})
            )
            selects[name] = select

        self.append(self._separator())

        async def _load_data() -> None:
            async with Loading("Loading data.."):
                kwargs = {name: select.value for name, select in selects.items()}
                data = self._source.data(**kwargs)
                self._set_data(data)

        self.append(Button("Load data").onclick(_load_data))

    def _separator(self) -> Div:
        return Div().style({"width": "1px", "height": "40px", "border-left": "1px solid var(--border)"})
