def escape_dollar_quoted_json(value: str) -> str:
    return value.replace("$$", "$ $")
