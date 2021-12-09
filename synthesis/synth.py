"""
CSC410 Final Project: Enumerative Synthesizer
by Victor Nicolet and Danya Lette

Fill in this file to complete the synthesis portion
of the assignment.
"""

from typing import Mapping
from z3 import *
from lang.ast import *
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
        self.state = []
        # The synthesizer is initialized with the program ast it needs
        # to synthesize hole completions for.
        self.ast = ast
        # TODO : hole_dict should call preprocessing function to populate hole_dict
        self.hole_dict = {}

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
        s = Solver()
        for key in self.hole_dict: # key is the variable and I want the name so it is easier to check paddle type
            expr_list = self.hole_dict[key]
            expr = expr_list.pop(0)
            while not self.ast.is_pure_expression(expr):
                if self.ast.is_almost_pure_expression(expr):
                    # assumes that there is a state with the variables called int_i, etc.
                    vars = list(expr.uses()) + self.state
                    varDict = verifier.create_var_dict(vars)
                    clause = verifier.validator(varDict, expr)
                    s.add(ForAll(vars, clause))
                    if s.check() == sat:
                        model = s.model()
                        # TODO: this method replaces int_i with values from SAT solver model
                        # expr = rebuild_expr(expr, model)
                        res[key.name] = expr
                        break

                else:
                    # TODO: Requires expand expression
                    # expr_list.extend(self.expand(expr))
                    expr = expr_list.pop(0)
                    # Not sure about this - how are we tracking
                    self.state = []
                    self.state_number = 0
            res[key.name] = expr
        return res
        # for hole in self.ast.hole_vars():
        #     print(self.ast.hole_can_use(hole))
        #
        # raise Exception("Synth.Synthesizer.synth_method_1 is not implemented.")

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
