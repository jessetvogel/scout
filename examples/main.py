from pathlib import Path
import random

import pandas as pd

from scout import App
from scout import DataSource

data = pd.DataFrame(
    [
        {
            "x": random.randint(0, 100),
            "y": random.randint(0, 100),
            "color": random.choice(["red", "green", "blue", "yellow", "orange"]),
        }
        for _ in range(100)
    ]
)


class MyData(DataSource):
    def params(self) -> dict[str, list[str]]:
        return {
            "size": ["100", "250", "1000"],
        }

    def data(self, **kwargs: str) -> pd.DataFrame:
        size = int(kwargs["size"])
        return pd.read_csv(Path(__file__).parent / "data.csv")[:size]


def main():
    app = App(MyData())
    app.run()


if __name__ == "__main__":
    main()
