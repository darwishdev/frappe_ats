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


def to_typed_dict[T](model_instance: BaseModel | dict[Any, Any] | Enum | str | bool | int | float | list | dict | None, target_type: T) -> T:
    """
    Converts a Pydantic model (or other types) to a dict and casts it to the target TypedDict.
    Handles BaseModel, primitives, lists, and nested structures.

    :param model_instance: The value to convert (BaseModel, str, bool, int, list, dict, etc.)
    :param target_type: The TypedDict class you want the consumer to see
    """
    # Handle None
    if model_instance is None:
        return cast(T, None)

    # Handle primitives (str, bool, int, float)
    if isinstance(model_instance, (str, bool, int, float)):
        return cast(T, model_instance)

    # Handle lists
    if isinstance(model_instance, list):
        result = []
        for item in model_instance:
            if isinstance(item, BaseModel):
                result.append(item.model_dump())
            elif isinstance(item, (list, dict)):
                result.append(to_typed_dict(item, type(item)))
            else:
                result.append(item)
        return cast(T, result)

    # Handle dicts
    if isinstance(model_instance, dict):
        result = {}
        for key, value in model_instance.items():
            if isinstance(value, BaseModel):
                result[key] = value.model_dump()
            elif isinstance(value, (list, dict)):
                result[key] = to_typed_dict(value, type(value))
            else:
                result[key] = value
        return cast(T, result)

    # Handle BaseModel
    if isinstance(model_instance, BaseModel):
        # Check if it has 'items' attribute (like list wrappers)
        if hasattr(model_instance, 'items'):
            items = getattr(model_instance, 'items')
            return cast(T, to_typed_dict(items, list))
        return cast(T, model_instance.model_dump())

    # Fallback - return as-is
    return cast(T, model_instance)
