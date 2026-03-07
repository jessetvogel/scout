from slash import App as SlashApp
from slash.core import Session

from scout.components import SelectGrid


class App:
    def __init__(self) -> None:
        pass

    def run(self) -> None:
        app = SlashApp()
        app.add_route("/", home)
        app.run()


def home():
    return (
        SelectGrid(5, 4)
        .style({"margin": "100px"})
        .onchange(
            lambda box: Session.require().log(
                "box",
                details=f"x = {box.x}, y = {box.y}, w = {box.w}, h = {box.h}",
            )
        )
    )
