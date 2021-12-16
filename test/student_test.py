import unittest
from lang.ast import *
from lang.symb_eval import EvaluationUndefinedHoleError, Evaluator
from lang.paddle import parse
from pathlib import Path
from random import randint
import os
from synthesis.synth import Synthesizer
from verification.verifier import is_valid

ITERATIONS_LIMIT = 100000


# function for synth test
def main_loop_synth_check(method_num, filename, iter_limit=ITERATIONS_LIMIT):
    # Parse the input file into an AST
    ast = parse(filename)
    # Initialize a Synthesizer with it
    synt = Synthesizer(ast)
    # Iterate until a solution is found or iteration limit is reached
    iteration = 0
    while iteration < iter_limit:
        iteration += 1
        # At each call of the methods of the synthesizer a new
        # hole completion should be returned.
        if method_num == 3:
            hole_completions = synt.synth_method_3()
        elif method_num == 2:
            hole_completions = synt.synth_method_2()
        else:
            hole_completions = synt.synth_method_1()
        # Evaluate the program with these completions
        evaluator = Evaluator(hole_completions)
        final_constraint_expr = evaluator.evaluate(ast)
        # Verify the program, if it is valid it is a solution!
        if is_valid(final_constraint_expr):
            return True
        # Otherwise the loop continues.
    return False


def testFile(testcase, filename):
    testcase.assertTrue(os.path.exists(filename))
    if not os.path.exists(filename):
        raise Exception(
            "TestSynth is looking for %s, which was in the starter code.\
                 Make sure file exists." % filename)
    r1 = main_loop_synth_check(1, filename)
    testcase.assertTrue(r1, msg="Method 1 failed to synthesize a solution for %s." % filename)
    r2 = main_loop_synth_check(2, filename)
    testcase.assertTrue(r2, msg="Method 2 failed to synthesize a solution for %s." % filename)
    r3 = main_loop_synth_check(3, filename)
    testcase.assertTrue(r3, msg="Method 3 failed to synthesize a solution for %s." % filename)


class TestStudent(unittest.TestCase):

    def test_sanity_student(self):
        """
        Sanity Check for test student
        """
        self.assertTrue(True)

    # Symbolic Evaluation
    def test_eval_mult_to_add(self):
        """
        test to check multiple addition for eval
        """
        filename = '%s/examples/student/eval/student_mult_to_add_true.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        prog: Program = parse(filename)
        empty = Evaluator({})
        prog_res = empty.evaluate(prog)
        # The result should be an expression
        self.assertIsInstance(prog_res, Expression)
        # In this particular case, the expression should be a binary expression
        self.assertIsInstance(prog_res, BinaryExpr)
        # and the operator should be =
        self.assertEqual(prog_res.operator, BinaryOperator.EQUALS)
        # there is only 2 variable in prog_res
        self.assertEqual(len(prog_res.uses()), 2)
        # Evaluate the expression 5 times with random ints
        for i in range(5):
            model = {
                "x": IntConst(randint(-55, 55)),
                "y": IntConst(randint(-55, 55))
            }
            lhs = empty.evaluate_expr(model, prog_res.left_operand)
            rhs = empty.evaluate_expr(model, prog_res.right_operand)

            self.assertTrue(eval(str(lhs)) == eval(str(rhs)))

    def test_eval_sum(self):
        """
        test to check sum of variables for eval
        """
        filename = '%s/examples/student/eval/student_sum.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        prog: Program = parse(filename)
        empty = Evaluator({})
        prog_res = empty.evaluate(prog)
        # The result should be an expression
        self.assertIsInstance(prog_res, Expression)
        # In this particular case, the expression should be a binary expression
        self.assertIsInstance(prog_res, BinaryExpr)
        # and the operator should be &&
        self.assertEqual(prog_res.operator, BinaryOperator.EQUALS)
        # there is only 3 variables in prog_res
        self.assertEqual(len(prog_res.uses()), 3)
        # Evaluate the expression 5 times with random ints
        for i in range(5):
            model = {
                "x": IntConst(randint(-100, 100)),
                "y": IntConst(randint(-100, 100)),
                "z": IntConst(randint(-100, 100))
            }
            lhs = empty.evaluate_expr(model, prog_res.left_operand)
            rhs = empty.evaluate_expr(model, prog_res.right_operand)

            self.assertTrue(eval(str(lhs)) == eval(str(rhs)))

        model = {"x": IntConst(1), "y": IntConst(
            2), "z": IntConst(3)}
        lhs = empty.evaluate_expr(model, prog_res.left_operand)
        rhs = empty.evaluate_expr(model, prog_res.right_operand)
        self.assertTrue(eval(str(lhs)) == eval(str(rhs)))

    def test_eval_max(self):
        """
        test to check maximum of two variables added by another variable for eval
        """
        filename = '%s/examples/student/eval/student_max.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        prog: Program = parse(filename)
        # Now let's give definitions
        self.assertEqual(len(prog.inputs), 3,
                         msg="In %s, we expected exactly 3 inputs." % filename)
        x = VarExpr(prog.inputs[0])
        y = VarExpr(prog.inputs[1])
        e1 = BinaryExpr(BinaryOperator.GREATER, x, y)
        e2 = Ite(e1, x, y)
        defined = Evaluator({"hmax": e2})
        prog_res = defined.evaluate(prog)
        # The result should be an expression
        self.assertIsInstance(prog_res, Expression)
        # In this particular case, the expression should be a binary expression
        self.assertIsInstance(prog_res, BinaryExpr)
        # and the operator should be &&
        self.assertEqual(prog_res.operator, BinaryOperator.AND)
        # there is only two variables in prog_res
        self.assertEqual(len(prog_res.uses()), 3)

    def test_eval_min(self):
        """
        test to check minimum of two variables added by another variable
        """
        filename = '%s/examples/student/eval/student_min.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        prog: Program = parse(filename)
        # Now let's give definitions
        self.assertEqual(len(prog.inputs), 3,
                         msg="In %s, we expected exactly 3 inputs." % filename)
        x = VarExpr(prog.inputs[0])
        y = VarExpr(prog.inputs[1])
        z = VarExpr(prog.inputs[2])
        e1 = BinaryExpr(BinaryOperator.LESSTHAN, x, y)
        e2 = Ite(e1, x, y)
        defined = Evaluator({"hmin": e2})
        prog_res = defined.evaluate(prog)
        # The result should be an expression
        self.assertIsInstance(prog_res, Expression)
        # In this particular case, the expression should be a binary expression
        self.assertIsInstance(prog_res, BinaryExpr)
        # and the operator should be &&
        self.assertEqual(prog_res.operator, BinaryOperator.AND)
        # there is only two variables in prog_res
        self.assertEqual(len(prog_res.uses()), 3)

    def test_eval_bool(self):
        """
        test to check boolean variables for eval
        """
        filename = '%s/examples/student/eval/student_bool.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        prog: Program = parse(filename)
        empty = Evaluator({})
        prog_res = empty.evaluate(prog)
        # The result should be an expression
        self.assertIsInstance(prog_res, Expression)
        # In this particular case, the expression should be a binary expression
        self.assertIsInstance(prog_res, BinaryExpr)
        # and the operator should be &&
        self.assertEqual(prog_res.operator, BinaryOperator.AND)
        # there is only 3 variables in prog_res
        self.assertEqual(len(prog_res.uses()), 3)
        # Evaluate the expression
        model = {"x": IntConst(1), "y": IntConst(
            2), "b": BoolConst(True)}
        lhs = empty.evaluate_expr(model, prog_res.left_operand)
        rhs = empty.evaluate_expr(model, prog_res.right_operand)
        self.assertFalse(eval(str(lhs)) == eval(str(rhs)))

    def test_eval_unary(self):
        """
        test to check unary operators for eval
        """
        filename = '%s/examples/student/eval/student_unary.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        prog: Program = parse(filename)
        empty = Evaluator({})
        prog_res = empty.evaluate(prog)
        # The result should be an expression
        self.assertIsInstance(prog_res, Expression)
        # In this particular case, the expression should be a binary expression
        self.assertIsInstance(prog_res, UnaryExpr)
        # and the operator should be NOT
        self.assertEqual(prog_res.operator, UnaryOperator.NOT)

        # there is only 2 variables in prog_res
        self.assertEqual(len(prog_res.uses()), 2)
        # Evaluate the expression
        model = {"y": IntConst(3), "z": IntConst(2)}
        op = empty.evaluate_expr(model, prog_res.operand)
        self.assertTrue(eval(str(op)))

    # Verifying Programs Test
    def test_verif_simple_false(self):
        """
        Test a simple false case of booleans for verification
        """
        filename = '%s/examples/student/verif/simple_false.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        try:
            ast = parse(filename)
        except:
            self.assertFalse(
                True, "Exception was raised when parsing %s" % filename)
        # Evaluate from empty
        try:
            ev = Evaluator({})
            final_constraint_expr = ev.evaluate(ast)
        except:
            self.assertFalse(
                True, "Exception was raised when parsing %s" % filename)
        # Verify
        self.assertFalse(is_valid(final_constraint_expr))

    def test_verif_simple_true(self):
        """
        Test a simple true case of booleans for verification
        """
        filename = '%s/examples/student/verif/simple_true.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        try:
            ast = parse(filename)
        except:
            self.assertFalse(
                True, "Exception was raised when parsing %s" % filename)
        # Evaluate from empty
        try:
            ev = Evaluator({})
            final_constraint_expr = ev.evaluate(ast)
        except:
            self.assertFalse(
                True, "Exception was raised when parsing %s" % filename)
        # Verify
        self.assertTrue(is_valid(final_constraint_expr))

    def test_verif_mult_to_add(self):
        """
        test to check multiple addition for verification
        """
        filename = '%s/examples/student/verif/student_mult_to_add_true.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        try:
            ast = parse(filename)
        except:
            self.assertFalse(
                True, "Exception was raised when parsing %s" % filename)
        # Evaluate from empty
        try:
            ev = Evaluator({})
            final_constraint_expr = ev.evaluate(ast)
        except:
            self.assertFalse(
                True, "Exception was raised when parsing %s" % filename)
        # Verify
        try:
            self.assertTrue(is_valid(final_constraint_expr))
        except:
            self.assertFalse(
                True, "Exception was raised when verifying %s" % filename)

    def test_verif_ite(self):
        """
        test to check if then else for verification
        """
        filename = '%s/examples/student/verif/ite.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        try:
            ast = parse(filename)
        except:
            self.assertFalse(
                True, "Exception was raised when parsing %s" % filename)
        # Evaluate from empty
        try:
            ev = Evaluator({})
            final_constraint_expr = ev.evaluate(ast)
        except:
            self.assertFalse(
                True, "Exception was raised when parsing %s" % filename)
        # Verify

        self.assertTrue(is_valid(final_constraint_expr))

    def test_verif_complex1(self):
        """
        test to check a rather complicated case for verification
        """
        filename = '%s/examples/student/verif/complex_1.paddle' % Path(
            __file__).parent.parent.absolute()
        if not os.path.exists(filename):
            raise Exception(
                "TestEval is looking for %s. Make sure file exists." % filename)

        try:
            ast = parse(filename)
        except:
            self.assertFalse(
                True, "Exception was raised when parsing %s" % filename)
        # Evaluate from empty
        try:
            ev = Evaluator({})
            final_constraint_expr = ev.evaluate(ast)
        except:
            self.assertFalse(
                True, "Exception was raised when parsing %s" % filename)
        # Verify

        self.assertTrue(is_valid(final_constraint_expr))

    # Enumerating Programs Test
    def test_synth_sum(self):
        """
        test to check summation to multiplication for synth
        """
        filename = '%s/examples/student/synth/sum.paddle' % (
            Path(__file__).parent.parent.absolute())
        testFile(self, filename)

    def test_synth_division(self):
        """
        test to check division for synth
        """
        filename = '%s/examples/student/synth/div.paddle' % (
            Path(__file__).parent.parent.absolute())
        testFile(self, filename)

    def test_synth_ite(self):
        """
        test to check if then else for synth
        """
        filename = '%s/examples/student/synth/ite.paddle' % (
            Path(__file__).parent.parent.absolute())
        testFile(self, filename)

    def test_no_sol(self):
        """
        test to check case where there is no solution for synth
        """
        filename = '%s/examples/student/synth/no_sol.paddle' % (
            Path(__file__).parent.parent.absolute())
        self.assertTrue(os.path.exists(filename))
        if not os.path.exists(filename):
            raise Exception(
                "TestSynth is looking for %s, which was in the starter code.\
                     Make sure file exists." % filename)
        r1 = main_loop_synth_check(1, filename, 1000)
        self.assertFalse(
            r1, msg="Method 1 failed to synthesize a solution for %s." % filename)
        r2 = main_loop_synth_check(2, filename, 1000)
        self.assertFalse(
            r2, msg="Method 2 failed to synthesize a solution for %s." % filename)
        r3 = main_loop_synth_check(3, filename, 1000)
        self.assertFalse(
            r3, msg="Method 3 failed to synthesize a solution for %s." % filename)

    def test_complex(self):
        """
        test to check a rather complex case for synth
        """
        filename = '%s/examples/student/synth/complex.paddle' % (
            Path(__file__).parent.parent.absolute())
        testFile(self, filename)
