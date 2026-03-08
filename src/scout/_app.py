import base64
import json

import pandas as pd
from slash import App as SlashApp
from slash.basic import Tooltip
from slash.core import Elem, Session
from slash.html import Button, Dialog, Span
from slash.layout import Column

from scout._layout import Layout
from scout.components import SelectGrid
from scout.icons import icon_scatter, icon_table, icon_theme
from scout.utils import Box


class App:
    def __init__(
        self,
        data: pd.DataFrame,
        *,
        cols: int = 6,
        rows: int = 5,
    ) -> None:
        self._data = data
        self._cols = cols
        self._rows = rows

    def run(self) -> None:
        app = SlashApp()
        app.add_route("/", self._home)
        app.run()

    def _home(self) -> Elem:
        layout = Layout(self._data, cols=self._cols, rows=self._rows)

        # Create menu
        Menu(layout).mount()

        # Set state
        state = Session.require().location.query.get("layout", None)
        if state is not None:
            layout.set_state(json.loads(base64.b64decode(state).decode()))

        # Render
        return Column(
            layout,
        ).style({"gap": "32px", "align-items": "center", "padding-top": "32px"})


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

        self.append(
            self._button(icon_table().style({"width": "20px"}), title="Add table").onclick(
                lambda: self._add_view("TableView", "table")
            )
        )
        self.append(
            self._button(icon_scatter().style({"width": "20px"}), title="Add scatter").onclick(
                lambda: self._add_view("ScatterView", "scatter")
            )
        )
        self.append(
            self._button(icon_theme().style({"width": "20px"}), title="Toggle theme").onclick(
                lambda: self._toggle_theme()
            )
        )

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
