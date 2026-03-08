from dataclasses import dataclass
from typing import Any, Self


@dataclass
class Box:
    x: int
    y: int
    w: int
    h: int

    def encode(self) -> Any:
        return [self.x, self.y, self.w, self.h]

    @classmethod
    def decode(cls, data: Any) -> Self:
        return cls(x=data[0], y=data[1], w=data[2], h=data[3])
