"""
CSC410 Final Project: Enumerative Synthesizer
by Victor Nicolet and Danya Lette

Fill in this file to complete the verification portion
of the assignment.
"""

from z3 import *
from lang.ast import *


def validator(vars: dict, formula: Expression) -> bool:
    # formula is True or False, 1, 2, etc
    if isinstance(formula, IntConst) or isinstance(formula, BoolConst):
        return formula.value

    # formula is 'x' or 'y', then return ex. 'int_x'
    if isinstance(formula, VarExpr):
        return vars[formula.name]

    # Unary expression case
    if isinstance(formula, UnaryExpr):
        operator = formula.operator
        operand = formula.operand

        # Not operator
        if operator.value == 1:
            if isinstance(operand, VarExpr):
                return Not(vars[operand.name])
            elif isinstance(operand, BoolConst):
                return Not(operand.value)
            elif isinstance(operand, Expression):
                return Not(validator(vars, operand))

        # Absolute value operator
        elif operator.value == 2:
            if isinstance(operand, VarExpr):
                return If(vars[operand.name] > 0, vars[operand.name], -vars[operand.name])
            elif isinstance(operand, IntConst):
                return If(operand.value > 0, operand.value, -operand.value)
            elif isinstance(operand, Expression):
                result = validator(vars, operand)
                return If(result > 0, result, - result)

        # Negative operator
        elif operator.value == 3:
            if isinstance(operand, VarExpr):
                return -vars[operand.name]
            elif isinstance(operand, IntConst):
                return -operand.value
            elif isinstance(operand, Expression):
                return -validator(vars, operand)

    # If then else Expression case
    if isinstance(formula, Ite):
        cond = formula.cond
        true_br = formula.true_br
        false_br = formula.false_br

        if isinstance(true_br, IntConst) and isinstance(false_br, IntConst):
            return If(validator(vars, cond), true_br.value, false_br.value)
        elif isinstance(true_br, BoolConst) and isinstance(false_br, BoolConst):
            return If(validator(vars, cond), true_br.value, false_br.value)
        elif isinstance(true_br, BoolConst) and isinstance(false_br, IntConst):
            return If(validator(vars, cond), true_br.value, false_br.value)
        elif isinstance(true_br, IntConst) and isinstance(false_br, BoolConst):
            return If(validator(vars, cond), true_br.value, false_br.value)
        elif isinstance(true_br, IntConst) and isinstance(false_br, VarExpr):
            return If(validator(vars, cond), true_br.value, vars[false_br.name])
        elif isinstance(true_br, BoolConst) and isinstance(false_br, VarExpr):
            return If(validator(vars, cond), true_br.value, vars[false_br.name])
        elif isinstance(true_br, VarExpr) and isinstance(false_br, IntConst):
            return If(validator(vars, cond), vars[true_br.name], false_br.value)
        elif isinstance(true_br, VarExpr) and isinstance(false_br, BoolConst):
            return If(validator(vars, cond), vars[true_br.name], false_br.value)
        elif isinstance(true_br, VarExpr) and isinstance(false_br, VarExpr):
            return If(validator(vars, cond), vars[true_br.name], vars[false_br.name])
        elif isinstance(true_br, VarExpr) and isinstance(false_br, Expression):
            return If(validator(vars, cond), vars[true_br.name], validator(vars, false_br))
        elif isinstance(true_br, Expression) and isinstance(false_br, VarExpr):
            return If(validator(vars, cond), validator(vars, true_br), vars[false_br.name])
        elif isinstance(true_br, IntConst) and isinstance(false_br, Expression):
            return If(validator(vars, cond), true_br.value, validator(vars, false_br))
        elif isinstance(true_br, BoolConst) and isinstance(false_br, Expression):
            return If(validator(vars, cond), true_br.value, validator(vars, false_br))
        elif isinstance(true_br, Expression) and isinstance(false_br, IntConst):
            return If(validator(vars, cond), validator(vars, true_br), false_br.value)
        elif isinstance(true_br, Expression) and isinstance(false_br, BoolConst):
            cond = validator(vars, cond)
            true_br = validator(vars, true_br)
            return If(cond, true_br, false_br.value)
        elif isinstance(true_br, Expression) and isinstance(false_br, Expression):
            return If(validator(vars, cond), validator(vars, true_br), validator(vars, false_br))

    # Binary Expression case
    if isinstance(formula, BinaryExpr):
        operator = formula.operator
        lhs = formula.left_operand
        rhs = formula.right_operand

        # addition operator
        if operator.value == 1:
            if isinstance(lhs, IntConst) and isinstance(rhs, IntConst):
                return lhs.value + rhs.value
            elif isinstance(lhs, VarExpr) and isinstance(rhs, IntConst):
                return vars[lhs.name] + rhs.value
            elif isinstance(lhs, IntConst) and isinstance(rhs, VarExpr):
                return lhs.value + vars[rhs.name]
            elif isinstance(lhs, VarExpr) and isinstance(rhs, VarExpr):
                return vars[lhs.name] + vars[rhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, VarExpr):
                return (validator(vars, lhs)) + vars[rhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, IntConst):
                return (validator(vars, lhs)) + rhs.value
            elif isinstance(lhs, VarExpr) and isinstance(rhs, Expression):
                return vars[lhs.name] + (validator(vars, rhs))
            elif isinstance(lhs, IntConst) and isinstance(rhs, Expression):
                return lhs.value + (validator(vars, rhs))
            elif isinstance(lhs, Expression) and isinstance(rhs, Expression):
                return (validator(vars, lhs)) + (validator(vars, rhs))

        # subtraction operator
        elif operator.value == 2:
            if isinstance(lhs, IntConst) and isinstance(rhs, IntConst):
                return lhs.value - rhs.value
            elif isinstance(lhs, VarExpr) and isinstance(rhs, IntConst):
                return vars[lhs.name] - rhs.value
            elif isinstance(lhs, IntConst) and isinstance(rhs, VarExpr):
                return lhs.value - vars[rhs.name]
            elif isinstance(lhs, VarExpr) and isinstance(rhs, VarExpr):
                return vars[lhs.name] - vars[rhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, VarExpr):
                return (validator(vars, lhs)) - vars[rhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, IntConst):
                return (validator(vars, lhs)) - rhs.value
            elif isinstance(lhs, VarExpr) and isinstance(rhs, Expression):
                return vars[lhs.name] - (validator(vars, rhs))
            elif isinstance(lhs, IntConst) and isinstance(rhs, Expression):
                return lhs.value - (validator(vars, rhs))
            elif isinstance(lhs, Expression) and isinstance(rhs, Expression):
                return (validator(vars, lhs)) - (validator(vars, rhs))

        # Multiplication operator
        elif operator.value == 3:
            if isinstance(lhs, IntConst) and isinstance(rhs, IntConst):
                return lhs.value * rhs.value
            elif isinstance(lhs, VarExpr) and isinstance(rhs, IntConst):
                return vars[lhs.name] * rhs.value
            elif isinstance(lhs, IntConst) and isinstance(rhs, VarExpr):
                return lhs.value * vars[rhs.name]
            elif isinstance(lhs, VarExpr) and isinstance(rhs, VarExpr):
                return vars[lhs.name] * vars[rhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, VarExpr):
                return (validator(vars, lhs)) * vars[rhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, IntConst):
                return (validator(vars, lhs)) * rhs.value
            elif isinstance(lhs, VarExpr) and isinstance(rhs, Expression):
                return vars[lhs.name] * (validator(vars, rhs))
            elif isinstance(lhs, IntConst) and isinstance(rhs, Expression):
                return lhs.value * (validator(vars, rhs))
            elif isinstance(lhs, Expression) and isinstance(rhs, Expression):
                return (validator(vars, lhs)) * (validator(vars, rhs))

        # Division operator
        elif operator.value == 4:
            if isinstance(lhs, IntConst) and isinstance(rhs, IntConst):
                return lhs.value / rhs.value
            elif isinstance(lhs, VarExpr) and isinstance(rhs, IntConst):
                return vars[lhs.name] / rhs.value
            elif isinstance(lhs, IntConst) and isinstance(rhs, VarExpr):
                return lhs.value / vars[rhs.name]
            elif isinstance(lhs, VarExpr) and isinstance(rhs, VarExpr):
                return vars[lhs.name] / vars[rhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, VarExpr):
                return (validator(vars, lhs)) / vars[rhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, IntConst):
                return (validator(vars, lhs)) / rhs.value
            elif isinstance(lhs, VarExpr) and isinstance(rhs, Expression):
                return vars[lhs.name] / (validator(vars, rhs))
            elif isinstance(lhs, IntConst) and isinstance(rhs, Expression):
                return lhs.value / (validator(vars, rhs))
            elif isinstance(lhs, Expression) and isinstance(rhs, Expression):
                return (validator(vars, lhs)) / (validator(vars, rhs))

        # modulo operator
        elif operator.value == 5:
            if isinstance(lhs, IntConst) and isinstance(rhs, IntConst):
                return lhs.value % rhs.value
            elif isinstance(lhs, VarExpr) and isinstance(rhs, IntConst):
                return vars[lhs.name] % rhs.value
            elif isinstance(lhs, IntConst) and isinstance(rhs, VarExpr):
                return lhs.value % vars[rhs.name]
            elif isinstance(lhs, VarExpr) and isinstance(rhs, VarExpr):
                return vars[lhs.name] % vars[rhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, VarExpr):
                return (validator(vars, lhs)) % vars[rhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, IntConst):
                return (validator(vars, lhs)) % rhs.value
            elif isinstance(lhs, VarExpr) and isinstance(rhs, Expression):
                return vars[lhs.name] % (validator(vars, rhs))
            elif isinstance(lhs, IntConst) and isinstance(rhs, Expression):
                return lhs.value % (validator(vars, rhs))
            elif isinstance(lhs, Expression) and isinstance(rhs, Expression):
                return (validator(vars, lhs)) % (validator(vars, rhs))

        # Equality operator
        elif operator.value == 6:
            if isinstance(lhs, IntConst) and isinstance(rhs, IntConst):
                return lhs.value == rhs.value
            if isinstance(lhs, VarExpr) and isinstance(rhs, VarExpr):
                return vars[lhs.name] == vars[rhs.name]
            elif isinstance(lhs, VarExpr) and isinstance(rhs, IntConst):
                return vars[lhs.name] == rhs.value
            elif isinstance(lhs, IntConst) and isinstance(rhs, VarExpr):
                return lhs.value == vars[rhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, VarExpr):
                return (validator(vars, lhs)) == vars[rhs.name]
            elif isinstance(rhs, Expression) and isinstance(lhs, VarExpr):
                return (validator(vars, rhs)) == vars[lhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, IntConst):
                return (validator(vars, lhs)) == rhs.value
            elif isinstance(rhs, Expression) and isinstance(lhs, IntConst):
                return (validator(vars, rhs)) == lhs.value
            elif isinstance(lhs, Expression) and isinstance(rhs, Expression):
                return (validator(vars, lhs)) == (validator(vars, rhs))

        # Greater than operator
        elif operator.value == 7:
            if isinstance(lhs, IntConst) and isinstance(rhs, IntConst):
                return lhs.value > rhs.value
            elif isinstance(lhs, VarExpr) and isinstance(rhs, VarExpr):
                return vars[lhs.name] > vars[rhs.name]
            elif isinstance(lhs, VarExpr) and isinstance(rhs, IntConst):
                return vars[lhs.name] > rhs.value
            elif isinstance(lhs, IntConst) and isinstance(rhs, VarExpr):
                return lhs.value > vars[rhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, VarExpr):
                return (validator(vars, lhs)) > vars[rhs.name]
            elif isinstance(rhs, Expression) and isinstance(lhs, VarExpr):
                lhs = vars[lhs.name]
                rhs = validator(vars, rhs)
                return lhs > rhs
            elif isinstance(lhs, Expression) and isinstance(rhs, IntConst):
                return (validator(vars, lhs)) > rhs.value
            elif isinstance(rhs, Expression) and isinstance(lhs, IntConst):
                return lhs.value > (validator(vars, rhs))
            elif isinstance(lhs, Expression) and isinstance(rhs, Expression):
                return (validator(vars, lhs)) > (validator(vars, rhs))

        # Greater than or equal to
        elif operator.value == 8:
            if isinstance(lhs, IntConst) and isinstance(rhs, IntConst):
                return lhs.value >= rhs.value
            elif isinstance(lhs, VarExpr) and isinstance(rhs, VarExpr):
                return vars[lhs.name] >= vars[rhs.name]
            elif isinstance(lhs, VarExpr) and isinstance(rhs, IntConst):
                return vars[lhs.name] >= rhs.value
            elif isinstance(lhs, IntConst) and isinstance(rhs, VarExpr):
                return lhs.value >= vars[rhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, VarExpr):
                return (validator(vars, lhs)) >= vars[rhs.name]
            elif isinstance(rhs, Expression) and isinstance(lhs, VarExpr):
                return vars[lhs.name] >= (validator(vars, rhs))
            elif isinstance(lhs, Expression) and isinstance(rhs, IntConst):
                return (validator(vars, lhs)) >= rhs.value
            elif isinstance(rhs, Expression) and isinstance(lhs, IntConst):
                return lhs.value >= (validator(vars, rhs))
            elif isinstance(lhs, Expression) and isinstance(rhs, Expression):
                return (validator(vars, lhs)) >= (validator(vars, rhs))

        # Less than operator
        elif operator.value == 9:
            if isinstance(lhs, IntConst) and isinstance(rhs, IntConst):
                return lhs.value < rhs.value
            elif isinstance(lhs, VarExpr) and isinstance(rhs, VarExpr):
                return vars[lhs.name] < vars[rhs.name]
            elif isinstance(lhs, VarExpr) and isinstance(rhs, IntConst):
                return vars[lhs.name] < rhs.value
            elif isinstance(lhs, IntConst) and isinstance(rhs, VarExpr):
                return lhs.value < vars[rhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, VarExpr):
                return (validator(vars, lhs)) < vars[rhs.name]
            elif isinstance(rhs, Expression) and isinstance(lhs, VarExpr):
                return vars[lhs.name] < (validator(vars, rhs))
            elif isinstance(lhs, Expression) and isinstance(rhs, IntConst):
                return (validator(vars, lhs)) < rhs.value
            elif isinstance(rhs, Expression) and isinstance(lhs, IntConst):
                return lhs.value < (validator(vars, rhs))
            elif isinstance(lhs, Expression) and isinstance(rhs, Expression):
                return (validator(vars, lhs)) < (validator(vars, rhs))

        # Less than or equal to operator
        elif operator.value == 10:
            if isinstance(lhs, IntConst) and isinstance(rhs, IntConst):
                return lhs.value <= rhs.value
            elif isinstance(lhs, VarExpr) and isinstance(rhs, VarExpr):
                return vars[lhs.name] <= vars[rhs.name]
            elif isinstance(lhs, VarExpr) and isinstance(rhs, IntConst):
                return vars[lhs.name] <= rhs.value
            elif isinstance(lhs, IntConst) and isinstance(rhs, VarExpr):
                return lhs.value <= vars[rhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, VarExpr):
                return (validator(vars, lhs)) <= vars[rhs.name]
            elif isinstance(rhs, Expression) and isinstance(lhs, VarExpr):
                return vars[lhs.name] <= (validator(vars, rhs))
            elif isinstance(lhs, Expression) and isinstance(rhs, IntConst):
                return (validator(vars, lhs)) <= rhs.value
            elif isinstance(rhs, Expression) and isinstance(lhs, IntConst):
                return lhs.value <= (validator(vars, rhs))
            elif isinstance(lhs, Expression) and isinstance(rhs, Expression):
                return (validator(vars, lhs)) <= (validator(vars, rhs))

        # And operator
        elif operator.value == 11:
            if isinstance(lhs, BoolConst) and isinstance(rhs, BoolConst):
                return And(lhs.value, rhs.value)
            elif isinstance(lhs, BoolConst) and isinstance(rhs, VarExpr):
                return And(lhs.value, vars[rhs.name])
            elif isinstance(lhs, VarExpr) and isinstance(rhs, BoolConst):
                return And(vars[lhs.name], rhs.value)
            elif isinstance(lhs, VarExpr) and isinstance(rhs, VarExpr):
                return And(vars[lhs.name], vars[rhs.name])
            elif isinstance(lhs, Expression) and isinstance(rhs, BoolConst):
                return And(validator(vars, lhs), rhs.value)
            elif isinstance(lhs, BoolConst) and isinstance(rhs, Expression):
                return And(lhs.value, validator(vars, rhs))
            elif isinstance(lhs, Expression) and isinstance(rhs, VarExpr):
                return And(validator(vars, lhs), vars[rhs.name])
            elif isinstance(lhs, VarExpr) and isinstance(rhs, Expression):
                return And(vars[lhs.name], validator(vars, rhs))
            elif isinstance(lhs, Expression) and isinstance(rhs, Expression):
                lhs = validator(vars, lhs)
                rhs = validator(vars, rhs)
                return And(lhs, rhs)

        # Or operator
        elif operator.value == 12:
            if isinstance(lhs, BoolConst) and isinstance(rhs, BoolConst):
                return Or(lhs.value, rhs.value)
            elif isinstance(lhs, BoolConst) and isinstance(rhs, VarExpr):
                return Or(lhs.value, vars[rhs.name])
            elif isinstance(lhs, VarExpr) and isinstance(rhs, BoolConst):
                return Or(vars[lhs.name], rhs.value)
            elif isinstance(lhs, VarExpr) and isinstance(rhs, VarExpr):
                return Or(vars[lhs.name], vars[rhs.name])
            elif isinstance(lhs, Expression) and isinstance(rhs, BoolConst):
                return Or(validator(vars, lhs), rhs.value)
            elif isinstance(lhs, BoolConst) and isinstance(rhs, Expression):
                return Or(lhs.value, validator(vars, rhs))
            elif isinstance(lhs, Expression) and isinstance(rhs, VarExpr):
                return Or(validator(vars, lhs), vars[rhs.name])
            elif isinstance(lhs, VarExpr) and isinstance(rhs, Expression):
                return Or(vars[lhs.name], validator(vars, rhs))
            elif isinstance(lhs, Expression) and isinstance(rhs, Expression):
                return Or(validator(vars, lhs), validator(vars, rhs))

        # not equal operator
        elif operator.value == 13:
            if isinstance(lhs, IntConst) and isinstance(rhs, IntConst):
                return lhs.value != rhs.value
            elif isinstance(lhs, VarExpr) and isinstance(rhs, VarExpr):
                return vars[lhs.name] != vars[rhs.name]
            elif isinstance(lhs, VarExpr) and isinstance(rhs, IntConst):
                return vars[lhs.name] != rhs.value
            elif isinstance(lhs, IntConst) and isinstance(rhs, VarExpr):
                return lhs.value != vars[rhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, VarExpr):
                return (validator(vars, lhs)) != vars[rhs.name]
            elif isinstance(rhs, Expression) and isinstance(lhs, VarExpr):
                return (validator(vars, rhs)) != vars[lhs.name]
            elif isinstance(lhs, Expression) and isinstance(rhs, IntConst):
                return (validator(vars, lhs)) != rhs.value
            elif isinstance(rhs, Expression) and isinstance(lhs, IntConst):
                return (validator(vars, rhs)) != lhs.value
            elif isinstance(lhs, Expression) and isinstance(rhs, Expression):
                return (validator(vars, lhs)) != (validator(vars, rhs))


def create_var_dict(varList: list) -> dict:
    vars = {}
    for var in varList:
        if var.name not in vars:
            # int
            if var.type.value == 1:
                vars[var.name] = Int(var.name)
            # bool
            else:
                vars[var.name] = Bool(var.name)
    return vars


def is_valid(formula: Expression) -> bool:
    """
    Returns true if the formula is valid.

    """
    # It should return true if the formula is valid.
    # To check that the formula is valid, you should use the Z3 api
    # use a recursive function for this

    # This handles the simple cases of basic_true and basic_false
    if isinstance(formula, BoolConst) or isinstance(formula, IntConst):
        return formula.value

    s = Solver()
    vars = create_var_dict(list(formula.uses()))
    clause = validator(vars, formula)
    # print(clause)
    s.add(Not(clause))
    return s.check() == unsat
