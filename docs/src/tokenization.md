# Tokenization

## `make_tokenizer(grammar: str) -> type`

The `make_tokenizer` function creates a tokenizer class from a grammar. For example:

```
TokenizerClass = zparse.make_tokenizer(grammar)
```

Once the tokenizer's class is created, we instantiate that class with the code we want to tokenize:

```
tokenizer = TokenizerClass(code)
```

### `TokenizerClass.tokens(self) -> Generator[Token]`

The `tokens` method is called on the tokenizer object to find the tokens. The 

```
tokens = parser.parse()
```

## `Token`

The `Token` class represents a token in the token stream.

### `Token.kind: str`

The token name (like `'INT'` and `'WS'`).

### `Token.text: str`

The text captured by the regular expression (like `'34'` and `' \t'`).

### `Token.line: int`

The Token's line number. If the token spans over multiple lines, this field contains the starting line.

### `Token.column: int`

The Token's column number.

### `Token.code: str`

A reference to all the code that is being tokenized.