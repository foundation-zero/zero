def ensure_list[T](x: T | list[T]) -> list[T]:
    """Provide list or single object, return list in both cases"""
    return x if isinstance(x, list) else [x]
