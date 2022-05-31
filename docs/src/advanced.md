# Advanced Features

## Advanced Tokenization

Tags are created by passing the keyword argument `base: type` to the `make_tokenizer` function. The tokenizer class it outputs will subclass this base class. The base class you input must subclass `zparse.BaseTokenizer`. Each tag in your grammar must be defined as a function in your base class. As an example, we can take the `@ignore` tag, which is already defined in `zparse.BaseTokenizer`. It's definition is simple:

```python
def ignore(self, token: Token):
    return
```

When a token is matched in the input stream, instead of being emitted directly, it is passed through the corresponding method. In most languages, whitespace is ignored. So if we match a whitespace token, we want to throw it out. The `@ignore` tac accomplishes this because the `ignore` method takes in the token and does not emit anything.

More sophisticated tag methods are not hard to imagine. For example, tokenization of Python code requires special examination of whitespace characters because indentation matters. In this case, the `@handle_whitespace` tag must analyze each whitespace token and emit `INDENT` and `DEDENT` tokens as needed using `yield` statements.