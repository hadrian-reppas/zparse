grammar = r'''

json: value

value
  : STRING
  | NUMBER
  | object
  | array
  | 'true'
  | 'false'
  | 'null'

object: '{' pairs? '}'
pairs: pair (',' pair)*
pair: STRING ':' value

array: '[' values? ']'
values: value (',' value)*

STRING: '"' (_ESCAPE | _SAFECODEPOINT)* '"'
_SAFECODEPOINT: ' '-'!' | '#'-'[' | ']'-'\U0010FFFF'
_ESCAPE: '\\' (_ESC_CHAR | _UNICODE)
_ESC_CHAR: '\\' | '"' | 'b' | 'f' | 'n' | 'r' | 't'
_UNICODE: 'u' _HEX _HEX _HEX _HEX
_HEX: '0'-'9' | 'a'-'f' | 'A'-'F'

NUMBER: '-'? _INT ('.' '0'-'9'+)? _EXP?
_INT: '0' | '1'-'9' ('0'-'9')*
_EXP: ('E' | 'e') ('+' | '-')? _INT

WS: (' ' | '\t' | '\n' | '\r')+ @ignore

'''
