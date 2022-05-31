from zparse.tokenizers import BaseTokenizer

from zparse.tokenizers import Token # TODO: remove

# FIXME
class BaseParser:
    def __init__(self, code: str):
        self.code = code


# FIXME
def make_parser(
    code: str,
    base: type=BaseParser,
    name: str='AnonymousParser',
    tok_base: type=BaseTokenizer,
    tok_name: str='AnonymousTokenizer',
) -> type:
    class AnonymousParser(BaseParser):
        def parse(self):
            return start([
                stmt(assign_stmt(
                    Token('a', x, 0, 0, 0),
                    expr(None, None, [
                        expr(Token('1', y, 0, 0, 0), None, [], None),
                        expr(None, None, [
                            expr(Token('3', y, 0, 0, 0), None, [], None),
                            expr(Token('5', y, 0, 0, 0), None, [], None),
                        ], None),
                    ], None)
                ), v()),
                stmt(None, print_stmt(
                    Token('print', z, 0, 0, 0),
                    expr(None, None, [
                        expr(None, Token('a', x, 0, 0, 0), [], None),
                        expr(Token('2', y, 0, 0, 0), None, [], None)
                    ], Token('**', w, 0, 0, 0)),
                )),
            ])
    return AnonymousParser

class x: name = 'NAME'
class y: name = 'INT'
class z: name = 'PRINT'
class w: name = 'POW'
class v: __repr__ = lambda s: 'None'

class start:
    def __init__(self, stmt): self.stmt = stmt
    def __repr__(self): return 'start()'

class stmt:
    def __init__(self, assign_stmt, print_stmt):
        self.assign_stmt, self.print_stmt = assign_stmt, print_stmt
    def __repr__(self): return 'stmt()'

class print_stmt:
    def __init__(self, PRINT, expr):
        self.PRINT, self.expr = PRINT, expr
    def __repr__(self):
        return 'print_stmt()'

class assign_stmt:
    def __init__(self, NAME, expr):
        self.NAME, self.expr = NAME, expr
    def __repr__(self):
        return 'assign_stmt()'

class expr:
    def __init__(self, INT, NAME, expr, POW):
        self.INT, self.NAME, self.expr, self.POW = INT, NAME, expr, POW
    def __repr__(self):
        return 'expr()'