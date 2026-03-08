import json
from typing import Self

from slash.core import Session
from slash.events import ChangeEvent, Handler
from slash.html import Div, Input
from slash.js import JSFunction

from scout.utils import Box


class SelectRect(Div):
    def __init__(self) -> None:
        super().__init__()

        self._handler: Handler[Box] | None = None

        self._setup()

    def _setup(self) -> None:
        self._rect = Div().style(
            {
                "position": "absolute",
                "border": "2px solid var(--red)",
                "border-radius": "2px",
                "box-sizing": "border-box",
            }
        )
        self.append(self._rect)

        # Create hidden input
        self._input = Input("hidden").onchange(self._onchange)
        self.append(self._input)

        self.onmount(self._onmount)

    def _onmount(self) -> None:
        Session.require().execute(_JS_SELECT_RECT_SETUP, [self.id, self._rect.id, self._input.id])

    def _onchange(self, event: ChangeEvent) -> None:
        x, y, w, h = json.loads(event.value)
        box = Box(x, y, w, h)
        if self._handler is not None:
            Session.require().call_handler(self._handler, box)

    def onchange(self, handler: Handler[Box]) -> Self:
        """Add event handler for change event."""
        self._handler = handler
        return self


_JS_SELECT_RECT_SETUP = JSFunction(
    ["id", "rect_id", "input_id"],
    r""" 
const elem = document.getElementById(id);
const rect = document.getElementById(rect_id);
const input = document.getElementById(input_id);

let selection = null;

function xy(event) {
    const r = elem.getBoundingClientRect();
    return [event.clientX - r.left, event.clientY - r.top];
}

function box() {
    const left = Math.min(selection[0], selection[2]);
    const top = Math.min(selection[1], selection[3]);
    const width = Math.abs(selection[0] - selection[2]);
    const height = Math.abs(selection[1] - selection[3]);
    return [left, top, width, height];
}

function refresh() {
    if (selection !== null) {
        const [left, top, width, height] = box();
        rect.style.display = null;
        rect.style.left = `${left}px`;
        rect.style.top = `${top}px`;
        rect.style.width = `${width}px`;
        rect.style.height = `${height}px`;
    } else {
        rect.style.display = "none";
    }
}

elem.addEventListener("mousedown", (event) => {
    if (selection === null) {
        const [x, y] = xy(event);
        selection = [x, y, x, y];
    }
});

elem.addEventListener("mousemove", (event) => {
    if (selection !== null) {
        const [x, y] = xy(event);
        selection[2] = x;
        selection[3] = y;
    }
    refresh();
});

elem.addEventListener("mouseup", (event) => {
    if (selection !== null) {
        // send selection to Python
        input.value = JSON.stringify(box());
        input.dispatchEvent(new Event("change"));
        // reset selection
        selection = null;
        refresh();
    }
});

refresh();
""",
)
