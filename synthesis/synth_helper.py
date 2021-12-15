from z3 import *
from lang.ast import *

"""
A helper methods file for synth methods.
Mainly focus on z3 stuffs in this file.
"""


def create_clause(expr: Expression, suffix: List[int]):
        """
        Given an expression, create a z3 clause based on the expression
        When creating z3 variables, use (Variable.name + suffix) as the name of the variable
        Suffix is passed down as a pointer to string, used for creating GrammarInt z3 variable
        Pre-condition: NO GrammarInt & GrammarVar in the expression!!!
        """
        if isinstance(expr, IntConst):
            return expr.value
        elif isinstance(expr, BoolConst):
            return expr.value
        elif isinstance(expr, VarExpr):
            if expr.var.type.value == 1:
                # Int
                return Int(expr.var.name)
            else:
                # Bool
                return Bool(expr.var.name)
        elif isinstance(expr, UnaryExpr):
            operator = expr.operator
            operand = expr.operand

            clause = create_clause(operand, suffix)

            if operator.value == 1:
                # NOT
                return Not(clause)
            elif operator.value == 2:
                # ABS
                return If(clause > 0, clause, -clause)
            else:
                # NEG
                return -clause
        elif isinstance(expr, BinaryExpr):
            operator = expr.operator
            lhs = create_clause(expr.left_operand, suffix)
            rhs = create_clause(expr.right_operand, suffix)

            if operator.value == 1:
                # PLUS
                return lhs + rhs
            elif operator.value == 2:
                # MINUS
                return lhs - rhs
            elif operator.value == 3:
                # TIMES
                return lhs * rhs
            elif operator.value == 4:
                # DIV
                return lhs / rhs
            elif operator.value == 5:
                # MODULO
                return lhs % rhs
            elif operator.value == 6:
                # EQUALS
                return lhs == rhs
            elif operator.value == 7:
                # GREATER
                return lhs > rhs
            elif operator.value == 8:
                # GREATER_EQ
                return lhs >= rhs
            elif operator.value == 9:
                # LESSTHAN
                return lhs < rhs
            elif operator.value == 10:
                # LESSTHAN_EQ
                return lhs <= rhs
            elif operator.value == 11:
                # AND
                return And(lhs, rhs)
            elif operator.value == 12:
                # OR
                return Or(lhs, rhs)
            elif operator.value == 13:
                # NOTEQUAL
                return lhs != rhs
        elif isinstance(expr, Ite):
            cond = create_clause(expr.cond, suffix)
            true_br = create_clause(expr.true_br, suffix)
            false_br = create_clause(expr.false_br, suffix)

            return If(cond, true_br, false_br)
        elif isinstance(expr, GrammarInteger):
            number = suffix[0]
            suffix[0] += 1
            return Int('Integer' + f'_{number}')

        raise TypeError

def duplicate(new_expr: Expression, exprs: List[Expression]) -> bool:
    """
    Given two pure recursive expressions, check if two are equivalent
    Return a boolean, True if two expressions are equivalent
    """

    c1 = create_clause(new_expr, [])
    c2s = [create_clause(expr, []) for expr in exprs]

    s = Solver()
    c = [(c1 != c2) for c2 in c2s]
    s.add(Or(c))
    return s.check() != unsat
