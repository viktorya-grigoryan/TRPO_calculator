import math
import re
from dataclasses import dataclass
from enum import Enum, auto
import sys
import argparse

sys.setrecursionlimit(10000)

class TokenType(Enum):
    NUMBER = auto()
    OPERATOR = auto()


@dataclass
class Token:
    type: TokenType
    value: str | float

class ASTNode:
    pass

@dataclass
class Number(ASTNode):
    value: float

@dataclass
class BinOp(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode

@dataclass
class UnaryOp(ASTNode):
    op: str
    operand: ASTNode


class CalculatorError(Exception):
    pass

class ParserError(CalculatorError):
    pass

class EvaluationError(CalculatorError):
    pass

class Parser:
    def __init__(self):
        self._tokens = []
        self._pos = 0
        self._current_token = None
  

    def tokenize(self, expression: str) -> list[Token]:
        token_spec = [
            ('NUMBER', r'\d+(\.\d*)?([eE][+-]?\d+)?'),
            ('OPERATOR', r'[+\-*/]'),
    
            ('SKIP', r'[ \t\n]'),
            ('MISMATCH', r'.'),
        ]
        tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_spec)
        tokens = []
        
        for mo in re.finditer(tok_regex, expression):
            kind = mo.lastgroup
            value = mo.group()
            
            if kind == 'NUMBER':
                tokens.append(Token(TokenType.NUMBER, float(value)))
            elif kind == 'OPERATOR':
                tokens.append(Token(TokenType.OPERATOR, value))
            elif kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise ParserError(f"Invalid character: {value}")
        
        return tokens

    def parse(self, expression: str) -> ASTNode:
        self._tokens = self.tokenize(expression)
        self._pos = 0
        self._current_token = self._tokens[0] if self._tokens else None
        return self._parse_expression()

    def _advance(self):
        self._pos += 1
        self._current_token = self._tokens[self._pos] if self._pos < len(self._tokens) else None

    def _parse_expression(self) -> ASTNode:
        node = self._parse_term()
        while self._current_token and self._current_token.type == TokenType.OPERATOR and self._current_token.value in '+-':
            op = self._current_token.value
            self._advance()
            node = BinOp(node, op, self._parse_term())
        return node

    def _parse_term(self) -> ASTNode:
        node = self._parse_power()
        while self._current_token and self._current_token.type == TokenType.OPERATOR and self._current_token.value in '*/':
            op = self._current_token.value
            self._advance()
            node = BinOp(node, op, self._parse_power())
        return node


    def _parse_power(self) -> ASTNode:
        if self._current_token and self._current_token.type == TokenType.OPERATOR and self._current_token.value == '-':
            self._advance()
            return UnaryOp('-', self._parse_power())
        return self._parse_atom()

    def _parse_atom(self) -> ASTNode:
        token = self._current_token
        if not token:
            raise ParserError("Unexpected end of expression")
            
        if token.type == TokenType.NUMBER:
            self._advance()
            return Number(token.value)

            
        raise ParserError(f"Expected number, function or parenthesis, got {token.value}")

    def _expect(self, token_type: TokenType, error_msg: str):
        if not self._current_token or self._current_token.type != token_type:
            raise ParserError(error_msg)
        self._advance()

class Evaluator:
    
    def evaluate(self, node: ASTNode) -> float:
        if isinstance(node, Number):
            return node.value
            
        elif isinstance(node, BinOp):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            
            if node.op == '+': return left + right
            elif node.op == '-': return left - right
            elif node.op == '*': return left * right
            elif node.op == '/':
                if right == 0:
                    raise EvaluationError("Division by zero")
                return left / right
            
                    
        elif isinstance(node, UnaryOp):
            operand = self.evaluate(node.operand)
            return -operand if node.op == '-' else operand
            
        
        raise EvaluationError(f"Unknown node type: {type(node)}")

class Calculator:
    def __init__(self):
        self.parser = Parser()
        self.evaluator = Evaluator()
    
    def calculate(self, expression: str) -> float:
        try:
            ast = self.parser.parse(expression)
            return self.evaluator.evaluate(ast)
        except CalculatorError as e:
            raise
        except Exception as e:
            raise CalculatorError(f"Unexpected error: {str(e)}") from e

def interactive_mode():

    print("Для выхода введите 'exit' или 'quit'")
    
    calc = Calculator()
    
    while True:
        try:
            expression = input("> ").strip()
            if expression.lower() in ('exit', 'quit'):
                break
            if not expression:
                continue
            
            result = calc.calculate(expression)
            print(result)
        except CalculatorError as e:
            print(f"Ошибка: {e}")
        except KeyboardInterrupt:
            print("\nВыход из калькулятора")
            break
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Калькулятор математических выражений')
    parser.add_argument('expression', nargs='?', help='Выражение для вычисления')
    parser.add_argument('-i', '--interactive', action='store_true', help='Интерактивный режим')
   
    
    args = parser.parse_args()
    

    calc = Calculator()
    
    if args.interactive:
        interactive_mode()
    elif args.expression:
        try:
            result = calc.calculate(args.expression)
            print(result)
        except CalculatorError as e:
            print(f"Ошибка: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
