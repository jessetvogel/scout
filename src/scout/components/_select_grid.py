import json
from typing import Self

from slash.core import Session
from slash.events import ChangeEvent, Handler
from slash.html import Div, Input
from slash.js import JSFunction

from scout.utils import Box


class SelectGrid(Div):
    def __init__(self, cols: int, rows: int) -> None:
        super().__init__()

        self._cols = cols
        self._rows = rows
        self._handler: Handler[Box] | None = None

        self._setup()

    def _setup(self) -> None:
        # Grid style
        self.style(
            {
                "display": "grid",
                "grid-template-columns": " ".join(["32px"] * self._cols),
                "grid-template-rows": " ".join(["32px"] * self._rows),
                "gap": "4px",
                "user-drag": "none",
            }
        )

        # Create cells
        self._cells: list[dict[str, int | str]] = []
        for x in range(self._cols):
            for y in range(self._rows):
                self.append(
                    cell := Div().style(
                        {
                            "grid-area": f"{y + 1} / {x + 1} / {y + 2} / {x + 2}",
                            "border": "1px solid var(--border)",
                            "border-radius": "2px",
                            "cursor": "pointer",
                            "user-drag": "none",
                        }
                    )
                )
                self._cells.append({"x": x, "y": y, "id": cell.id})

        # Create hidden input
        self._input = Input("hidden").onchange(self._onchange)
        self.append(self._input)

        self.onmount(self._onmount)

    def _onmount(self) -> None:
        Session.require().execute(_JS_SELECT_GRID_SETUP, [self.id, self._cells, self._input.id])

    def _onchange(self, event: ChangeEvent) -> None:
        x, y, w, h = json.loads(event.value)
        box = Box(x, y, w, h)
        if self._handler is not None:
            Session.require().call_handler(self._handler, box)

    def onchange(self, handler: Handler[Box]) -> Self:
        """Add event handler for change event."""
        self._handler = handler
        return self


_JS_SELECT_GRID_SETUP = JSFunction(
    ["grid_id", "cells", "input_id"],
    r""" 
const input = document.getElementById(input_id);
const grid = document.getElementById(grid_id);

let selection = null;

function box() {
    const x = Math.min(selection[0], selection[2]);
    const y = Math.min(selection[1], selection[3]);
    const w = Math.abs(selection[0] - selection[2]) + 1;
    const h = Math.abs(selection[1] - selection[3]) + 1;
    return [x, y, w, h];
}

function refresh(id) {
    if (selection !== null) {
        const [x, y, w, h] = box();
        for (const cell of cells) {
            const elem = document.getElementById(cell.id);
            if (cell.x >= x && cell.x < x + w && cell.y >= y && cell.y < y + h) {
                elem.style.backgroundColor = "var(--blue)";
            } else {
                elem.style.backgroundColor = null;
            }
        }
    } else {
        for (const cell of cells) {
            const elem = document.getElementById(cell.id);
            if (cell.id == id) {
                elem.style.backgroundColor = "var(--light-gray)";
            } else {
                elem.style.backgroundColor = null;
            }
        }
    }
}

for (const cell of cells) {
    const elem = document.getElementById(cell.id);

    elem.addEventListener("mousedown", () => {
        if (selection === null) {
            selection = [cell.x, cell.y, cell.x, cell.y];
            refresh();
        }
    });

    elem.addEventListener("mouseup", () => {
        if (selection !== null) {
            // send selection to Python
            input.value = JSON.stringify(box());
            input.dispatchEvent(new Event("change"));
            // reset selection
            selection = null;
            refresh(cell.id);
        }
    });

    elem.addEventListener("mouseover", () => {
        if (selection !== null) {
            selection[2] = cell.x;
            selection[3] = cell.y;
        }
        refresh(cell.id);
    });
    
    grid.addEventListener("mouseout", () => refresh());
}
""",
)
