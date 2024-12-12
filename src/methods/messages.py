STOP_CHARACTERS = [
    "_",
    "*",
    "[",
    "]",
    "(",
    ")",
    "~",
    "`",
    ">",
    "#",
    "+",
    "-",
    "=",
    "|",
    "{",
    "}",
    ".",
    "!"
]


def md_replace_text(text: str) -> str:
    """
    Replacing text for MarkdownV2

    :param text: Text to replace
    :return: Replaced text
    """

    text = str(text)

    for character in STOP_CHARACTERS:
        if character in text:
            text = text.replace(character, f"\\{character}")

        if "42777" in text:
            text = text.replace("42777", " ")

    return text


def text_replace(text: str, **kwargs: dict) -> str:
    """
    Replace variable in json text

    :param text: Text to be replaced
    :param kwargs: Variables to replace
    """

    for element in kwargs:
        text = text.replace("{" f"{element}" "}", str(kwargs[element]))

    return text
