import base64
import json
import random

import pandas as pd
from slash import App as SlashApp
from slash.core import Elem, Session
from slash.layout import Column

from scout._layout import Layout


class App:
    def __init__(self) -> None:
        pass

    def run(self) -> None:
        app = SlashApp()
        app.add_route("/", home)
        app.run()


def home() -> Elem:
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
    layout = Layout(data, cols=5, rows=4)

    layout.set_state(
        {
            "cols": 5,
            "rows": 4,
            "views": [
                [[0, 0, 2, 2], "TableView", []],
                [[2, 0, 2, 2], "ScatterView", []],
                [[0, 2, 4, 2], "EmptyView", []],
            ],
        }
    )

    # Set state
    state = Session.require().location.query.get("layout", None)
    if state is not None:
        layout.set_state(json.loads(base64.b64decode(state).decode()))

    # Render

    return Column(
        layout,
    ).style(
        {
            "gap": "32px",
            "align-items": "center",
            "margin-top": "32px",
        }
    )
