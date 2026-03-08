from typing import Any

from slash.basic import DataTable
from slash.html import Div

from scout.views import View, ViewContext


class TableView(View, Div):
    def __init__(self, ctx: ViewContext) -> None:
        View.__init__(self, ctx)
        Div.__init__(self, table := DataTable(tuple(ctx.data.keys())))

        self._table = table

        self.style({"background-color": "var(--bg-dark)", "width": "100%", "height": "100%"})

    def refresh(self) -> None:
        self._table.set_keys(tuple(self.ctx.data.keys()))
        self._table.set_max_rows(self.ctx.height // 37 - 2)
        self._table.set_data(tuple(row for i, row in self.ctx.data.iterrows() if self.ctx.mask[i]))  # type: ignore

    def get_state(self) -> Any:
        return {}

    def set_state(self, state: Any) -> None:
        pass
