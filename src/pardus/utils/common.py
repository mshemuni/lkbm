import re
from typing import Dict, Optional

from pardus.utils.error import NopeError

NOPES = [
    "/", " -", "- ", "\"", " ",
    "'", "(", ")" ",", ";",
    "&", ">", "<", "|",
    "=", "[", "]", "#", "!", "?",
    ":", "{", "}", "%", "~", "*",
]

COMMANDS = {
    "apt": {
        "repositories": {
            "get": "COMMAND",
            "set": "COMMAND",
        },
        "update": "COMMAND",
        "upgrade": "COMMAND",
        "list": {
            "": "COMMAND",
            "installed": "COMMAND",
            "upgradeable": "COMMAND",
        },
        "install": "COMMAND",
        "reinstall": "COMMAND",
        "remove": "COMMAND",
        "purge": "COMMAND",
        "search": "COMMAND",
        "show": "COMMAND",
        "autoremove": "COMMAND",
        "magic": "COMMAND",

    }
}


def clear(text: str) -> str:
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)


def is_valid_source_line(line: str) -> None:
    pattern = re.compile(r'^(deb|deb-src)\s+'
                         r'(\[.*?\]\s+)?'
                         r'https?://\S+\s+'
                         r'\S+\s+'
                         r'(\S+.*)?$')

    if not bool(pattern.match(line.strip())):
        raise ValueError("Bad source")


def option_matcher(option: str) -> Optional[Dict[str, str]]:
    if not option:
        return None

    options_to_return = {}
    options = option.strip().lstrip("[").rstrip("]")

    for option in options.split():
        key, value = option.split("=")
        options_to_return[key] = value

    return options_to_return


def escape_string(name: str) -> None:
    if any(nope in name for nope in NOPES):
        raise NopeError(f"Not cool! {name}")
