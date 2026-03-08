from typing import Any

from slash.basic import Checkbox, DataTable
from slash.core import Elem
from slash.html import Span
from slash.layout import Column

from scout.views import View, ViewContext


class TableView(View, DataTable):
    def __init__(self, ctx: ViewContext) -> None:
        View.__init__(self, ctx)
        DataTable.__init__(self, tuple(ctx.data.keys()))

    def refresh(self) -> None:
        # self.set_keys(tuple(self.ctx.data.keys()))
        self.set_max_rows(self.ctx.height // 37 - 2)
        self.set_data(tuple(row for i, row in self.ctx.data.iterrows() if self.ctx.mask[i]))  # type: ignore

    def get_state(self) -> Any:
        return {"keys": self._keys}

    def set_state(self, state: Any) -> None:
        self.set_keys(state["keys"])

    def settings(self) -> Elem:
        checkboxes: list[Checkbox] = []
        for key in self.ctx.data.keys():
            checkboxes.append(Checkbox(key, checked=key in self._keys).onclick(lambda: update()))

        def update() -> None:
            self.set_keys([key for key, checkbox in zip(self.ctx.data.keys(), checkboxes) if checkbox.checked])
            self.ctx.store_state()

        return Column(
            Span("Columns").style({"font-weight": "bold", "text-align": "center"}),
            *checkboxes,
        ).style({"width": "100%"})
