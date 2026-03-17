from typing import Any

from slash.core import Elem
from slash.events import ChangeEvent
from slash.html import Div, Input, Option, Select
from slash.layout import Panel

from scout.views import View, ViewContext


class FilterView(View, Panel):
    def __init__(self, ctx: ViewContext) -> None:
        View.__init__(self, ctx)
        Panel.__init__(self)

        self._keys = tuple(ctx.data.keys())

        self.key = self._keys[0]
        self.value = None

        self._setup()

    @property
    def key(self) -> str | None:
        return self._key

    @key.setter
    def key(self, key: str | None) -> None:
        self._key = key

    @property
    def value(self) -> str | None:
        return self._value

    @value.setter
    def value(self, value: str | None) -> None:
        self._value = value

    def _setup(self) -> None:
        self.clear()
        self.style(
            {
                "display": "flex",
                "flex-direction": "column",
                "gap": "8px",
                "height": "100%",
                "box-sizing": "border-box",
                "justify-content": "center",
            }
        )
        self.append(
            select := Select([Option("-", value="")] + [Option(key) for key in self._keys]).onchange(
                self._onchange_select
            )
        )
        self.append(input := Input(placeholder="Filter value").onchange(self._onchange_input))

        select.value = self.key or ""
        input.value = self.value or ""

    def _onchange_select(self, event: ChangeEvent) -> None:
        if event.value == "":
            self.key = None
        else:
            self.key = event.value

        self.ctx.store_state()
        self._update_selection()

    def _onchange_input(self, event: ChangeEvent) -> None:
        if event.value == "":
            self.value = None
        else:
            self.value = event.value

        self.ctx.store_state()
        self._update_selection()

    def _update_selection(self) -> None:
        if self.value is None:
            self.ctx.mask[:] = True
        else:
            self.ctx.mask[:] = self.ctx.data[self.key] == self.value
        self.ctx.refresh_views()

    def get_state(self) -> Any:
        return {"key": self.key, "value": self.value}

    def set_state(self, state: Any) -> None:
        self.key = state["key"]
        self.value = state["value"]

    def settings(self) -> Elem:
        return Div()
