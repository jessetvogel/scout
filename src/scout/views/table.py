from typing import Any

from slash.basic import DataTable

from scout.views import View, ViewContext


class TableView(View, DataTable):
    def __init__(self, ctx: ViewContext) -> None:
        View.__init__(self, ctx)
        DataTable.__init__(self, tuple(ctx.data.keys()))

    def refresh(self) -> None:
        self.set_keys(tuple(self.ctx.data.keys()))
        self.set_max_rows(self.ctx.height // 37 - 2)
        self.set_data(tuple(row for i, row in self.ctx.data.iterrows() if self.ctx.mask[i]))  # type: ignore

    def get_state(self) -> Any:
        return {}

    def set_state(self, state: Any) -> None:
        pass
