from typing import Any

from pandas.api.types import is_numeric_dtype
from slash.basic import Axes, Scatter
from slash.html import Option, Select, Span
from slash.layout import Column, Panel, Row

from scout.views import View, ViewContext

PAD = 16


class ScatterView(View, Panel):
    def __init__(self, ctx: ViewContext) -> None:
        View.__init__(self, ctx)
        Panel.__init__(self)

        df = self.ctx.data
        self._keys: tuple[str, ...] = tuple(key for key in df if is_numeric_dtype(df.dtypes[key]))  # type: ignore
        self._x_key = self._keys[0]
        self._y_key = self._keys[1]

        self._select_x_key = Select([Option(key) for key in self._keys]).style({"text-align": "center"})
        self._select_y_key = Select([Option(key) for key in self._keys]).style({"text-align": "center"})
        self._select_x_key.value = self._x_key
        self._select_y_key.value = self._y_key

        self._select_x_key.onchange(self.refresh)
        self._select_y_key.onchange(self.refresh)

        self.style({"width": "100%", "height": "100%", "box-sizing": "border-box", "padding": f"{PAD}px"})

    def refresh(self) -> None:
        self._x_key = self._select_x_key.value
        self._y_key = self._select_y_key.value

        width = self.ctx.width - PAD - PAD
        height = self.ctx.height - PAD - PAD - 50

        self.clear()
        self.append(
            Column(
                axes := Axes(width=width, height=height),
                Row(
                    Column(
                        Span("x-axis").style({"font-weight": "bold", "font-size": "12px"}),
                        self._select_x_key,
                    ).style({"flex-grow": "1", "text-align": "center"}),
                    Column(
                        Span("y-axis").style({"font-weight": "bold", "font-size": "12px"}),
                        self._select_y_key,
                    ).style({"flex-grow": "1", "text-align": "center"}),
                ).style({"gap": "16px", "justify-content": "center"}),
            ).style({"gap": "0px"})
        )

        axes.add_plot(Scatter(self.ctx.data[self._x_key], self.ctx.data[self._y_key]))  # type: ignore
        # axes.set_xlabel(x_key)
        # axes.set_ylabel(y_key)
        axes.render()

    def get_state(self) -> Any:
        return {}

    def set_state(self, state: Any) -> None:
        pass
