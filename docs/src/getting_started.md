# Getting Started

## Installation

The easiest way to install zparse with from [PyPi](https://https://pypi.org/):

```
pip install zparse
```

## Basic Usage

Using zparse starts with writing a grammar. Grammars are described in a python-like version of [EBNF](https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form). Details on writing grammars can be found on the [Grammars](./grammars.md) page. You can use raw multiline strings or store your grammars in files:

```
grammar = r'''
_INT: ('0'-'9')+
start: '[' _INT (',' _INT)* ']'
'''
```

```
grammar = open('grammar.peg').read()
```

Once you have your grammar, pass it to the `make_parser` method:

```
ParserClass = zparse.make_parser(grammar)
```

`make_parser` returns a type which must then be instantiated with the code you want to parse. Call the `parse` method on the parser object to get the parse tree:

```
parser = ParserClass(code)
parse_tree = parser.parse()
```