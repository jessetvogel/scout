import json
from typing import Self

from slash.core import Session
from slash.events import ChangeEvent, Handler
from slash.html import Div, Input
from slash.js import JSFunction

from scout.utils import Box


class SelectGrid(Div):
    def __init__(self, width: int, height: int) -> None:
        super().__init__()

        self._width = width
        self._height = height
        self._handler: Handler[Box] | None = None

        self._setup()

    def _setup(self) -> None:
        # Grid style
        self.style(
            {
                "display": "grid",
                "grid-template-columns": " ".join(["32px"] * self._width),
                "grid-template-rows": " ".join(["32px"] * self._height),
                "gap": "4px",
                "user-drag": "none",
            }
        )

        # Create cells
        self._cells: list[dict[str, int | str]] = []
        for x in range(self._width):
            for y in range(self._height):
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
        Session.require().execute(_JS_SELECT_GRID_SETUP, [self._cells, self._input.id])

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
    ["cells", "input_id"],
    r"""
const selection = [null, null, null, null];
const input = document.getElementById(input_id);

function refresh(id) {
    if (selection[0] !== null) {
        const x_min = Math.min(selection[0], selection[2]);
        const x_max = Math.max(selection[0], selection[2]);
        const y_min = Math.min(selection[1], selection[3]);
        const y_max = Math.max(selection[1], selection[3]);
    
        for (const cell of cells) {
            const elem = document.getElementById(cell.id);
            if (cell.x >= x_min && cell.x <= x_max && cell.y >= y_min && cell.y <= y_max) {
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
        selection[0] = cell.x;
        selection[1] = cell.y;
        selection[2] = cell.x;
        selection[3] = cell.y;
        refresh();
    });

    elem.addEventListener("mouseup", () => {
        // send selection to Python
        input.value = JSON.stringify([
            Math.min(selection[0], selection[2]), // x
            Math.min(selection[1], selection[3]), // y
            Math.abs(selection[0] - selection[2]) + 1, // width
            Math.abs(selection[1] -selection[3]) + 1, // height
        ]);
        input.dispatchEvent(new Event("change"));
        // reset selection
        selection[0] = null;
        selection[1] = null;
        selection[2] = null;
        selection[3] = null;
        refresh(cell.id);
    });

    elem.addEventListener("mouseover", () => {
        selection[2] = cell.x;
        selection[3] = cell.y;
        refresh(cell.id);
    });
    // elem.addEventListener("mouseout", () => refresh());
}
""",
)
