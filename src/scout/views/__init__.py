from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import pandas as pd
from slash.core import Elem

from scout.utils import Box


@dataclass
class ViewContext:
    data: pd.DataFrame
    """Current data."""
    mask: pd.Series
    """Current mask. Editable."""
    box: Box
    """Box of view."""
    width: int
    """Width of the view in pixels."""
    height: int
    """Height of the view in pixels."""
    store_state: Callable[[], None]
    """Store state."""
    refresh_views: Callable[[], None]
    """Refresh views."""


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

    @abstractmethod
    def settings(self) -> Elem:
        """Settings element."""
