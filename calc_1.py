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
    FUNCTION = auto()
    CONSTANT = auto()
    LPAREN = auto()
    RPAREN = auto()

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

@dataclass
class FunctionCall(ASTNode):
    func: str
    arg: ASTNode

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
        self._functions = {'sin', 'cos', 'tg', 'ctg', 'ln', 'exp', 'sqrt', 'arctan'}
        self._constants = {'pi': math.pi, 'e': math.e}

    def tokenize(self, expression: str) -> list[Token]:
        token_spec = [
            ('NUMBER', r'\d+(\.\d*)?([eE][+-]?\d+)?'),
            ('OPERATOR', r'[+\-*/%^]'),
            ('FUNCTION', r'sin|cos|tg|ctg|ln|exp|sqrt|arctan'),
            ('CONSTANT', r'pi|e'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
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
            elif kind == 'FUNCTION':
                tokens.append(Token(TokenType.FUNCTION, value))
            elif kind == 'CONSTANT':
                tokens.append(Token(TokenType.CONSTANT, value))
            elif kind == 'LPAREN':
                tokens.append(Token(TokenType.LPAREN, value))
            elif kind == 'RPAREN':
                tokens.append(Token(TokenType.RPAREN, value))
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
        node = self._parse_factor()
        while self._current_token and self._current_token.type == TokenType.OPERATOR and self._current_token.value in '*/%':
            op = self._current_token.value
            self._advance()
            node = BinOp(node, op, self._parse_factor())
        return node

    def _parse_factor(self) -> ASTNode:
        node = self._parse_power()
        while self._current_token and self._current_token.type == TokenType.OPERATOR and self._current_token.value == '^':
            op = self._current_token.value
            self._advance()
            node = BinOp(node, op, self._parse_factor())
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
            
        elif token.type == TokenType.CONSTANT:
            self._advance()
            return Number(self._constants[token.value])
            
        elif token.type == TokenType.FUNCTION:
            func = token.value
            self._advance()
            self._expect(TokenType.LPAREN, "Expected '(' after function name")
            arg = self._parse_expression()
            self._expect(TokenType.RPAREN, "Expected ')' after function argument")
            return FunctionCall(func, arg)
            
        elif token.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN, "Expected ')' after expression")
            return expr
            
        raise ParserError(f"Expected number, function or parenthesis, got {token.value}")

    def _expect(self, token_type: TokenType, error_msg: str):
        if not self._current_token or self._current_token.type != token_type:
            raise ParserError(error_msg)
        self._advance()

class Evaluator:
    def __init__(self, angle_unit='radian'):
        self.angle_unit = angle_unit.lower()
        if self.angle_unit not in ['radian', 'degree']:
            raise ValueError("angle_unit must be either 'radian' or 'degree'")

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
            elif node.op == '^':
                try:
                    result = left ** right
                    if abs(result) == float('inf'):
                        raise EvaluationError("Numerical overflow")
                    return result
                except OverflowError:
                    raise EvaluationError("Numerical overflow")
                    
        elif isinstance(node, UnaryOp):
            operand = self.evaluate(node.operand)
            return -operand if node.op == '-' else operand
            
        elif isinstance(node, FunctionCall):
            arg = self.evaluate(node.arg)
            
            if node.func == 'sin':
                x = math.radians(arg) if self.angle_unit == 'degree' else arg
                return math.sin(x)
            elif node.func == 'cos':
                x = math.radians(arg) if self.angle_unit == 'degree' else arg
                return math.cos(x)
            elif node.func == 'tg':
                x = math.radians(arg) if self.angle_unit == 'degree' else arg
                return math.tan(x)
            elif node.func == 'ctg':
                x = math.radians(arg) if self.angle_unit == 'degree' else arg
                tan = math.tan(x)
                if tan == 0:
                    raise EvaluationError("Cotangent is undefined")
                return 1 / tan
            elif node.func =='arctan':
                arctan = math.atan(arg)
                res = arctan*180/math.pi if self.angle_unit == 'degree' else arctan
                return res

            elif node.func == 'ln':
                if arg <= 0:
                    raise EvaluationError("Logarithm is only defined for positive numbers")
                return math.log(arg)
            elif node.func == 'exp':
                try:
                    result = math.exp(arg)
                    if result == float('inf'):
                        raise EvaluationError("Numerical overflow")
                    return result
                except OverflowError:
                    raise EvaluationError("Numerical overflow")
            elif node.func == 'sqrt':
                if arg < 0:
                    raise EvaluationError("Square root is only defined for non-negative numbers")
                return math.sqrt(arg)
                
        raise EvaluationError(f"Unknown node type: {type(node)}")

class Calculator:
    def __init__(self, angle_unit='radian'):
        self.parser = Parser()
        self.evaluator = Evaluator(angle_unit)
    
    def calculate(self, expression: str) -> float:
        try:
            ast = self.parser.parse(expression)
            return self.evaluator.evaluate(ast)
        except CalculatorError as e:
            raise
        except Exception as e:
            raise CalculatorError(f"Unexpected error: {str(e)}") from e

def interactive_mode(angle_unit='radian'):
    print(f"Калькулятор (углы в {'градусах' if angle_unit == 'degree' else 'радианах'})")
    print("Для выхода введите 'exit' или 'quit'")
    
    calc = Calculator(angle_unit=angle_unit)
    
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
    parser.add_argument('--degree', action='store_true', help='Использовать градусы вместо радиан')
    
    args = parser.parse_args()
    
    angle_unit = 'degree' if args.degree else 'radian'
    calc = Calculator(angle_unit=angle_unit)
    
    if args.interactive:
        interactive_mode(angle_unit)
    elif args.expression:
        try:
            result = calc.calculate(args.expression)
            print(result)
        except CalculatorError as e:
            print(f"Ошибка: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
