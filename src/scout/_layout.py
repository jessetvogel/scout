from __future__ import annotations

from typing import Any

import pandas as pd
from slash.html import Dialog, Div, Span
from slash.layout import Column

from scout.components import SelectGrid
from scout.utils import Box
from scout.views import EmptyView, View, ViewContext
from scout.views.scatter import ScatterView
from scout.views.table import TableView

VIEWS: list[type[View]] = [
    TableView,
    EmptyView,
    ScatterView,
]

CELL_WIDTH = 128
CELL_HEIGHT = 128
GRID_GAP = 16


class Layout(Div):
    def __init__(self, data: pd.DataFrame, *, cols: int, rows: int) -> None:
        super().__init__()

        self._data = data
        self._mask = pd.Series([True] * len(data))
        self._cols = cols
        self._rows = rows
        self._views: list[View] = []

        self._setup()

    @property
    def cols(self) -> int:
        return self._cols

    @property
    def rows(self) -> int:
        return self._rows

    def _setup(self) -> None:
        self.clear()
        self.style(
            {
                "display": "grid",
                "grid-template-columns": " ".join([f"{CELL_WIDTH}px"] * self._cols),
                "grid-template-rows": " ".join([f"{CELL_HEIGHT}px"] * self._rows),
                "gap": f"{GRID_GAP}px",
            }
        )

        for view in self._views:
            self.append(Cell(self, view))

    def get_state(self) -> Any:
        return {
            "cols": self._cols,
            "rows": self._rows,
            "views": [],  # TODO
        }

    def set_state(self, state: Any) -> None:
        self._cols = state["cols"]
        self._rows = state["rows"]
        self._views = [
            self._create_view(view_type, view_state, Box(*box)) for (box, (view_type, view_state)) in state["cells"]
        ]
        self._setup()

    def _refresh_views(self) -> None:
        for view in self._views:
            view.refresh()

    def _create_view(self, view_type: str, view_state: Any, box: Box) -> View:
        # Create view context
        ctx = ViewContext(
            box=box,
            width=box.w * (CELL_WIDTH + GRID_GAP) - GRID_GAP,
            height=box.h * (CELL_WIDTH + GRID_GAP) - GRID_GAP,
            data=self._data,
            mask=self._mask,
        )

        view: View
        for cls in VIEWS:
            if cls.__name__ == view_type:
                view = cls(ctx)
                break
        else:
            msg = f"Unknown view type '{view_type}'"
            raise ValueError(msg)

        view.set_state(view_state)

        view.refresh()

        return view


class Cell(Div):
    def __init__(self, layout: Layout, view: View) -> None:
        super().__init__()
        self._layout = layout
        self._view = view
        self._setup()

    def _setup(self) -> None:
        self.style({"position": "relative", "overflow": "hidden"})
        self.append(self._view, self._button_resize())
        self._set_position()

    def _set_position(self) -> None:
        x, y = self._view.ctx.box.x, self._view.ctx.box.y
        w, h = self._view.ctx.box.w, self._view.ctx.box.h
        self.style({"grid-column": f"{x + 1} / span {w}", "grid-row": f"{y + 1} / span {h}"})

    def serialize(self) -> Any:
        pass

    def deserialize(self, data: Any) -> None:
        pass

    def _button_resize(self) -> Div:
        return (
            Div()
            .style(
                {
                    "position": "absolute",
                    "right": "8px",
                    "top": "8px",
                    "background-color": "var(--green)",
                    "width": "24px",
                    "height": "24px",
                    "opacity": "0.5",
                    "border-radius": "12px",
                }
            )
            .onclick(self._open_dialog_resize)
        )

    def _open_dialog_resize(self) -> None:
        # TODO: escape dialog problems
        self._dialog = Dialog(
            Column(
                Span("Set position").style({"font-weight": "bold"}),
                SelectGrid(self._layout.cols, self._layout.rows).onchange(self._resize),
            ).style({"gap": "16px", "align-items": "center"})
        ).style({"outline": "none"})
        self.append(self._dialog)
        self._dialog.show_modal()

    def _resize(self, box: Box) -> None:
        self._dialog.unmount()

        self._view.ctx.box = box
        self._view.ctx.width = box.w * (CELL_WIDTH + GRID_GAP) - GRID_GAP
        self._view.ctx.height = box.h * (CELL_WIDTH + GRID_GAP) - GRID_GAP

        self._set_position()
        self._view.refresh()
