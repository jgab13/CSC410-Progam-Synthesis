"""
CSC410 Final Project: Enumerative Synthesizer
by Victor Nicolet and Danya Lette
Fill in this file to complete the synthesis portion
of the assignment.
"""

from typing import Mapping
from z3 import *
from lang.ast import *
from lang.symb_eval import Evaluator
from synthesis.synth_helper import *
from verification import verifier
import copy


class Synthesizer():
    """
    This class is has three methods `synth_method_1`, `synth_method_2` or
    `synth_method_3` for generating expression for a program's holes.
    You may also choose to add data attributes and methods to this class
    to enable instances of `Synthesizer` to remember information about
    previous runs.
    Calling `synth_method_1`, `synth_method_2` or `synth_method_3` should
    produce a new set of hole completions at each call for a given
    `Synthesizer` instance.
    For example, suppose the program p contains one hole `h1` with the
    grammar `[ G : int -> G + G | 0 | 1 ]`. Then, the following sequence
    is a possible execution:
    ```
    > s = Synthesizer(p)
    > s.synth_method_1()
    { "h1" : 0 }
    > s.synth_method_1()
    { "h1" : 1 }
    > s.synth_method_1()
    { "h1" : 0 + 1 }
    ...
    ```
    Each call produces a hole completion. The returned object should
    be a mapping from the hole id (its name) to the expression of the
    hole.
    Each `synth_method_..` should implement a different enumeration
    strategy (e.g. depth first, breadth first, constants-first,
    variables-first...).
    **Don't forget that we expect your third method to be the best on
    average!**
    *Hint*: the method `hole_can_use` in the `Program` class returns the
    set of variables that a given hole can use in its completions.
    e.g. `prog.hole_can_use("h1")` returns the variables that "h1" can use.
    """

    def __init__(self, ast: Program):
        """
        Initialize the Synthesizer.
        The Synthesizer can have a state or other data attributes and
        methods to remember which programs have been synthesized before.
        """
        self.state_number = 0
        # The synthesizer is initialized with the program ast it needs
        # to synthesize hole completions for.
        self.ast = ast

        # Track the current idx of the expanded recursive expression
        self.recurIdx = {}

        # A list of stored outputs waiting for synth_method to call
        self.outputs = {}

        # Output from the previous calls, used for GrammarIntSolver
        self.last_output = {}

        # Prerecursive is the initial recursive expressions
        self.prerecursive, self.constant = self.preprocess()
        self.recursive = copy.deepcopy(self.prerecursive)

    def preprocess(self):
        """
        Preprocess to fill self.recursive and self.constant dicts with the
        recursive rule or constant rule respectively
        """
        # Dictionary using hole.var.name as key, rule.symbol.name as second key
        # storing all recursive expression for expand
        recursive = {}

        # Dictionary using hole.var.name as first key, rule.symbol.name as second
        # key storing all constant expression for substitution
        constant = {}

        for hole in self.ast.holes:
            hole_name = hole.var.name

            recursive[hole_name] = {}
            constant[hole_name] = {}

            for rule_indx in range(len(hole.grammar.rules)):
                rule = hole.grammar.rules[rule_indx]
                recursive[hole_name][rule.symbol.name] = []
                constant[hole_name][rule.symbol.name] = []
                for production in rule.productions:
                    # Constant expressions are IntConst, BoolConst, GrammarInt, GrammarVar
                    if(self.ast.is_pure_expression(production) or
                            isinstance(production, GrammarInteger) or
                            isinstance(production, GrammarVar)):

                        # Check for GrammarVar
                        if isinstance(production, GrammarVar):
                            # Use hole_can_use to get all usable variables, only take same type
                            valid_vars = [VarExpr(var, var.name)
                                          for var in self.ast.hole_can_use(hole_name)
                                          if var.type == rule.symbol.type]

                            constant[hole_name][rule.symbol.name].extend(valid_vars)
                        else:
                            constant[hole_name][rule.symbol.name].append(production)
                    else:
                        recursive[hole_name][rule.symbol.name].append(production)

            # If there's any GrammarInteger in the constant
            if any(isinstance(expr, GrammarInteger) for expr in constant[hole_name][rule.symbol.name]):
                # Some basic pruning for GrammarInt:
                # 1. Remove all other InstConst
                # 2. If GrammarInt is the only constant, add a IntConst(0) for GrammarIntSolver (Scrach)
                # 2. Maybe design a special case in grammarIntSolver if int is the only constant
                constant[hole_name][rule.symbol.name] =\
                    [expr for expr in constant[hole_name][rule.symbol.name] if not isinstance(expr, IntConst)]

            # Initialize self.outputs and self.recurIdx
            self.recurIdx[hole_name] = 0
            main_prod_name = hole.grammar.rules[0].symbol.name
            self.outputs[hole_name] = []
            self.outputs[hole_name].extend(constant[hole_name][main_prod_name])

            # Initialize self.last_output
            self.last_output[hole_name] = None

        return recursive, constant

    def grammarIntSolver(self, expr: Expression, hole_name: str) -> Expression:
        """
        Given a almost pure expression (pure expression except having garmmarInt),
        solve for the integer value using z3
        Return a solved expression, None if unsat (no solution)
        """
        # raise NotImplementedError

        sub_state = self.last_output.copy()

        counter = [0]
        grammarint_expr = create_grammarint_expr(expr, counter)
        sub_state[hole_name] = grammarint_expr

        # Check if there's a hole hasn't output
        for key in sub_state:
            # key is hole_name
            if sub_state[key] is None:
                # key hasn't output
                # Get the name of the main production
                empty_main_prod_name = \
                    [hole.grammar.rules[0].symbol.name for hole in self.ast.holes if hole.var.name == key][0]
                sub_state[key] = self.constant[key][empty_main_prod_name][0]
                if isinstance(sub_state[key], GrammarInteger):
                    sub_state[key] = IntConst(1)

        evaluator = Evaluator(sub_state)
        final_constraint_expr = evaluator.evaluate(self.ast)
        clauses = [create_clause(final_constraint_expr, '')]
        input_var = []
        for var in final_constraint_expr.uses():
            if not var.name.startswith('Int_'):
                if var.type.value == 1:
                    # Int
                    input_var.append(Int(var.name))
                else:
                    # Bool
                    input_var.append(Bool(var.name))

        s = Solver()
        # Set div0 and mod0 to be 0
        x = Int('INTEGER')
        clauses.append(x / 0 == 0)
        clauses.append(x % 0 == 0)

        if input_var:
            s.add(ForAll(input_var, And(clauses)))
        else:
            s.add(And(clauses))

        # Set a 0.5 second timer on z3 solver
        s.set("timeout", 500)

        if s.check() == sat:
            model = s.model()
            new_expr = sub_int(model, grammarint_expr)
            return new_expr
        else:
            return None

    def expand(self, recur: Expression, hole_name: str) -> List[Expression]:
        """
        Given a recursive expression, name of the current hole.
        Expand the expression into more recursive expressions, return a list of expanded experssiosn
        Call expand and substitute together when self.output[hole] is empty??
        Please call equality check outside
        """
        if self.ast.is_pure_expression(recur):
            return [recur]

        result = []
        if isinstance(recur, VarExpr):
            # If the expressions is just the recursive var
            name = recur.var.name
            result.extend(self.prerecursive[hole_name][name])
        elif isinstance(recur, UnaryExpr):
            # Expand recursively on the unary operand
            for expr in self.expand(recur.operand, hole_name):
                result.append(UnaryExpr(recur.operator, expr))
        elif isinstance(recur, BinaryExpr):
            # Note simple pruning can be added for:
            # If two operands are the same and the operator is commutative (add, multiply, equality etc.)
            commutative = [1, 3, 6, 10, 11, 12, 13]
            if(str(recur.left_operand) == str(recur.right_operand)
                    and recur.operator.value in commutative):
                for expr in self.expand(recur.left_operand, hole_name):
                    result.append(BinaryExpr(recur.operator, expr, recur.right_operand))
            else:
                # Expand recursively on the left operand
                for expr in self.expand(recur.left_operand, hole_name):
                    result.append(BinaryExpr(recur.operator, expr, recur.right_operand))
                # Expand recursively on the right operand
                for expr in self.expand(recur.right_operand, hole_name):
                    result.append(BinaryExpr(recur.operator, recur.left_operand, expr))
        elif isinstance(recur, Ite):
            # Expand recursively on the condition
            for expr in self.expand(recur.cond, hole_name):
                result.append(Ite(expr, recur.true_br, recur.false_br))

            # Expand recursively on the true branch
            for expr in self.expand(recur.true_br, hole_name):
                result.append(Ite(recur.cond, expr, recur.false_br))

            # Expand recursively on the false branch
            for expr in self.expand(recur.false_br, hole_name):
                result.append(Ite(recur.cond, recur.true_br, expr))
        else:
            # Only reach here if the intial grammar_expression has none fully recursive expression
            # Such as (True ? G : G) or (2 > G)
            result.append(recur)

        return result

    def substitute(self, recur: Expression, hole_name: str) -> List[Expression]:
        """
        Given a recursive defined expression, substitute all constant in it
        Return a list of substituted expression
        """
        if self.ast.is_pure_expression(recur):
            return [recur]

        result = []
        if isinstance(recur, VarExpr):
            # Example: "G" -> [x,y]
            result = self.constant[hole_name][recur.var.name]

        elif isinstance(recur, UnaryExpr):
            # Substitute recursively on the unary operand
            for expr in self.substitute(recur.operand, hole_name):
                result.append(UnaryExpr(recur.operator, expr))

        elif isinstance(recur, BinaryExpr):
            # Substitute recursively on both side
            for lhs_expr in self.substitute(recur.left_operand, hole_name):
                for rhs_expr in self.substitute(recur.right_operand, hole_name):
                    if not (str(lhs_expr) == str(rhs_expr) and recur.operator.value in [11, 12]):
                        result.append(BinaryExpr(recur.operator, lhs_expr, rhs_expr))
                    # Similarly, some simple pruning can be added here

        elif isinstance(recur, Ite):
            # Substitute recursively on all three expressions
            for cond_expr in self.substitute(recur.cond, hole_name):
                for true_expr in self.substitute(recur.true_br, hole_name):
                    for false_expr in self.substitute(recur.false_br, hole_name):
                        result.append(Ite(cond_expr, true_expr, false_expr))

        else:
            # Only reach here if the intial grammar_expression has none fully recursive expression
            result.append(recur)

        return result

    def synth_main(self) -> Mapping[str, Expression]:
        """
        The main algorithm method for synthesising.
        """
        res = {}

        for hole in self.ast.holes:
            hole_name = hole.var.name
            main_prod_name = hole.grammar.rules[0].symbol.name

            res_expr = None
            while res_expr is None:
                if not self.outputs[hole_name]:
                    # The output list is empty for this hole

                    # Check if the produciton rules are finite
                    if self.recurIdx[hole_name] == len(self.recursive[hole_name][main_prod_name]):
                        # There is no more recursive expression that we can expand
                        # We've tried every possible hole_completion
                        # return a dummy data (last output value) instead
                        res_expr = self.last_output[hole_name]
                        if res_expr is None:
                            res_expr = self.constant[hole_name][main_prod_name][0]
                            if isinstance(res_expr, GrammarInteger):
                                res_expr = IntConst(1)
                        break
                    else:
                        # A do_while loop prevent the preventing VarExpr without constant
                        do_while = True
                        while do_while or not self.outputs[hole_name]:
                            currRecur = self.recursive[hole_name][main_prod_name][self.recurIdx[hole_name]]
                            new_recurs = self.expand(currRecur, hole_name)

                            self.recursive[hole_name][main_prod_name].extend(new_recurs)

                            # Update self.recurIdx
                            self.recurIdx[hole_name] += 1

                            self.outputs[hole_name] = self.substitute(currRecur, hole_name)
                            do_while = False

                res_expr = self.outputs[hole_name].pop(0)

                # Check if a GrammarInt is in the expression
                # Having GrammarInt in the expression is the only reason of a False in is_pure_expression check
                if not self.ast.is_pure_expression(res_expr):
                    res_expr = self.grammarIntSolver(res_expr, hole_name)

            res[hole_name] = res_expr

        self.last_output = res
        return res

    def synth_method_1(self,) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 1).
        **
        A variable first algorithm. Variables are priortized over constants and will be evaluated first.
        constants will also get evaluated right after all the constants so that the potential correct hole completion
        won't be missed.
        **
        """
        # make it variable first
        constant_save = self.constant.copy()
        for hole in self.constant:
            for prod in self.constant[hole]:
                # put all constants in front of all vars
                i = 0
                while i < len(self.constant[hole][prod]):
                    if not (isinstance(self.constant[hole][prod][i], IntConst) or
                            isinstance(self.constant[hole][prod][i], BoolConst)):
                        # put const at the beginning of the list
                        var = self.constant[hole][prod].pop(i)
                        self.constant[hole][prod].insert(0, var)
                    i += 1

        res = self.synth_main()
        self.constant = constant_save
        return res

    def synth_method_2(self,) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 2).
        **A constant first algorithm. constants are priortized over variables and will be evaluated first.
        Variables will also get evaluated right after all the constants so that the potential correct hole completion
        won't be missed. **
        """
        # make it constant first
        constant_save = self.constant.copy()
        for hole in self.constant:
            for prod in self.constant[hole]:
                # put all constants in front of all vars
                i = 0
                while i < len(self.constant[hole][prod]):
                    if (isinstance(self.constant[hole][prod][i], IntConst) or
                            isinstance(self.constant[hole][prod][i], BoolConst)):
                        # put const at the beginning of the list
                        const = self.constant[hole][prod].pop(i)
                        self.constant[hole][prod].insert(0, const)
                    i += 1
        res = self.synth_main()
        self.constant = constant_save
        return res

    def synth_method_3(self,) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 3).
        **This search algorithm uses BFS to expand the rules for each production rule, starting with primitives such as
        constants and variables. Then it builds recursive expressions based on these primitives and the process continues
        as increasingly nested recursive expressions are expanded and added to the queue. Simple pruning is used to remove
        unnecessary redundant expressions such as 'x1 && x1' or 'x1 || x1'. Additionally, we use z3 on any expression that
        contains a grammar integer to find a satisfying assignment.**
        """
        return self.synth_main()
