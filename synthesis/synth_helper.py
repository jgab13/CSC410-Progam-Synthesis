from z3 import *
from lang.ast import *

"""
A helper methods file for synth methods.
Mainly focus on z3 in this file.
"""


def create_clause(expr: Expression, suffix: str):
    """
    Given an expression, create a z3 clause based on the expression
    When creating z3 variables, use (Variable.name + suffix) as the name of the variable
    Pre-condition: NO GrammarInt & GrammarVar in the expression
    """
    if isinstance(expr, IntConst):
        return expr.value
    elif isinstance(expr, BoolConst):
        return expr.value
    elif isinstance(expr, VarExpr):
        if expr.var.type.value == 1:
            # Int
            return Int(expr.var.name + suffix)
        else:
            # Bool
            return Bool(expr.var.name + suffix)
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

    raise TypeError


def create_grammarint_expr(expr: Expression, counter: List[int]):
    """
    Create a new Expression, replacing all GrammarInt with VarExpr.
    Each replaced VarExpr will have a name of "Int_{num}".
    The counter acts as a counter in C, or a global variable
    """
    if isinstance(expr, IntConst):
        return expr
    elif isinstance(expr, BoolConst):
        return expr
    elif isinstance(expr, VarExpr):
        return expr
    elif isinstance(expr, UnaryExpr):
        return UnaryExpr(expr.operator, create_grammarint_expr(expr, counter))
    elif isinstance(expr, BinaryExpr):
        return BinaryExpr(expr.operator,
                          create_grammarint_expr(expr.left_operand, counter),
                          create_grammarint_expr(expr.right_operand, counter))
    elif isinstance(expr, Ite):
        return Ite(create_grammarint_expr(expr.cond, counter),
                   create_grammarint_expr(expr.true_br, counter),
                   create_grammarint_expr(expr.false_br, counter))
    elif isinstance(expr, GrammarInteger):
        var = Variable(f'Int_{counter[0]}', PaddleType.INT)
        res = VarExpr(var, f'Int_{counter[0]}')
        counter[0] += 1
        return res

    raise TypeError


def sub_int(model, expr: Expression) -> Expression:
    if isinstance(expr, IntConst):
        return expr
    elif isinstance(expr, BoolConst):
        return expr
    elif isinstance(expr, VarExpr):
        if (expr.var.name.startswith('Int_')):
            res = model[Int(expr.name)]
            if (res is None):
                res = 0
            else:
                res = res.as_long()
            return IntConst(res)
        else:
            return expr
    elif isinstance(expr, UnaryExpr):
        return UnaryExpr(expr.operator, sub_int(model, expr))
    elif isinstance(expr, BinaryExpr):
        return BinaryExpr(expr.operator,
                          sub_int(model, expr.left_operand),
                          sub_int(model, expr.right_operand))
    elif isinstance(expr, Ite):
        return Ite(sub_int(expr.cond),
                   sub_int(model, expr.true_br),
                   sub_int(model, expr.false_br))

    pass


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
