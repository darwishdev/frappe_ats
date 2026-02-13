from typing import Type, Type, Any, TypedDict, cast, get_type_hints
from pydantic import BaseModel
from typing import Any, Iterable, Sequence
def pick_keys(row: dict[str, Any], keys: Iterable[str]) -> dict[str, Any]:
    """
    Return a new dict with only the specified keys from `row` using .get().
    Missing keys will have value None.

    Example:
        row = {"a": 1, "b": 2, "c": 3}
        pick_keys(row, ["a", "c", "x"])
        => {"a": 1, "c": 3, "x": None}
    """
    return {key: row.get(key) for key in keys}

def pick_keys_from_rows(rows: Sequence[dict[str, Any]], keys: Iterable[str]) -> list[dict[str, Any]]:
    """
    Return a list of dicts where each dict contains only the specified keys from the corresponding row.

    Example:
        rows = [{"a": 1, "b": 2}, {"a": 3, "b": 4, "c": 5}]
        pick_keys_from_rows(rows, ["a"])
        => [{"a": 1}, {"a": 3}]
    """
    return [pick_keys(row, keys) for row in rows or []]


def to_typed_dict[T](model_instance: BaseModel, target_type: T) -> T:
    """
    Converts a Pydantic model to a dict and casts it to the target TypedDict.

    :param model_instance: The Pydantic model object (or string)
    :param target_type: The TypedDict class you want the consumer to see
    """
    return cast(T, model_instance.model_dump())



def create_typed_dict_from_model(model: Type[BaseModel]) -> type:
    """
    Dynamically creates a TypedDict from a Pydantic BaseModel.
    """
    hints = get_type_hints(model)
    # Use functional syntax: TypedDict(name, fields_dict)
    return TypedDict(f"{model.__name__}Dict", hints)  # type: ignore
