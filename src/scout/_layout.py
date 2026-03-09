from __future__ import annotations

import base64
import json
from typing import Any

import pandas as pd
from slash.core import Session
from slash.html import Button, Code, Dialog, Div, Pre, Span
from slash.layout import Column

from scout.components.select_grid import SelectGrid
from scout.icons import icon_dots
from scout.utils import Box
from scout.views import EmptyView, View, ViewContext
from scout.views.scatter import ScatterView
from scout.views.table import TableView

CELL_WIDTH = 128
CELL_HEIGHT = 128
GRID_GAP = 16

VIEW_TYPES: list[type[View]] = [TableView, ScatterView, EmptyView]


class Layout(Div):
    def __init__(self, cols: int, rows: int) -> None:
        super().__init__()

        self._cols = cols
        self._rows = rows

        self._data: pd.DataFrame | None = None
        self._views: list[View] = []

        self._setup()

    @property
    def cols(self) -> int:
        return self._cols

    @property
    def rows(self) -> int:
        return self._rows

    def set_data(self, data: pd.DataFrame) -> None:
        self._data = data
        self._mask = pd.Series([True] * len(data))

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

        # placeholders
        for x in range(self._cols):
            for y in range(self._rows):
                self.append(
                    Div().style(
                        {
                            "grid-column": f"{x + 1} / {x + 2}",
                            "grid-row": f"{y + 1} / {y + 2}",
                            "border": "1px solid var(--border-muted)",
                            "border-radius": "8px",
                            "opacity": "0.33",
                        }
                    )
                )

        # views
        for view in self._views:
            self.append(Cell(self, view))

    def get_state(self) -> Any:
        return {
            "cols": self._cols,
            "rows": self._rows,
            "views": [self._encode_view(view) for view in self._views],
        }

    def set_state(self, state: Any) -> None:
        self._cols = state["cols"]
        self._rows = state["rows"]
        self._views = [self._decode_view(view_data) for view_data in state["views"]]
        self._setup()

    def _encode_view(self, view: View) -> Any:
        return [
            view.ctx.box.encode(),
            view.__class__.__name__,
            view.get_state(),
        ]

    def _decode_view(self, data: Any) -> View:
        view_box = Box.decode(data[0])
        view_type = data[1]
        view_state = data[2]
        return self._create_view(view_box, view_type, view_state)

    def _create_view(self, view_box: Box, view_type: str, view_state: Any | None = None) -> View:
        assert self._data is not None

        # Create view context
        ctx = ViewContext(
            box=view_box,
            width=view_box.w * (CELL_WIDTH + GRID_GAP) - GRID_GAP,
            height=view_box.h * (CELL_WIDTH + GRID_GAP) - GRID_GAP,
            data=self._data,
            mask=self._mask,
            refresh_views=self._refresh_views,
            store_state=self._store_state,
        )

        view: View
        for cls in VIEW_TYPES:
            if cls.__name__ == view_type:
                view = cls(ctx)
                break
        else:
            msg = f"Unknown view type '{view_type}'"
            raise ValueError(msg)

        if view_state is not None:
            try:
                view.set_state(view_state)
            except Exception as err:
                Session.require().log(
                    "Failed to set state of view",
                    level="warning",
                    details=Pre(Code(str(err))),
                )

        view.refresh()

        return view

    def add_view(self, view_box: Box, view_type: str) -> None:
        view = self._create_view(view_box, view_type)
        self._views.append(view)
        self.append(Cell(self, view))
        view.refresh()
        self._store_state()

    def remove_view(self, view: View) -> None:
        self._views.remove(view)
        self._store_state()

    def _refresh_views(self) -> None:
        for view in self._views:
            view.refresh()

    def _store_state(self) -> None:
        state = base64.b64encode(json.dumps(self.get_state()).encode()).decode()
        Session.require().history.replace({}, f"?layout={state}")

    def _load_state(self) -> None:
        # Set state from URL query
        if (state := Session.require().location.query.get("layout", None)) is not None:
            self.set_state(json.loads(base64.b64decode(state).decode()))


class Cell(Div):
    def __init__(self, layout: Layout, view: View) -> None:
        super().__init__()
        self._layout = layout
        self._view = view
        self._setup()

    def _setup(self) -> None:
        self.style(
            {
                "position": "relative",
                "background-color": "var(--bg-dark)",
                "overflow": "auto",
            }
        )
        self.append(self._view, self._button_resize())
        self._set_position()

    def _set_position(self) -> None:
        x, y = self._view.ctx.box.x, self._view.ctx.box.y
        w, h = self._view.ctx.box.w, self._view.ctx.box.h
        self.style({"grid-column": f"{x + 1} / span {w}", "grid-row": f"{y + 1} / span {h}"})

    def _button_resize(self) -> Div:
        return (
            Div(icon_dots().style({"width": "16px"}))
            .style(
                {
                    "display": "flex",
                    "align-items": "center",
                    "justify-content": "center",
                    "position": "absolute",
                    "right": "6px",
                    "top": "6px",
                    "background-color": "color-mix(in srgb, var(--bg), transparent 50%)",
                    "width": "24px",
                    "height": "24px",
                    "border-radius": "12px",
                    "cursor": "pointer",
                }
            )
            .onclick(self._open_dialog)
        )

    def _open_dialog(self) -> None:
        # Remove any previous dialog
        if hasattr(self, "_dialog") and self._dialog.is_mounted():
            self._dialog.unmount()

        # Create dialog
        self._dialog = Dialog(
            Column(
                Span("Set position").style({"font-weight": "bold"}),
                SelectGrid(self._layout.cols, self._layout.rows).onchange(self._resize),
                self._view.settings(),
                Button("Delete")
                .style(
                    {
                        "color": "var(--red)",
                        "border": "1px solid var(--red)",
                        "width": "100%",
                    }
                )
                .onclick(lambda: delete()),
                Button("Close").style({"width": "100%"}).onclick(lambda: self._dialog.unmount()),
            ).style({"gap": "8px", "align-items": "center"})
        ).style({"outline": "none"})
        self.append(self._dialog)

        def delete() -> None:
            self._layout.remove_view(self._view)
            self.unmount()

        # Show dialog
        self._dialog.show_modal()

    def _resize(self, box: Box) -> None:
        # self._dialog.unmount()

        self._view.ctx.box = box
        self._view.ctx.width = box.w * (CELL_WIDTH + GRID_GAP) - GRID_GAP
        self._view.ctx.height = box.h * (CELL_WIDTH + GRID_GAP) - GRID_GAP

        self._set_position()
        self._layout._store_state()
        self._view.refresh()
