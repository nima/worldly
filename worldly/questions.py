import dataclasses
import typing

@dataclasses.dataclass
class Question:
    dimension: str
    question: typing.Callable[[str, typing.Any, str], str]
    group_by: typing.Callable[[typing.Any], typing.Any] = lambda _: _
    filter_out: typing.Callable[[typing.Any], bool] = None
