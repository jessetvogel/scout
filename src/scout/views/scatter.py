from typing import Any

from pandas.api.types import is_numeric_dtype
from slash.basic import Axes, Scatter
from slash.html import Div, Option, Select, Span
from slash.layout import Column, Panel, Row

from scout.components import SelectRect
from scout.utils import Box
from scout.views import View, ViewContext

PAD = 16


class ScatterView(View, Panel):
    def __init__(self, ctx: ViewContext) -> None:
        View.__init__(self, ctx)
        Panel.__init__(self)

        df = self.ctx.data
        self._keys: tuple[str, ...] = tuple(key for key in df if is_numeric_dtype(df.dtypes[key]))
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
        height = self.ctx.height - PAD - PAD - 54

        self._axes = Axes(width=width, height=height).set_grid(True)

        select_rect = (
            SelectRect()
            .style(
                {
                    "position": "absolute",
                    "width": f"{width}px",
                    "height": f"{height}px",
                    "top": "0px",
                    "left": "0px",
                }
            )
            .onchange(self._set_selection)
        )

        self.clear()
        self.append(
            Column(
                Div(self._axes, select_rect).style({"position": "relative"}),
                Row(
                    Column(
                        Span("x-axis").style({"font-weight": "bold", "font-size": "12px", "margin-bottom": "4px"}),
                        self._select_x_key,
                    ).style({"flex-grow": "1", "text-align": "center"}),
                    Column(
                        Span("y-axis").style({"font-weight": "bold", "font-size": "12px", "margin-bottom": "4px"}),
                        self._select_y_key,
                    ).style({"flex-grow": "1", "text-align": "center"}),
                ).style({"gap": "16px", "justify-content": "center"}),
            ).style({"gap": "0px"})
        )

        self._axes.add_plot(
            Scatter(
                self.ctx.data.loc[self.ctx.mask, self._x_key].tolist(),
                self.ctx.data.loc[self.ctx.mask, self._y_key].tolist(),
            )
        )

        self._axes.add_plot(
            Scatter(
                self.ctx.data.loc[~self.ctx.mask, self._x_key].tolist(),
                self.ctx.data.loc[~self.ctx.mask, self._y_key].tolist(),
                opacity=0.5,
            )
        )

        # axes.set_xlabel(x_key)
        # axes.set_ylabel(y_key)

        self._axes.render()

    def get_state(self) -> Any:
        return {}

    def set_state(self, state: Any) -> None:
        pass

    def _set_selection(self, box: Box) -> None:
        # Convert box coordinates to data coordinates
        x_min, y_max = self._axes._uv_to_xy(box.x, box.y)
        x_max, y_min = self._axes._uv_to_xy(box.x + box.w, box.y + box.h)

        # Set mask
        if x_min == x_max and y_min == y_max:
            # If just clicked
            self.ctx.mask[:] = True
        else:
            self.ctx.mask[:] = self.ctx.data[self._x_key].between(x_min, x_max) & self.ctx.data[self._y_key].between(
                y_min, y_max
            )

        # Refresh views
        self.ctx.refresh_views()

    # def _uv_to_xy(self, u: float, v: float) -> tuple[float, float]:
    #     """Convert SVG uv-coordinates to abstract xy-coordinates."""
    #     x = self._view.x_min + (self._view.x_max - self._view.x_min) * (u - self._view.u_min) / (
    #         self._view.u_max - self._view.u_min
    #     )
    #     y = self._view.y_min + (self._view.y_max - self._view.y_min) * (v - self._view.v_min) / (
    #         self._view.v_max - self._view.v_min
    #     )
    #     return x, y
