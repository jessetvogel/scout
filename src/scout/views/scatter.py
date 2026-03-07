from typing import Any

from slash.basic import Axes, Scatter
from slash.core import Session
from slash.layout import Panel

from scout.views import View, ViewContext


class ScatterView(View, Panel):
    def __init__(self, ctx: ViewContext) -> None:
        View.__init__(self, ctx)
        Panel.__init__(self)

        self.style({"width": "100%", "height": "100%", "box-sizing": "border-box", "padding": "16px"})

    def refresh(self) -> None:
        x_key = "x"
        y_key = "y"

        width = self.ctx.width - 32
        height = self.ctx.height - 32

        self.clear()
        self.append(axes := Axes(width=width, height=height))

        axes.add_plot(
            Scatter(
                self.ctx.data[x_key],
                self.ctx.data[y_key],
            )
        )
        axes.set_xlabel(x_key)
        axes.set_ylabel(y_key)
        axes.render()

        Session.require().log("refresh!")

    def get_state(self) -> Any:
        return {}

    def set_state(self, state: Any) -> None:
        pass
