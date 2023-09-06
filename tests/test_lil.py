from littlelang import parser
from littlelang.interpreter import PRELUDE, run, LilEnvironment


def easy_run(code):
    node = parser.Parser(code).parse()
    env = LilEnvironment()
    env.load(PRELUDE)

    return run(env, node)


def test_math1():
    assert easy_run("(+ 3 9)") == 12


def test_fn():
    assert (
        easy_run(
            """
            ((fn '(a b) '(+ a b)) 1 2)
            """
        )
        == 3
    )
    pass


# TODO: Fix parser which can infinite loop on unexpected characters like an extra )


def test_fn_in_python():
    f = easy_run("(fn '(a b) '(* a b))")
    assert f(2, 4) == 8


# ;; How do we feel about this syntax?
# (def :add (fn [:a :b] '(* a b)))

# (defn :add [:a :b] '(+ a b))


def test_literal_list():
    assert easy_run("[3 4 5]") == [3, 4, 5]
