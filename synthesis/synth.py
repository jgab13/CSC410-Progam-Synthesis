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
from verification import verifier


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
        # TODO : hole_dict should call preprocessing function to populate hole_dict
        self.hole_dict = self.preprocess()
        self.intCoutner = 0
        self.state = {}
    
    def preprocess(self):
        result = {}
        for hole in self.ast.holes:
            result[hole.var.name] = []
            holeType = hole.var.type

            for rule in hole.grammar.rules:
                if rule.symbol.type != holeType:
                    continue
                for production in rule.productions:
                    if(isinstance(production, GrammarVar)):
                        result[hole.var.name] += [VarExpr(var, var.name) for var in self.ast.hole_can_use(hole.var.name) if rule.symbol.type == var.type]
                    else:
                        result[hole.var.name].append(production)
        
        return result
    
    # Return a list of expanded Expressions
    # Pre-condtiion: production is not a pure_experssion, otherwise facing a infinite recursion if in FIFO data structures(Queue)
    def expand(self, hole: HoleDeclaration, production: Expression) -> List[Expression]:
        if(self.ast.is_pure_expression(production)):
            return [production]
        result = []
        rules = hole.grammar.rules

        def getExpressions(rules: List[ProductionRule], rule_name: str) -> List[Expression]:
            
            for rule in rules:
                if(rule.symbol.name == rule_name):
                    temp = []
                    for expression in rule.productions:
                        if isinstance(expression, GrammarVar):
                            temp += [VarExpr(var, var.name) for var in self.ast.hole_can_use(hole.var.name) if rule.symbol.type == var.type]
                        else:
                            temp.append(expression)
                    return temp

            return []

        if isinstance(production, Ite):
            # Expand the If condition
            if(not self.ast.is_almost_pure_expression(production.cond)):
                if_expressions = self.expand(hole, production.cond)
                result += [Ite(expre, production.true_br, production.false_br) for expre in if_expressions]
            
            # Expand the Then part
            if(not self.ast.is_almost_pure_expression(production.true_br)):
                true_expressions = self.expand(hole, production.true_br)
                result += [Ite(production.cond, expre, production.false_br) for expre in true_expressions]

            # Expand the Else part
            if(not self.ast.is_almost_pure_expression(production.false_br)):
                else_expressions = self.expand(hole, production.false_br)
                result += [Ite(production.cond, production.true_br, expre) for expre in else_expressions]

        elif isinstance(production, BinaryExpr):
            # Expand left operand
            if(not self.ast.is_almost_pure_expression(production.left_operand)):
                left_expressions = self.expand(hole, production.left_operand)
                result += [BinaryExpr(production.operator, expre, production.right_operand) for expre in left_expressions]

            # Expand right operand
            if(not self.ast.is_almost_pure_expression(production.right_operand)):
                right_expressions = self.expand(hole, production.right_operand)
                result += [BinaryExpr(production.operator, production.left_operand, expre) for expre in right_expressions]

        elif isinstance(production, UnaryExpr):
            expressions = self.expand(hole, production.operand)
            result = [UnaryExpr(production.operator, expre) for expre in expressions]
        elif isinstance(production, VarExpr):
            result = getExpressions(rules, VarExpr(production).name)
        elif isinstance(production, GrammarInteger):
            # THINGS TODO: What should we do with Integer??
            intName = f"Int_{self.intCoutner}"
            self.intCoutner += 1

            intVar = Variable(intName, PaddleType.INT)
            intExp = VarExpr(intVar, intName)
            result = [intExp]
        elif isinstance(production, GrammarVar):
            # GrammarVar shouldn't appear!
            pass

        return result
    
    def substitute(self, production: Expression, model) -> Expression:
        if(self.ast.is_pure_expression(production)):
            return production
        if isinstance(production, Ite):
            # Expand the If condition
            return(Ite(self.substitute(production.cond, model),
                self.substitute(production.true_br, model),
                self.substitute(production.false_br, model)
            ))
                

        elif isinstance(production, BinaryExpr):
            # Expand left operand
            return(BinaryExpr(production.operator,
                self.substitute(production.left_operand, model),
                self.substitute(production.right_operand, model)
            ))
                

        elif isinstance(production, UnaryExpr):
            return(UnaryExpr(production.operator,
                self.substitute(production.operand, model)
            ))

        elif isinstance(production, VarExpr):
            if(self.ast.is_almost_pure_expression(production)):
                # Assuming the name of the Integer variable in z3 is VarExpr.name
                return IntConst(model[Int(production.name)].as_long())
        
        return production

    #  pre-processing call to populate queue and stacks
    #  what to do with multiple production rules?
    #  populate queue in order for each production rule
    #  heuristic - put at the front of the queue?
    #
    # dictionary of queues - one queue for each hole
    # pre-process function (q, ast)
    #  populate queue with each expression for each production rule
    #  for each hole, for each production, each expression
    #  only add production rules if it is the sam type of the hole value

    #  synth_method call - return a mapping of hole to expression
    # for each hole - pop from the queue - if it's well-formed - add hole : q.pop() to mapping
    # iterate on the expression and add to the queue

    # Finish preprocessing
    # function call to expand recursive expression - should return a list of grammar expressions

    # other small methods to expand     

    # TODO: implement something that allows you to remember which
    # programs have already been generated.

    def synth_method_1(self,) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 1).

        **TODO: write a description of your approach in this method.**
        """
        # TODO : complete this method
        res = {}
        # hole variable might be easier - then I can take the name
        for hole in self.ast.holes: # key is the variable and I want the name so it is easier to check paddle type
            expr_list = self.hole_dict[hole.var.name]
            expr = expr_list.pop(0)
            while not self.ast.is_pure_expression(expr):
                if self.ast.is_almost_pure_expression(expr):
                    # assumes that there is a state with the variables called int_i, etc.
                    if self.state == {} and len(self.state) < len(self.ast.holes):
                        expr_list.append(expr)
                    else:
                        s = Solver()
                        vars = list(expr.uses())
                        for var in self.ast.inputs:
                            if var not in vars:
                                vars.append(var)
                        varDict = verifier.create_var_dict(vars)

                        state_copy = self.state.copy()
                        # set almost pure expr to hole key
                        state_copy[hole.var.name] = expr
                        # Pass in dictionary of valid hole completions to evaluator
                        evaluator = Evaluator(state_copy)
                        # Generate assertion expression with valid hole completions substituted into hole defns
                        final_constraint_expr = evaluator.evaluate(self.ast)
                        clause = verifier.validator(varDict, final_constraint_expr)
                        inputVars = [varDict[var.name] for var in self.ast.inputs]
                        s.add(ForAll(inputVars, clause))
                        cond = s.check()
                        if cond == sat:
                            model = s.model()
                            # print(clause)
                            # print(s.check())
                            # print(s.model())
                            # TODO: this method replaces int_i with values from SAT solver model
                            expr = self.substitute(expr, model)
                            res[hole.var.name] = expr
                            break
                        expr = expr_list.pop(0)

                else:
                    # TODO: Requires expand expression
                    expr_list.extend(self.expand(hole, expr))
                    expr = expr_list.pop(0)
                    self.intCoutner = 0
            res[hole.var.name] = expr

        self.state = res
        return res

    def synth_method_2(self,) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 2).

        **TODO: write a description of your approach in this method.**
        """
        # TODO : complete this method
        raise Exception("Synth.Synthesizer.synth_method_2 is not implemented.")

    def synth_method_3(self,) -> Mapping[str, Expression]:
        """
        Returns a map from each hole id in the program `self.ast`
        to an expression (method 3).

        **TODO: write a description of your approach in this method.**
        """
        # TODO : complete this method
        raise Exception("Synth.synth_method_3 is not implemented.")
