# Grammars

zparse accepts [PEG](https://en.wikipedia.org/wiki/Parsing_expression_grammar) grammars. zparse grammars contain four elements: rule definitions, token definitions, token declarations, and fragment definitions.

## Fragment Definitions

Fragment definitions look like this:

```
_INT: ('0'-'9')+
```

The left hand side of the definitions contains the fragment's name. Fragment names are written in all caps and begin with an underscore. The right hand side contains a regular expression. Regular expression can contain 8 elements:
1. string literals (`'abc'`, `'if'`)
2. ranges (`'a'-'z'`, `'0'-'9'`)
3. zero or more (`'a'*`, `('a'-'z')*`)
4. one or more (`'a'+`, `('a'-'z')+`)
5. optional (`'a'?`, `('a'-'z')?`)
6. concatenation (`'a' 'b'`, `'a'* 'b'+`)
7. option (`'a' | 'b'`)
8. reference to another fragment (`_FRAG+`)

## Token Declarations

Token declarations are just a token name followed by a newline. Token names are written in all caps, but do not start with an underscore. Token declarations are useful when you want to use custom code to emit tokens. For example, the Python grammar contains `INDENT` and `DEDENT` tokens, but those don't correspond to regular expressions:

```
IDENT
DEDENT
```

## Token Definitions

Token definitions look like this:

```
WHITE_SPACE: {self.ws}? (' ' | '\t' | '\n')+ @ignore
```

Token declarations can contain all the elements from fragments. They can also contain tags (like `@ignore`) and predicates (like `{self.ws}`) which are explained on the [advanced features](./advanced.md) page. Unlike fragment definitions, token definitions cannot reference other token definitions.

## Rule Definitions

Fragment definitions, token declarations, and token definitions all describe tokenization. Rule definitions describe parsing.

```
expr
  : INT
  | '(' expr ')'
  | expr '**' expr !right_assoc
  | '-' expr
  | expr ('*' | '/') expr
  | expr ('+' | '-') expr
```

Rule must contain at least one lowercase letter and cannot start with an underscore. Rule definitions can contains references to other rules, themselves, and tokens, but cannot reference fragments directly. Rules can contain directives (`!right_assoc`), but only at the top level (so `rule: a (b | c !right_assoc) | d` would not be allowed). Any definitions can extend past a single line, but subsequent lines must be indented.