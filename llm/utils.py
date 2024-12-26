import re

from typing import Tuple
from collections import deque

CODE_BLOCK_PLACEHOLDER = "<CODE_BLOCK>"


def extract_code_blocks(text: str) -> Tuple[deque, str]:
    """
    Extract code blocks from a string and return a queue of code blocks and a string with
    all code blocks replaced by a placeholder <CODE_BLOCK>.

    :param text: The string to extract code blocks from.
    :return: A tuple of a queue of code blocks and a string where all code blocks have been
             replaced by a placeholder.
    """
    text_no_code, _ = re.subn(
        r"```.*?```",
        CODE_BLOCK_PLACEHOLDER,
        text,
        flags=re.DOTALL | re.MULTILINE,
        count=10,
    )
    pattern = r"^```(?:\w+)?\s*\n(.*?)(?=^```)```"
    result = re.finditer(pattern, text, re.DOTALL | re.MULTILINE)
    queue = deque([])
    for match in result:
        queue.append(match.group(0))
    return queue, text_no_code


def replace_code_blocks(queue: deque, text: str) -> str:
    """
    Replace all code blocks in a string with the first code block in the queue.

    :param queue: The queue of code blocks to replace.
    :param text: The string to replace code blocks in.
    :return: A string with all code blocks replaced by the first code block in the queue.
    """
    while queue:
        text = text.replace(CODE_BLOCK_PLACEHOLDER, queue.popleft(), 1)
    return text
