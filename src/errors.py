from __future__ import annotations

class GrammarError(Exception):
    def __init__(self, msg: str, tokens: tuple[Token]=()):
        self.msg = msg
        self.tokens = tokens

class TokenError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

class ParseError(Exception):
    def __init__(self, msg: str, tokens: tuple[Token]=()):
        self.msg = msg
        self.tokens = tokens