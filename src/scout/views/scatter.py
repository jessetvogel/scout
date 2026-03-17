from typing import Any, cast

import pandas as pd
from colorswan import OkColor
from colorswan.okcolor import Oklch
from pandas.api.types import is_numeric_dtype
from slash._utils import default_color
from slash.basic import Axes, Scatter
from slash.core import Elem
from slash.html import Div, Option, Select, Span
from slash.layout import Column, Panel, Row

from scout.components.select_rect import SelectRect
from scout.utils import Box
from scout.views import View, ViewContext

PAD = 16

CONVERTER = OkColor()


class ScatterView(View, Panel):
    def __init__(self, ctx: ViewContext) -> None:
        View.__init__(self, ctx)
        Panel.__init__(self)

        self._setup()

    def _setup(self) -> None:
        self.style({"width": "100%", "height": "100%", "box-sizing": "border-box", "padding": f"{PAD}px"})

        df = self.ctx.data

        keys_all = tuple(df.keys())
        keys_num = tuple(key for key in keys_all if is_numeric_dtype(df.dtypes[key]))

        self._select_x = Select([Option(key) for key in keys_num]).style({"text-align": "center"})
        self._select_y = Select([Option(key) for key in keys_num]).style({"text-align": "center"})
        self._select_c = Select([Option("-", "")] + [Option(key) for key in keys_all]).style({"text-align": "center"})

        self.x_key = keys_num[0]
        self.y_key = keys_num[min(1, len(keys_num) - 1)]
        self.c_key = None

        self._select_x.onchange(self._onchange_select)
        self._select_y.onchange(self._onchange_select)
        self._select_c.onchange(self._onchange_select)

    @property
    def x_key(self) -> str:
        return self._select_x.value

    @x_key.setter
    def x_key(self, key: str) -> None:
        self._select_x.value = key

    @property
    def y_key(self) -> str:
        return self._select_y.value

    @y_key.setter
    def y_key(self, key: str) -> None:
        self._select_y.value = key

    @property
    def c_key(self) -> str | None:
        c = self._select_c.value
        return c if c != "" else None

    @c_key.setter
    def c_key(self, key: str | None) -> None:
        self._select_c.value = key if key is not None else ""

    def _onchange_select(self) -> None:
        self.ctx.store_state()
        self.refresh()

    def refresh(self) -> None:
        df = self.ctx.data

        width = self.ctx.width - PAD - PAD
        height = self.ctx.height - PAD - PAD - 54

        self._axes = Axes(width=width, height=height).set_grid(True)

        self.clear()
        self.append(
            Column(
                Div(
                    self._axes,
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
                    .onchange(self._set_selection),
                ).style({"position": "relative"}),
                Row(
                    Column(
                        Span("x-axis").style({"font-weight": "bold", "font-size": "12px", "margin-bottom": "4px"}),
                        self._select_x,
                    ).style({"flex": "1", "text-align": "center", "min-width": "0"}),
                    Column(
                        Span("y-axis").style({"font-weight": "bold", "font-size": "12px", "margin-bottom": "4px"}),
                        self._select_y,
                    ).style({"flex": "1", "text-align": "center", "min-width": "0"}),
                    Column(
                        Span("color").style({"font-weight": "bold", "font-size": "12px", "margin-bottom": "4px"}),
                        self._select_c,
                    ).style({"flex": "1", "text-align": "center", "min-width": "0"}),
                ).style({"gap": "16px", "justify-content": "center"}),
            ).style({"gap": "0px"})
        )

        if self.c_key is None:
            self._add_scatter(df)
            self._axes.set_legend(False)
        else:
            if not is_numeric_dtype(df.dtypes[self.c_key]):
                c_values = df[self.c_key].unique().tolist()
                for i, c_value in enumerate(c_values):
                    self._add_scatter(
                        df.loc[df[self.c_key] == c_value],
                        label=str(c_value),
                        color=default_color(i),
                    )
                self._axes.set_legend(True)
            else:
                self._add_scatter(df, color_key=self.c_key)
                self._axes.set_legend(False)

        # axes.set_xlabel(x_key)
        # axes.set_ylabel(y_key)

        if self._axes.is_mounted():
            self._axes.render()
        else:
            self._axes.onmount(lambda: self._axes.render())

    def get_state(self) -> Any:
        return {
            "x": self.x_key,
            "y": self.y_key,
            "c": self.c_key,
        }

    def set_state(self, state: Any) -> None:
        df = self.ctx.data

        if state["x"] in df:
            self.x_key = state["x"]
        if state["y"] in df:
            self.y_key = state["y"]
        if state["c"] in df:
            self.c_key = state["c"]

    def _set_selection(self, box: Box) -> None:
        df = self.ctx.data
        mask = self.ctx.mask

        # Convert box coordinates to data coordinates
        x_min, y_max = self._axes._uv_to_xy(box.x, box.y)
        x_max, y_min = self._axes._uv_to_xy(box.x + box.w, box.y + box.h)

        # Set mask
        if x_min == x_max and y_min == y_max:
            # If just clicked
            mask[:] = True
        else:
            mask[:] = df[self.x_key].between(x_min, x_max) & df[self.y_key].between(y_min, y_max)

        # Refresh views
        self.ctx.refresh_views()

    def _add_scatter(
        self,
        df: pd.DataFrame,
        *,
        label: str | None = None,
        color: str | None = None,
        color_key: str | None = None,
    ) -> None:
        mask = self.ctx.mask

        rows_a = df.loc[mask]
        rows_b = df.loc[~mask]

        if color is not None:
            color_a = color
            color_b = color
        elif color_key is not None:
            c_col = df[color_key]
            c_min, c_max = c_col.min(), c_col.max()
            color_a = color_gradient((rows_a[color_key] - c_min) / (c_max - c_min))
            color_b = color_gradient((rows_b[color_key] - c_min) / (c_max - c_min))
        else:
            color_a = None
            color_b = None

        self._axes.add_plot(
            Scatter(
                rows_a[self.x_key].tolist(),
                rows_a[self.y_key].tolist(),
                color=color_a,
                label=label,
            )
        )
        self._axes.add_plot(
            Scatter(
                rows_b[self.x_key].tolist(),
                rows_b[self.y_key].tolist(),
                color=color_b,
                opacity=0.33,
            )
        )

    def settings(self) -> Elem:
        return Div()


converter = OkColor()

palette = ["#1d4fa6", "#19cf86", "#ffee00", "#e3440a", "#990000"]
palette_oklch: list[Oklch] = [cast(Oklch, converter.convert(c, return_type="oklch")) for c in palette]


def color_gradient(values: list[float]) -> list[str]:
    n = len(palette_oklch)
    colors = []
    for value in values:
        # Compute position along the palette
        pos = value * (n - 1)
        i = int(pos)
        t = pos - i
        if i >= n - 1:
            colors.append(f"oklch({palette_oklch[-1].L:.4f} {palette_oklch[-1].C:.4f} {palette_oklch[-1].h:.4f})")
            continue

        start = palette_oklch[i]
        end = palette_oklch[i + 1]

        # Interpolate L, C, H
        L = start.L + t * (end.L - start.L)
        C = start.C + t * (end.C - start.C)
        dh = (end.h - start.h + 180) % 360 - 180
        H = (start.h + t * dh) % 360

        colors.append(f"oklch({L:.4f} {C:.4f} {H:.4f})")

    return colors
