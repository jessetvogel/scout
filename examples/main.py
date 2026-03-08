import random

import pandas as pd

from scout import App

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


def main():
    app = App(data)
    app.run()


if __name__ == "__main__":
    main()
