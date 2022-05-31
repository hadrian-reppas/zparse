import networkx as nx
import typing
import enum
import types
import re

from zparse.errors import GrammarError, TokenError
from zparse.metalang import Parser, Grammar

# TODO: check of tokens match the empty string,
#       check if patterns get matched by earlier tokens (eg '>' then '>>')

# TODO: figure out implicit token fuckery. (eg '>' and '>>', is think the only way
#       to resolve this is to do some tokenizing at parse time). I currently
#       limit implicit tokens to single characters...

reserved_token_names = ['EOF']
reserved_tag_names = ['__init__', 'handle_tag_function', 'TokenKind', 'tokens']

class Token(typing.NamedTuple):
    text: str
    kind: enum.Enum
    line: int
    column: int
    code: str
    def __repr__(self):
        if self.kind.name.startswith('_'):
            return f'Token({self.text!r})'
        return f'Token({self.text!r}, {self.kind.name})'

class BaseTokenizer:
    def __init__(self, code: str):
        self.code = code
    def ignore(self, token: Token):
        pass
    @staticmethod
    def handle_tag_function(ret_val):
        if ret_val is None:
            pass
        elif isinstance(ret_val, types.GeneratorType):
            for token in ret_val:
                if not isinstance(token, Token):
                    raise TypeError(
                        f'tag function emitted value of type {type(token)}'
                    )
                yield token
        else:
            if not isinstance(ret_val, Token):
                raise TypeError(
                    f'tag function emitted value of type {type(ret_val)}'
                )
            yield ret_val

def make_tokenizer(
    code: str,
    base: type=BaseTokenizer,
    name: str='AnonymousTokenizer',
    allow_big_implicits: bool=False,
) -> type:
    if not issubclass(base, BaseTokenizer):
        raise ValueError('base must subclass tokenizers.BaseTokenizer')
    grammar = Parser(code).parse()
    check_for_illegal_token_names(grammar)
    check_for_illegal_tag_names(grammar, base)
    return make_class(name, base, grammar, allow_big_implicits)

def make_class(
    name: str,
    base: type,
    grammar: Grammar,
    allow_big_implicits: bool,
) -> type:
    tokens_func = make_tokens_func(grammar, allow_big_implicits)
    TokenKind = make_TokenKind(grammar, allow_big_implicits)
    return type(
        name,
        (base,),
        {
            'TokenKind': TokenKind,
            'tokens': tokens_func,
        },
    )

func_type = typing.Callable[[], typing.Generator[Token, None, None]]

def make_tokens_func(grammar: Grammar, allow_big_implicits: bool) -> func_type:
    token_info = make_regex(grammar, allow_big_implicits)
    def tokens(self):
        rest = self.code
        line = 1
        column = 0
        while rest:
            best_len = 0
            best_kind = None
            best_tag = None
            for name, regex, tag, predicate in token_info:
                if predicate is not None and not eval(predicate):
                    continue
                m = regex.search(rest)
                if m is not None and m.span()[0] == 0:
                    cur_len = m.span()[1]
                    if cur_len > best_len:
                        best_len = cur_len
                        best_kind = eval(f'self.TokenKind.{name}')
                        best_tag = tag
            if best_len == 0:
                raise TokenError(
                    f'unknown char {rest[0]!r} on line'
                    f'{line} and column {column}'
                )
            text = rest[:best_len]
            tok = Token(text, best_kind, line, column, self.code)
            rest = rest[best_len:]
            line += text.count('\n')
            if '\n' in text:
                column = len(text) - text.rfind('\n')
            else:
                column += len(text)
            if best_tag is None:
                yield tok
            else:
                yield from self.handle_tag_function(
                    eval(f'self.{best_tag}(tok)')
                )
        yield Token('', eval('self.TokenKind.EOF'), line, column, self.code)
    return tokens

def make_regex(
    grammar: Grammar,
    allow_big_implicits: bool,
) -> list[tuple[str, re.Pattern, str, str]]:
    frag_order = get_frag_order(grammar)
    frag_defs = {frag.name.name: frag.value for frag in grammar.fragment_definitions}
    fragments = {}
    for frag_name in frag_order:
        fragments[frag_name] = frag_defs[frag_name].to_regex(fragments)
    tokens = []
    escape = {'.', '^', '$', '*', '+', '?', '{', '}', '(', ')', '\\', '[', ']', '|'}
    for name, value in get_implicit_tokens(grammar, allow_big_implicits).items():
        tokens.append((
            name,
            re.compile(''.join('\\' + c if c in escape else c for c in value)),
            None,
            None,
        ))
    for tok_def in grammar.token_definitions:
        tokens.append((
            tok_def.name.name,
            re.compile(tok_def.value.to_regex(fragments)),
            (
                None if tok_def.tag is None
                else tok_def.tag.name.name
            ),
            (
                None if tok_def.predicate is None
                else tok_def.predicate.code.token.text[1:-1]
            ),
        ))
    return tokens

def get_frag_order(grammar: Grammar) -> list[str]:
    frag_graph = nx.DiGraph()
    for frag_def in grammar.fragment_definitions:
        name = frag_def.name.name
        frag_graph.add_node(name)
        refs = frag_def.value.identifiers()
        for ref in refs:
            frag_graph.add_edge(ref, name)
    try:
        return list(nx.algorithms.topological_sort(frag_graph))
    except nx.NetworkXUnfeasible:
        cycle = nx.algorithms.find_cycle(frag_graph)
        frags = [edge[0] for edge in cycle]
        msg = ''
        if len(frags) == 1:
            msg = f'{frags[0]!r} cannot be defined recursively'
        elif len(frags) == 2:
            msg = f'{frags[0]!r} and {frags[1]!r} cannot be defined recursively'
        else:
            before = ', '.join(repr(frag) for frag in frags[:-1])
            msg = before + f', and {frags[-1]!r} cannot be defined recursively'
        raise GrammarError(msg)

def check_for_illegal_token_names(grammar: Grammar) -> None:
    for tok_dec in grammar.token_declarations:
        if tok_dec.name in reserved_token_names:
            raise GrammarError(
                f'{tok_dec.name!r} is a reserved token name',
                (tok_dec,),
            )
    for tok_def in grammar.token_definitions:
        if tok_def.name.name in reserved_token_names:
            raise GrammarError(
                f'{tok_def.name.name!r} is a reserved token name',
                (tok_dec,),
            )

def check_for_illegal_tag_names(grammar: Grammar, base: type) -> None:
    for tok_def in grammar.token_definitions:
        if tok_def.tag is None:
            continue
        if tok_def.tag.name in reserved_tag_names:
            raise GrammarError(
                f'{tok_def.tag.name!r} is an illegal tag name',
                (tok_def.tag.name,),
            )

def make_TokenKind(grammar: Grammar, allow_big_implicits: bool) -> type:
    tok_names = []
    tok_names.extend(tok.name for tok in grammar.token_declarations)
    tok_names.extend(tok.name.name for tok in grammar.token_definitions)
    tok_names.extend(reserved_token_names)
    tok_names.extend(get_implicit_tokens(grammar, allow_big_implicits))
    return make_enum('TokenKind', tok_names)

def get_implicit_tokens(
    grammar: Grammar, 
    allow_big_implicits: bool,
) -> dict[str, str]:
    values = set()
    for rule_def in grammar.rule_definitions:
        for alt in rule_def.alternatives:
            for lit in alt.value.literals():
                if not allow_big_implicits and len(lit) > 1:
                    # TODO: remove this restriction
                    raise GrammarError(
                        f'implicit token {lit!r} cannot be multiple characters',
                        rule_def.name.token,
                    )
                values.add(lit)
    return {get_name(v): v for v in values}

def get_name(v: str) -> str:
    return '_' + '_'.join(hex(ord(c))[2:] for c in v)

def make_enum(name: str, members: list[str]) -> type:
	code = (
        f'class {name}(enum.Enum):\n'
        + '\n'.join(f'    {m} = enum.auto()' for m in members)
    )
	exec(code)
	return eval(name)