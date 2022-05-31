# Errors

zparse defines three errors.

## `GrammarError`

A `GrammarError` is thrown when a grammar is malformed. This includes syntax errors and logical errors (like recursion in fragment definitions and rules that reference fragments).

### `GrammarError.msg: str`

This field contains a description of the error.

### `GrammarError.tokens: list[Token]`

This field contains a list of the offending tokens. It may be empty if there is a syntax error and tokenization fails.

## `TokenError`

A `TokenError` is thrown during parsing when none of the token definitions match the input.

### `TokenError.msg: str`

This field contains a description of the error.

## `ParseError`

A `ParseError` is thrown during parsing when none of the token definitions match the input.

### `ParseError.msg: str`

This field contains a description of the error.

### `ParseError.tokens: list[Token]`

This field contains the offending tokens. It usually contains a single token.