from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import pandas as pd
from slash.core import Elem
from slash.html import Span
from slash.layout import Panel

from scout.utils import Box


@dataclass
class ViewContext:
    box: Box
    """Box."""
    width: int
    """Width of the view in pixels."""
    height: int
    """Height of the view in pixels."""
    data: pd.DataFrame
    """Data."""
    mask: pd.Series
    """Selection mask."""


class View(ABC, Elem):
    def __init__(self, ctx: ViewContext) -> None:
        self._ctx = ctx

    @property
    def ctx(self) -> ViewContext:
        return self._ctx

    def refresh(self) -> None:
        """Refreshes the view."""

    @abstractmethod
    def get_state(self) -> Any:
        """Returns the current state."""

    @abstractmethod
    def set_state(self, state: Any) -> None:
        """Sets the current state."""


class EmptyView(View, Panel):
    def __init__(self, ctx: ViewContext) -> None:
        View.__init__(self, ctx)
        Panel.__init__(self)

        self.style({"width": "100%", "height": "100%", "box-sizing": "border-box", "padding": "16px"})

        self.append(Span("empty panel").style({"font-style": "italic"}))

    def get_state(self) -> Any:
        """Returns the current state."""

    def set_state(self, state: Any) -> None:
        """Sets the current state."""


__all__ = ["View", "EmptyView"]
