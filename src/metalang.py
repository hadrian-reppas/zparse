import enum
import typing

from zparse.errors import GrammarError

class TokenKind(enum.Enum):
    EOF     = enum.auto()
    ID      = enum.auto()
    CODE    = enum.auto()
    STRING  = enum.auto()
    NEWRULE = enum.auto()
    COLON   = enum.auto()
    LPAREN  = enum.auto()
    RPAREN  = enum.auto()
    OR      = enum.auto()
    STAR    = enum.auto()
    PLUS    = enum.auto()
    QMARK   = enum.auto()
    DOT     = enum.auto()
    AT      = enum.auto()
    BAM     = enum.auto()
    EQUALS  = enum.auto()
    DASH    = enum.auto()

# TODO: maybe keep track of last line and column
class Token(typing.NamedTuple):
    kind: TokenKind
    text: str
    line: int
    column: int
    code: str
    def __repr__(self):
        return f'Token({self.kind.name}, {self.text!r})'

class Tokenizer:
    def __init__(self, code: str) -> None:
        self.code = code
        self.slow = 0
        self.fast = 0
        self.line = 1
        self.column = 0
        self.line_slow = 1
        self.column_slow = 0
        self.toks = []
    def peek_char(self) -> str:
        if self.fast == len(self.code):
            return ''
        return self.code[self.fast]
    def next_char(self) -> str:
        if self.fast == len(self.code):
            return ''
        c = self.code[self.fast]
        if c == '\n':
            self.line += 1
            self.column = 0
        else:
            self.column += 1
        self.fast += 1
        return c
    def chars_left(self) -> int:
        return len(self.code) - self.fast
    def make_token(self, kind: TokenKind) -> Token:
        text = self.code[self.slow:self.fast]
        token = Token(
            kind,
            text,
            self.line_slow,
            self.column_slow,
            self.code
        )
        self.line_slow = self.line
        self.column_slow = self.column
        self.slow = self.fast
        if token.kind != TokenKind.NEWRULE:
            self.toks.append(token)
        return token
    def tokens(self) -> typing.Generator[Token, None, None]:
        if self.peek_char().isalpha() or self.peek_char() == '_':
            yield self.make_token(TokenKind.NEWRULE)
        while True:
            if self.peek_char() == '':
                yield self.make_token(TokenKind.EOF)
                return
            elif self.peek_char().isspace():
                yield from self.handle_whitespace()
            elif self.peek_char().isalpha() or self.peek_char() == '_':
                yield self.handle_identifier()
            elif self.peek_char() == '{':
                yield self.handle_code()
            elif self.peek_char() == "'":
                yield self.handle_sq_string()
            elif self.peek_char() == '"':
                yield self.handle_dq_string()
            elif self.peek_char() == ':':
                self.next_char()
                yield self.make_token(TokenKind.COLON)
            elif self.peek_char() == '(':
                self.next_char()
                yield self.make_token(TokenKind.LPAREN)
            elif self.peek_char() == ')':
                self.next_char()
                yield self.make_token(TokenKind.RPAREN)
            elif self.peek_char() == '|':
                self.next_char()
                yield self.make_token(TokenKind.OR)
            elif self.peek_char() == '*':
                self.next_char()
                yield self.make_token(TokenKind.STAR)
            elif self.peek_char() == '+':
                self.next_char()
                yield self.make_token(TokenKind.PLUS)
            elif self.peek_char() == '?':
                self.next_char()
                yield self.make_token(TokenKind.QMARK)
            elif self.peek_char() == '.':
                self.next_char()
                yield self.make_token(TokenKind.DOT)
            elif self.peek_char() == '@':
                self.next_char()
                yield self.make_token(TokenKind.AT)
            elif self.peek_char() == '!':
                self.next_char()
                yield self.make_token(TokenKind.BAM)
            elif self.peek_char() == '=':
                self.next_char()
                yield self.make_token(TokenKind.EQUALS)
            elif self.peek_char() == '-':
                self.next_char()
                yield self.make_token(TokenKind.DASH)
            elif self.peek_char() == '#':
                self.consume_comment()
            else:
                self.unknown_char()
    def handle_whitespace(self) -> typing.Generator[Token, None, None]:
        self.next_char()
        while self.peek_char().isspace():
            self.next_char()
        token = self.make_token(TokenKind.NEWRULE)
        if (
            token.text.endswith('\n')
            and (self.peek_char().isalnum() or self.peek_char() == '_')
        ):
            self.toks.append(token)
            yield token
    def handle_identifier(self) -> Token:
        self.next_char()
        while self.peek_char().isalnum() or self.peek_char() == '_':
            self.next_char()
        return self.make_token(TokenKind.ID)
    def handle_code(self) -> Token:
        self.next_char()
        depth = 1
        while self.peek_char() != '}' or depth > 1:
            if self.peek_char() == "'":
                self.next_char()
                while self.peek_char() != "'":
                    if self.next_char() == '\\':
                        self.next_char()
                self.next_char()
            elif self.peek_char() == '"':
                self.next_char()
                while self.peek_char() != '"':
                    if self.next_char() == '\\':
                        self.next_char()
                self.next_char()
            elif self.peek_char() == '{':
                self.next_char()
                depth += 1
            elif self.peek_char() == '}':
                self.next_char()
                depth -= 1
            else:
                if self.next_char() == '':
                    self.unclosed_code()
        self.next_char()
        return self.make_token(TokenKind.CODE)
    def handle_sq_string(self) -> Token:
        self.next_char()
        while self.peek_char() != "'" and self.peek_char() != '':
            if self.next_char() == '\\':
                self.next_char()
        if self.next_char() == '':
            self.unclosed_string()
        return self.make_token(TokenKind.STRING)
    def handle_dq_string(self) -> Token:
        self.next_char()
        while self.peek_char() != '"' and self.peek_char() != '':
            if self.next_char() == '\\':
                self.next_char()
        if self.next_char() == '':
            self.unclosed_string()
        return self.make_token(TokenKind.STRING)
    def consume_comment(self):
        while self.peek_char() != '\n':
            self.next_char()
    def unknown_char(self):
        raise GrammarError(
            f'unknown char {self.peek_char()!r} on line '
            f'{self.line_slow} and column {self.column_slow}'
        )
    def unclosed_string(self):
        raise GrammarError(
            f'unclosed string literal starting on line '
            f'{self.line_slow} and column {self.column_slow}',
        )
    def unclosed_code(self):
        raise GrammarError(
            f'unclosed code snippet starting on line'
            f'{self.line_slow} and column {self.column_slow}',
        )


# TODO: come up with superclass for Tag, Directive, InlineCode, Predicate
#       so that type hints are list[Token | GrammarExpr | SOME_OTHER_TYPE]

class GrammarExpr:
    def to_regex(self, fragments: dict[str, str]) -> str:
        assert False, 'not implemented'
    def identifiers(self) -> set[str]:
        assert False, 'not implemented'
    def literals(self) -> set[str]:
        print(type(self))
        assert False, 'not implemented'

class Identifier(GrammarExpr):
    def __init__(self, token: Token):
        self.name = token.text
        self.token = token
    def __repr__(self):
        return f'Id({self.name!r})'
    def is_rule(self) -> bool:
        return not self.name.isupper()
    def is_token(self) -> bool:
        return self.name.isupper() and not self.name.startswith('_')
    def is_fragment(self) -> bool:
        return self.name.isupper() and self.name.startswith('_')
    def to_regex(self, fragments: dict[str, str]) -> str:
        if self.name not in fragments:
            raise GrammarError(
                f'fragment {self.name!r} is not defined',
                (self,),
            )
        return fragments[self.name]
    def identifiers(self) -> set[str]:
        return {self.name}
    def literals(self) -> set[str]:
        return set()

class StringLiteral(GrammarExpr):
    def __init__(self, token: Token):
        self.value = eval(token.text)
        self.token = token
    def __repr__(self):
        return f'Str({self.token.text})'
    def to_regex(self, fragments: dict[str, str]) -> str:
        escape = {'.', '^', '$', '*', '+', '?', '{', '}', '\\', '[', ']', '|'}
        return ''.join(
            '\\' + c if c in escape else c for c in self.value
        )
    def identifiers(self) -> set[str]:
        return set()
    def literals(self) -> set[str]:
        return {self.value}

class InlineCode:
    def __init__(self, token: Token):
        # TODO: self.value = ast.parse(token.text[1:-1].strip())
        self.token = token
    def __repr__(self):
        return 'Code()'

class Predicate:
    def __init__(self, code: InlineCode, qmark: Token):
        self.code = code # TODO: code.value must be an Expr
        self.qmark = qmark
    def __repr__(self):
        return 'Predicate()'

class Range(GrammarExpr):
    def __init__(
        self,
        low: StringLiteral,
        high: StringLiteral,
        dash: Token,
    ):
        self.low = low
        self.high = high
        self.dash = dash
    def __repr__(self):
        return f'Range({self.low.value!r}, {self.high.value!r})'
    def to_regex(self, fragments: dict[str, str]) -> str:
        low, high = self.low.value, self.high.value
        if ord(high) < ord(low):
            low, high = high, low
        if low == ']': low = '\\]'
        if high == ']': high = '\\]'
        if low == '^': low = '\\^'
        return f'[{low}-{high}]'
    def identifiers(self) -> set[str]:
        return set()
    def literals(self) -> set[str]:
        return set()

class Alias(GrammarExpr):
    def __init__(self, alias: Identifier, name: Identifier, dash: Token):
        self.name = name
        self.alias = alias
        self.dash = dash
    def __repr__(self):
        return f'Alias({self.alias.name!r}, {self.name.name!r})'
    def identifiers(self) -> set[str]:
        return {self.name}
    def literals(self) -> set[str]:
        return set()

class Any(GrammarExpr):
    def __init__(self, token: Token):
        self.token = token
    def __repr__(self):
        return 'Any()'
    def to_regex(self, fragments: dict[str, str]) -> str:
        return '.'
    def identifiers(self) -> set[str]:
        return set()
    def literals(self) -> set[str]:
        return set()

class Tag:
    def __init__(self, name: Identifier, at: Token):
        self.name = name
        self.at = at
    def __repr__(self):
        return f'Tag({self.name.name!r})'

class Directive:
    def __init__(self, name: Identifier, bam: Token):
        self.name = name
        self.bam = bam
    def __repr__(self):
        return f'Directive({self.name.name!r})'

class Alternative:
    def __init__(
        self,
        value: GrammarExpr,
        tag: typing.Optional[Tag],
        directives: list[Directive],
        code: InlineCode,
        predicate: Predicate,
    ):
        self.value = value
        self.tag = tag
        self.directives = directives
        self.code = code
        self.predicate = predicate
    def __repr__(self):
        return (
            f'Alternative({self.value}, {self.tag}, '
            f'{self.directives}, {self.code}, {self.predicate})'
        )
    
class Union(GrammarExpr):
    def __init__(self, values: list[GrammarExpr], ors: list[Token]):
        self.values = values
        self.ors = ors
    def __repr__(self):
        return f'Union({self.values})'
    def to_regex(self, fragments: dict[str, str]) -> str:
        mid = '|'.join(
            f'({value.to_regex(fragments)})' for value in self.values
        )
        return f'({mid})'
    def identifiers(self) -> set[str]:
        out = set()
        for value in self.values:
            out |= value.identifiers()
        return out
    def literals(self) -> set[str]:
        out = set()
        for value in self.values:
            out |= value.literals()
        return out

class Concatenation(GrammarExpr):
    def __init__(self, values: list[GrammarExpr]):
        self.values = values
    def __repr__(self):
        return f'Concat({self.values})'
    def to_regex(self, fragments: dict[str, str]) -> str:
        mid = ''.join(
            value.to_regex(fragments) for value in self.values
        )
        return f'({mid})'
    def identifiers(self) -> set[str]:
        out = set()
        for value in self.values:
            out |= value.identifiers()
        return out
    def literals(self) -> set[str]:
        out = set()
        for value in self.values:
            out |= value.literals()
        return out

class Optional(GrammarExpr):
    def __init__(self, value: GrammarExpr, qmark: Token):
        self.value = value
        self.qmark = qmark
    def __repr__(self):
        return f'Optional({self.value})'
    def to_regex(self, fragments: dict[str, str]) -> str:
        return f'({self.value.to_regex(fragments)})?'
    def identifiers(self) -> set[str]:
        return self.value.identifiers()
    def literals(self) -> set[str]:
        return self.value.literals()

class NongreedyOptional(GrammarExpr):
    def __init__(self, value: GrammarExpr, qmark1: Token, qmark2: Token):
        self.value = value
        self.qmark1 = qmark1
        self.qmark2 = qmark2
    def __repr__(self):
        return f'NgOptional({self.value})'
    def to_regex(self, fragments: dict[str, str]) -> str:
        return f'({self.value.to_regex(fragments)})??'
    def identifiers(self) -> set[str]:
        return self.value.identifiers()
    def literals(self) -> set[str]:
        return self.value.literals()

class Plus(GrammarExpr):
    def __init__(self, value: GrammarExpr, plus: Token):
        self.value = value
        self.plus = plus
    def __repr__(self):
        return f'Plus({self.value})'
    def to_regex(self, fragments: dict[str, str]) -> str:
        return f'({self.value.to_regex(fragments)})+'
    def identifiers(self) -> set[str]:
        return self.value.identifiers()
    def literals(self) -> set[str]:
        return self.value.literals()

class NongreedyPlus(GrammarExpr):
    def __init__(self, value: GrammarExpr, plus: Token, qmark: Token):
        self.value = value
        self.plus = plus
        self.qmark = qmark
    def __repr__(self):
        return f'NgPlus({self.value})'
    def to_regex(self, fragments: dict[str, str]) -> str:
        return f'({self.value.to_regex(fragments)})+?'
    def identifiers(self) -> set[str]:
        return self.value.identifiers()
    def literals(self) -> set[str]:
        return self.value.literals()

class Star(GrammarExpr):
    def __init__(self, value: GrammarExpr, star: Token):
        self.value = value
        self.star = star
    def __repr__(self):
        return f'Star({self.value})'
    def to_regex(self, fragments: dict[str, str]) -> str:
        return f'({self.value.to_regex(fragments)})*'
    def identifiers(self) -> set[str]:
        return self.value.identifiers()
    def literals(self) -> set[str]:
        return self.value.literals()

class NongreedyStar(GrammarExpr):
    def __init__(self, value: GrammarExpr, star: Token, qmark: Token):
        self.value = value
        self.star = star
        self.qmark = qmark
    def __repr__(self):
        return f'NgStar({self.value})'
    def to_regex(self, fragments: dict[str, str]) -> str:
        return f'({self.value.to_regex(fragments)})*?'
    def identifiers(self) -> set[str]:
        return self.value.identifiers()
    def literals(self) -> set[str]:
        return self.value.literals()

class RuleDefinition:
    def __init__(
        self,
        name: Identifier,
        alternatives: list[Alternative],
        colon: Token,
    ):
        self.name = name
        self.alternatives = alternatives
        self.colon = colon
    def __repr__(self):
        return f'RuleDef({self.name.name!r}, {self.alternatives})'

class TokenDefinition:
    def __init__(
        self,
        name: Identifier,
        value: GrammarExpr,
        tag: typing.Optional[Tag],
        predicate: Predicate,
        colon: Token,
    ):
        self.name = name
        self.value = value
        self.tag = tag
        self.predicate = predicate
        self.colon = colon
    def __repr__(self):
        return (
            f'TokenDef({self.name.name!r}, {self.value}'
            f', {self.tag}, {self.predicate})'
        )

class FragmentDefinition:
    def __init__(self, name: Identifier, value: GrammarExpr, colon: Token):
        self.name = name
        self.value = value
        self.colon = colon
    def __repr__(self):
        return f'FragDef({self.name.name!r}, {self.value})'

class Grammar:
    def __init__(
        self,
        token_declarations: list[Identifier],
        fragment_definitions: list[FragmentDefinition],
        token_definitions: list[TokenDefinition],
        rule_definitions: list[RuleDefinition],
        code: str,
    ):
        self.token_declarations = token_declarations
        self.fragment_definitions = fragment_definitions
        self.token_definitions = token_definitions
        self.rule_definitions = rule_definitions
        self.code = code
    def __repr__(self):
        return (
            f'Grammar({self.token_declarations}, '
            f'{self.fragment_definitions}, '
            f'{self.token_definitions}, '
            f'{self.rule_definitions})'
        )


class Parser:
    def __init__(self, code: str):
        self.code = code
        self.tokenizer = Tokenizer(code)
        self.tokens = self.tokenizer.tokens()
        self.buffer = next(self.tokens)
        self.grammar = Grammar([], [], [], [], code)
    def next_token(self) -> typing.Optional[Token]:
        token = self.buffer
        try:
            self.buffer = next(self.tokens)
        except StopIteration:
            self.buffer = None
        return token
    def peek_token(self) -> typing.Optional[Token]:
        return self.buffer
    def parse(self) -> Grammar:
        while True:
            if self.peek_token().kind == TokenKind.NEWRULE:
                self.next_token()
                if not self.peek_token().kind == TokenKind.ID:
                    self.parse_error('unexpected token', self.peek_token())
                name = Identifier(self.next_token())
                if self.peek_token().kind == TokenKind.COLON:
                    if name.is_rule():
                        self.parse_rule_def(name)
                    elif name.is_token():
                        self.parse_token_def(name)
                    else:
                        self.parse_fragment_def(name)
                elif self.peek_token().kind in [TokenKind.NEWRULE, TokenKind.EOF]:
                    self.add_token_declaration(name)
                else:
                    self.parse_error('unexpected token', self.peek_token())
            elif self.peek_token().kind == TokenKind.EOF:
                self.next_token()
                break
            else:
                self.parse_error('unexpected token', self.peek_token())
        return self.grammar
    def parse_rule_def(self, name: Identifier) -> None:
        colon = self.next_token()
        if colon.kind != TokenKind.COLON:
            self.parse_error('unexpected token', colon)
        tokens = self.collect_expr_tokens()
        if len(tokens) == 0:
            self.parse_error('rule definitions cannot be empty', colon)
        self.check_for_illegal_rule_tokens(tokens)
        tokens = self.handle_single_tokens(tokens)
        tokens = self.handle_ats_bams_and_predicates(tokens)
        self.check_for_illegal_rule_refs(tokens)
        tokens = self.handle_aliases(tokens)
        tokens = self.handle_parentheses(tokens)
        tokens = self.handle_ops(tokens)
        alternatives = self.make_alternatives(tokens)
        rule_def = RuleDefinition(
            name,
            alternatives,
            colon,
        )
        self.grammar.rule_definitions.append(rule_def)
    def parse_token_def(self, name: Identifier) -> None:
        colon = self.next_token()
        if colon.kind != TokenKind.COLON:
            self.parse_error('unexpected token', colon)
        tokens = self.collect_expr_tokens()
        self.check_for_illegal_token_tokens(tokens)
        tokens = self.handle_single_tokens(tokens)
        tokens, tag, predicate = self.extract_things(tokens)
        self.check_for_illegal_token_refs(tokens)
        tokens = self.handle_ranges(tokens)
        value = self.recursively_parse(tokens)
        token_def = TokenDefinition(
            name,
            value,
            tag,
            predicate,
            colon,
        )
        self.grammar.token_definitions.append(token_def)
    def parse_fragment_def(self, name: Identifier) -> None:
        colon = self.next_token()
        if colon.kind != TokenKind.COLON:
            self.parse_error('unexpected token', colon)
        tokens = self.collect_expr_tokens()
        self.check_for_illegal_fragment_tokens(tokens)
        tokens = self.handle_single_tokens(tokens)
        tokens = self.handle_ranges(tokens)
        value = self.recursively_parse(tokens)
        frag_def = FragmentDefinition(
            name,
            value,
            colon,
        )
        self.grammar.fragment_definitions.append(frag_def)
    def add_token_declaration(self, name: Identifier) -> None:
        self.grammar.token_declarations.append(name)
    def collect_expr_tokens(self) -> list[Token]:
        stop_tokens = [TokenKind.NEWRULE, TokenKind.EOF]
        toks = []
        while self.peek_token().kind not in stop_tokens:
            if self.peek_token().kind == TokenKind.COLON:
                self.parse_error(
                    'unexpected colon',
                    self.peek_token(),
                )
            toks.append(self.next_token())
        return toks
    def check_for_illegal_rule_tokens(
        self,
        tokens: list[Token]
    ) -> None:
        for token in tokens:
            if token.kind == TokenKind.DASH:
                self.parse_error(
                    'rule definitions cannot contain ranges',
                    token,
                )
            elif token.kind == TokenKind.DOT:
                self.parse_error(
                    'rule definitions cannot contain wildcards',
                    token,
                )
    def handle_single_tokens(
        self,
        tokens: list[Token],
    ) -> list[Token | GrammarExpr]:
        out = []
        for token in tokens:
            if token.kind == TokenKind.ID:
                out.append(Identifier(token))
            elif token.kind == TokenKind.STRING:
                out.append(StringLiteral(token))
            elif token.kind == TokenKind.CODE:
                out.append(InlineCode(token))
            else:
                out.append(token)
        return out
    def handle_ats_bams_and_predicates(
        self,
        tokens: list[Token | GrammarExpr],
    ) -> list[Token | GrammarExpr]:
        out = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if isinstance(token, Token):
                if token.kind == TokenKind.AT:
                    if (i + 1 == len(tokens)
                        or not isinstance(tokens[i + 1], Identifier)):
                        self.parse_error(
                            '@ must be followed by an identifier',
                            token,
                        )
                    out.append(Tag(tokens[i + 1], token))
                    i += 1
                elif token.kind == TokenKind.BAM:
                    if (
                        i + 1 == len(tokens)
                        or not isinstance(tokens[i + 1], Identifier)
                    ):
                        self.parse_error(
                            '! must be followed by an identifier',
                            token,
                        )
                    out.append(Directive(tokens[i + 1], token))
                    i += 1
                elif token.kind == TokenKind.QMARK:
                    if (
                        i > 0
                        and isinstance(tokens[i - 1], InlineCode)
                    ):
                        out.append(Predicate(out.pop(), token))
                    else:
                        out.append(token)
                else:
                    out.append(token)
            else:
                out.append(token)
            i += 1
        return out
    def handle_aliases(
        self,
        tokens: list[Token | GrammarExpr],
    ) -> list[Token | GrammarExpr]:
        is_kind = lambda t, k: isinstance(t, Token) and t.kind == k
        out = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if is_kind(token, TokenKind.EQUALS):
                if (
                    len(out) == 0
                    or not isinstance(out[-1], Identifier)
                    or i + 1 == len(tokens)
                    or not isinstance(tokens[i + 1], Identifier)
                ):
                    self.parse_error(
                        '= must have an identifier on each side',
                        token,
                    )
                alias = Alias(out.pop(), tokens[i + 1], token)
                out.append(alias)
                i += 1
            else:
                out.append(token)
            i += 1
        return out
    def handle_parentheses(
        self,
        tokens: list[Token | GrammarExpr],
    ) -> list[Token | GrammarExpr]:
        is_kind = lambda t, k: isinstance(t, Token) and t.kind == k
        out = []
        depth = 0
        in_parens = left_paren = None
        for token in tokens:
            if is_kind(token, TokenKind.LPAREN):
                if depth > 0:
                    in_parens.append(token)
                    depth += 1
                else:
                    in_parens = []
                    left_paren = token
                    depth += 1
            elif is_kind(token, TokenKind.RPAREN):
                if depth == 0:
                    self.parse_error(
                        'unmatched right parentheses',
                        token,
                    )
                elif depth == 1:
                    depth = 0
                    if len(in_parens) == 0:
                        self.parse_error(
                            'parentheses must contain an expression',
                            token,
                        )
                    out.append(self.recursively_parse(in_parens))
                else:
                    depth -= 1
                    in_parens.append(token)
            elif depth > 0:
                in_parens.append(token)
            else:
                out.append(token)
        if depth > 0:
            self.parse_error(
                'unclosed parentheses',
                left_paren,
            )
        return out
    def handle_ops(
        self,
        tokens: list[Token | GrammarExpr],
    ) -> list[Token | GrammarExpr]:
        is_kind = lambda t, k: isinstance(t, Token) and t.kind == k
        out = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if is_kind(token, TokenKind.STAR):
                if (
                    len(out) == 0
                    or not isinstance(out[-1], GrammarExpr)
                ):
                    self.parse_error(
                        '* must follow an expression',
                        token,
                    )
                if (
                    i + 1 < len(tokens)
                    and is_kind(tokens[i + 1], TokenKind.QMARK)
                ):
                    star = NongreedyStar(out.pop(), token, tokens[i + 1])
                    out.append(star)
                    i += 1
                else:
                    star = Star(out.pop(), token)
                    out.append(star)
            elif is_kind(token, TokenKind.PLUS):
                if (
                    len(out) == 0
                    or not isinstance(out[-1], GrammarExpr)
                ):
                    self.parse_error(
                        '+ must follow an expression',
                        token,
                    )
                if (
                    i + 1 < len(tokens)
                    and is_kind(tokens[i + 1], TokenKind.QMARK)
                ):
                    plus = NongreedyPlus(out.pop(), token, tokens[i + 1])
                    out.append(plus)
                    i += 1
                else:
                    plus = Plus(out.pop(), token)
                    out.append(plus)
            elif is_kind(token, TokenKind.QMARK):
                if (
                    len(out) == 0
                    or not isinstance(out[-1], GrammarExpr)
                ):
                    self.parse_error(
                        '? must follow an expression',
                        token,
                    )
                if (
                    i + 1 < len(tokens)
                    and is_kind(tokens[i + 1], TokenKind.QMARK)
                ):
                    opt = NongreedyOptional(out.pop(), token, tokens[i + 1])
                    out.append(opt)
                    i += 1
                else:
                    opt = Optional(out.pop(), token)
                    out.append(opt)
            else:
                out.append(token)
            i += 1
        return out
    def make_alternatives(
        self,
        tokens: list[Token | GrammarExpr],
    ) -> list[Alternative]:
        is_kind = lambda t, k: isinstance(t, Token) and t.kind == k
        groups = [[]]
        ors = []
        for token in tokens:
            if is_kind(token, TokenKind.OR):
                if len(groups[-1]) == 0:
                    self.parse_error('alternatives cannot be empty', token)
                groups.append([])
                ors.append(token)
            else:
                groups[-1].append(token)
        if len(groups[-1]) == 0:
            self.parse_error('alternatives cannot be empty', ors[-1])
        alternatives = []
        for group in groups:
            value, tag, directives, code, predicate = self.split_group(group)
            alt = Alternative(value, tag, directives, code, predicate)
            alternatives.append(alt)
        if alternatives[0].tag is None:
            for alt in alternatives[1:]:
                if alt.tag is not None:
                    self.parse_error(
                        'all or none of the alternatives should have tags',
                        alt.tag.at,
                    )
        else:
            for alt in alternatives[1:]:
                if alt.tag is None:
                    self.parse_error(
                        'all or none of the alternatives should have tags',
                        alternatives[0].tag.at,
                    )
        return alternatives
    def split_group(
        self,
        group: list[GrammarExpr],
    ) -> tuple[
        GrammarExpr,
        typing.Optional[Tag],
        list[Directive],
        typing.Optional[InlineCode],
        typing.Optional[Predicate],
    ]:
        is_kind = lambda t, k: isinstance(t, Token) and t.kind == k
        tag = None
        directives = []
        code = None
        predicate = None
        while group:
            if isinstance(group[-1], Tag):
                if tag is None:
                    tag = group.pop()
                else:
                    self.parse_error(
                        'alternatives cannot have multiple tags',
                        tag.at,
                    )
            elif isinstance(group[-1], Directive):
                directives.append(group.pop())
            elif isinstance(group[-1], InlineCode):
                if code is None:
                    code = group.pop()
                else:
                    self.parse_error(
                        'alternatives can only have one code snippet',
                        code.token,
                    )
            else:
                break
        if (
            len(group) > 0
            and isinstance(group[0], Predicate)
        ):
            predicate = group.pop(0)
        if len(group) == 0:
            if tag is not None:
                self.parse_error(
                    'alternatives cannot be empty',
                    tag.at,
                )
            elif code is not None:
                self.parse_error(
                    'alternatives cannot be empty',
                    code.token,
                )
            elif predicate is not None:
                self.parse_error(
                    'alternatives cannot be empty',
                    predicate.code.token,
                )
            else:
                self.parse_error(
                    'alternatives cannot be empty',
                    directives[0].bam,
                )
        for elem in group:
            if isinstance(elem, Tag):
                self.parse_error(
                    'tags must be at the end of an alternative',
                    elem.at,
                )
            elif isinstance(elem, Directive):
                self.parse_error(
                    'directives must be at the end of an alternative',
                    elem.bam,
                )
            elif isinstance(elem, InlineCode):
                self.parse_error(
                    'code snippets must be at the end of an alternative',
                    elem.token,
                )
            elif isinstance(elem, Predicate):
                self.parse_error(
                    'predicates must be at the start of an alternative',
                    elem.code.token,
                )
        value = group[0] if len(group) == 1 else Concatenation(group)
        return value, tag, directives, code, predicate
    def recursively_parse(
        self,
        tokens: list[Token | GrammarExpr]
    ) -> GrammarExpr:
        is_kind = lambda t, k: isinstance(t, Token) and t.kind == k
        tokens = self.handle_parentheses(tokens)
        tokens = self.handle_ops(tokens)
        groups = [[]]
        ors = []
        for token in tokens:
            if is_kind(token, TokenKind.OR):
                if len(groups[-1]) == 0:
                    self.parse_error('alternatives cannot be empty', token)
                groups.append([])
                ors.append(token)
            else:
                groups[-1].append(token)
        if len(groups[-1]) == 0:
            self.parse_error('alternatives cannot be empty', ors[-1])
        if len(groups) == 1:
            if len(groups[0]) == 1:
                return groups[0][0]
            return Concatenation(groups[0])
        values = []
        for group in groups:
            if len(group) == 1:
                values.append(group[0])
            else:
                values.append(Concatenation(group))
        return Union(values, ors)
    def check_for_illegal_token_tokens(
        self,
        tokens: list[Token]
    ) -> None:
        for token in tokens:
            if token.kind == TokenKind.BAM:
                self.parse_error(
                    'token definitions cannot contain directives',
                    token,
                )
            elif token.kind == TokenKind.EQUALS:
                self.parse_error(
                    'token definitions cannot contain aliases',
                    token,
                )
            elif token.kind == TokenKind.DOT:
                self.parse_error(
                    'token definitions cannot contain wildcards',
                    token,
                )
    def extract_things(
        self,
        tokens: list[Token | GrammarExpr],
    ) -> tuple[
        list[Token | GrammarExpr],
        Tag,
        typing.Optional[Predicate],
    ]:
        is_kind = lambda t, k: isinstance(t, Token) and t.kind == k
        out = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if is_kind(token, TokenKind.AT):
                if (
                    i + 1 < len(tokens)
                    and isinstance(tokens[i + 1], Identifier)
                ):
                    out.append(Tag(tokens[i + 1], token))
                    i += 1
                else:
                    self.parse_error(
                        '@ must be followed by an identifier',
                        token,
                    )
            else:
                out.append(token)
            i += 1
        tag = None
        predicate = None
        if (
            len(out) > 1
            and isinstance(out[0], InlineCode)
            and is_kind(out[1], TokenKind.QMARK)
        ):
            predicate = Predicate(out.pop(0), out.pop(0))
        i = len(out) - 1
        while i >= 0:
            if isinstance(out[i], Tag):
                if tag is not None:
                    self.parse_error(
                        'token definitions cannot have multiple tags',
                        tag.at,
                    )
                tag = out.pop(i)
            elif isinstance(out[i], InlineCode):
                self.parse_error(
                    'token definitions cannot contain code snippets',
                    out[i].token,
                )
            else:
                break
            i -= 1
        if len(out) == 0:
            if tag is not None:
                self.parse_error(
                    'token definitions cannot be empty',
                    tag.at,
                )
            else:
                self.parse_error(
                    'token definitions cannot be empty',
                    predicate.code.token,
                )
        for token in out:
            if isinstance(token, Tag):
                self.parse_error(
                    'tags must be at the end of token definitions',
                    token.at,
                )
            elif isinstance(token, InlineCode):
                self.parse_error(
                    'token definitions cannot contain code snippets',
                    token.token,
                )
        return out, tag, predicate
    def check_for_illegal_fragment_tokens(
        self,
        tokens: list[Token],
    ) -> None:
        for token in tokens:
            if token.kind == TokenKind.CODE:
                self.parse_error(
                    'fragment definitions cannot contain code snippets',
                    token,
                )
            elif token.kind == TokenKind.BAM:
                self.parse_error(
                    'fragment definitions cannot contain directives',
                    token,
                )
            elif token.kind == TokenKind.AT:
                self.parse_error(
                    'fragment definitions cannot contain tags',
                    token,
                )
            elif token.kind == TokenKind.EQUALS:
                self.parse_error(
                    'fragment definitions cannot contain aliases',
                    token,
                )
            elif token.kind == TokenKind.ID:
                if Identifier(token).is_rule():
                    self.parse_error(
                        'fragment definitions cannot contain rule references',
                        token,
                    )
                elif Identifier(token).is_token():
                    self.parse_error(
                        'fragment definitions cannot contain token references',
                        token,
                    )
    def check_for_illegal_rule_refs(
        self,
        tokens: list[Token | GrammarExpr],
    ) -> None:
        for token in tokens:
            if isinstance(token, Identifier):
                if token.is_fragment():
                    self.parse_error(
                        'rule definitions cannot contain fragment references',
                        token.token,
                    )
    def check_for_illegal_token_refs(
        self,
        tokens: list[Token | GrammarExpr],
    ) -> None:
        for token in tokens:
            if isinstance(token, Identifier):
                if token.is_rule():
                    self.parse_error(
                        'token definitions cannot contain rule references',
                        token.token,
                    )
                elif token.is_token():
                    self.parse_error(
                        'token definitions cannot contain token references',
                        token.token,
                    )
    def handle_ranges(
        self,
        tokens: list[Token | GrammarExpr],
    ) -> list[Token | GrammarExpr]:
        is_kind = lambda t, k: isinstance(t, Token) and t.kind == k
        out = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if is_kind(token, TokenKind.DASH):
                if (
                    len(out) == 0
                    or not isinstance(out[-1], StringLiteral)
                    or i + 1 == len(tokens)
                    or not isinstance(tokens[i + 1], StringLiteral)
                ):
                    self.parse_error(
                        '- must have an string on each side',
                        token,
                    )
                rng = Range(out.pop(), tokens[i + 1], token)
                if len(rng.low.value) != 1:
                    self.parse_error(
                        'range bounds must be a single character',
                        rng.low.token,
                    )
                if len(rng.high.value) != 1:
                    self.parse_error(
                        'range bounds must be a single character',
                        rng.high.token,
                    )
                out.append(rng)
                i += 1
            else:
                out.append(token)
            i += 1
        return out
    def parse_error(self, msg: str, token: Token):
        raise GrammarError(
            msg,
            (token,),
        )

