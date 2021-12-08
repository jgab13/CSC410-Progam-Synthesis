import unittest
from lang.ast import *
from lang.symb_eval import EvaluationUndefinedHoleError, Evaluator
from lang.paddle import parse
from pathlib import Path
from random import randint
import os
from verification.verifier import is_valid


class TestStudent(unittest.TestCase):

    def test_sanity_student(self):
        self.assertTrue(True)
    
    # Symbolic Evaluation 
    def test_eval_mult_to_add(self):
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
        # and the operator should be &&
        self.assertEqual(prog_res.operator, BinaryOperator.EQUALS)
        # there is only 2 variable in prog_res
        self.assertEqual(len(prog_res.uses()), 2)
        # Evaluate the expression
        for i in range(5):
            model = {
                "x": IntConst(randint(-55, 55)),
                "y": IntConst(randint(-55, 55))
            }
            lhs = empty.evaluate_expr(model, prog_res.left_operand)
            rhs = empty.evaluate_expr(model, prog_res.right_operand)

            self.assertTrue(eval(str(lhs)) == eval(str(rhs)))

    def test_eval_sum(self):
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
        # Evaluate the expression
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
        z = VarExpr(prog.inputs[2])
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
        # and the operator should be &&
        self.assertEqual(prog_res.operator, UnaryOperator.NOT)

        # there is only 2 variables in prog_res
        self.assertEqual(len(prog_res.uses()), 2)
        # Evaluate the expression
        model = {"y": IntConst(3), "z": IntConst(2)}
        op = empty.evaluate_expr(model, prog_res.operand)
        self.assertTrue(eval(str(op)))
   
    # Verifying Programs Test
    def test_verif_simple_false(self):
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
        
    def test_verif_complex2(self):
        filename = '%s/examples/student/verif/complex_2.paddle' % Path(
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
