# Parsing

## `make_parser(grammar: str) -> type`

The `make_parser` function creates a parser class from a grammar. For example:

```
ParserClass = zparse.make_parser(grammar)
```

Internally, this calls the `make_tokenizer` method. Once the parser's class is created, we instantiate that class with the code we want to parse:

```
parser = ParserClass(code)
```

### `ParserClass.parse(self) -> Node`

The `parse` method is called on the parser object to find the parse tree:

```
parse_tree = parser.parse()
```

## `Node`

The `Node` class describes the parse tree. Each node contains a `str` with the name of the rule it was created from. It also contains a list of all of its children.

### `Node.kind: str`

The name of the rule this node was expanded from.

### `Node.children: list[Node | Token]`

A list containing all of this node's terminal and nonterminal children in order.