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

        self.prerecursive, self.constant = self.preprocess()
        self.recursive = copy.deepcopy(self.prerecursive)



    def preprocess(self):
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
        for var in expr.uses():
            if(var.type.value == 1):
                #Int
                input_var.append(Int(var.name))
            else:
                #Bool
                input_var.append(Bool(var.name))

        s = Solver()
        # Set div0 and mod0 to be 0
        x = Int('x')
        clauses.append(x / 0 == 0)
        clauses.append(x % 0 == 0)
 
        s.add(ForAll(input_var, And(clauses)))
        
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
                    if not (str(lhs_expr) == str(rhs_expr) and recur.operator.value in [6,10,11,12,13]):
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

    def synth_method_1(self,) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 1).

        **TODO: write a description of your approach in this method.**
        """
        # TODO : complete this method
        raise Exception("Synth.Synthesizer.synth_method_1 is not implemented.")

    def synth_method_2(self,) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 2).

        **TODO: write a description of your approach in this method.**
        """
        # TODO : complete this method
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
                        res[hole_name] = self.last_output[hole_name]
                    else:
                        # A do_while loop prevent the preventing VarExpr without constant
                        do_while = True
                        while do_while or not self.outputs[hole_name]:
                            currRecur = self.recursive[hole_name][main_prod_name][self.recurIdx[hole_name]]
                            new_recurs = self.expand(currRecur, hole_name)

                            # # Check duplicate
                            # for new_recur in new_recurs:
                            #     if not duplicate(new_recur, self.recursive[hole_name][main_prod_name]):
                            #         self.recursive[hole_name][main_prod_name].append(new_recur)
                            self.recursive[hole_name][main_prod_name].extend(new_recurs)

                            # Update self.recurIdx
                            self.recurIdx[hole_name] += 1

                            self.outputs[hole_name] = self.substitute(currRecur, hole_name)
                            do_while = False

                res_expr = self.outputs[hole_name].pop(0)

                if not self.ast.is_pure_expression(res_expr):
                    res_expr = self.grammarIntSolver(res_expr, hole_name)

            res[hole_name] = res_expr

        self.last_output = res
        return res
        # raise Exception("Synth.Synthesizer.synth_method_2 is not implemented.")

    def synth_method_3(self,) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 3).

        **TODO: write a description of your approach in this method.**
        """
        # TODO : complete this method
        raise Exception("Synth.synth_method_3 is not implemented.")
