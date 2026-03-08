from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class DataSource(ABC):
    @abstractmethod
    def params(self) -> dict[str, list[str]]:
        """Returns parameters and list of options."""

    @abstractmethod
    def data(self, **kwargs: Any) -> pd.DataFrame:
        """Returns data."""
