import pytest
from littlelang import Little, LittleWithStd
from littlelang.little import Identifier, QuotedRuntime


@pytest.fixture
def base_little() -> Little:
    return Little()


@pytest.fixture
def std_little() -> Little:
    return LittleWithStd()


def test_integer(base_little: Little):
    assert base_little.exec("5") == 5
    assert base_little.exec(" 13455 ") == 13455


def test_float(base_little: Little):
    assert base_little.exec("5.3") == 5.3
    assert base_little.exec(" 13.455 ") == 13.455
    assert base_little.exec("0.34") == 0.34


def test_string(base_little: Little):
    assert base_little.exec('"Hello, world!"') == "Hello, world!"


def test_string_escapes(base_little: Little):
    assert base_little.exec('"\\n\\n\\t\\\\"') == "\n\n\t\\"


def test_symbol(base_little: Little):
    assert base_little.exec(":hello") == "hello"


def test_vector(base_little: Little):
    assert base_little.exec("[3 5 :hi 4.2]") == [3, 5, "hi", 4.2]


def test_none(base_little: Little):
    assert base_little.exec("None") is None


def test_true(base_little: Little):
    assert base_little.exec("True") is True


def test_false(base_little: Little):
    assert base_little.exec("False") is False


def test_map(base_little: Little):
    assert base_little.exec('{:one 1 3 "hello" "five" 3.4}') == {
        "one": 1,
        3: "hello",
        "five": 3.4,
    }


def test_nesting(base_little: Little):
    assert base_little.exec("{:one 1 :list [1 2 3] :dict {:one 1 :two 2}}") == {
        "one": 1,
        "list": [1, 2, 3],
        "dict": {"one": 1, "two": 2},
    }


def test_identifier(base_little: Little):
    base_little.env.define("x", 5)
    base_little.env.define("my_list", [3, 4, "hello"])
    assert base_little.exec("x") == 5
    assert base_little.exec("my_list") == [3, 4, "hello"]


def test_quoted(base_little: Little):
    q = base_little.exec("'a")
    assert isinstance(q, QuotedRuntime)
    assert isinstance(q.node, Identifier)


def test_expression(base_little: Little):
    base_little.env.define("+", lambda a, b: a + b)
    assert base_little.exec("(+ 1 2)") == 3
    assert base_little.exec("(+ 1 (+ 2 3))") == 6


def test_quoted_execution(base_little: Little):
    def scope(child: QuotedRuntime):
        env = child.env.new_scope()
        env.define("x", 1)
        return child.exec(env, child.node)

    base_little.env.define("+", lambda a, b: a + b)
    base_little.env.define("x", 5)
    base_little.env.define("scope", scope)
    assert base_little.exec("(+ x 1)") == 6
    assert base_little.exec("(scope '(+ x 1))") == 2
    assert base_little.exec("x") == 5


def test_map_and_list_get(std_little: Little):
    std_little.exec(
        """
(def :dict '{:a 2 :b 4 :c {:a 10}})
(def :a '(get dict :a))
(def :my_list '[9 10 11])
(def :list_val '(get my_list 2))
(def :get_in_test '(get-in dict [:c :a]))
                    """
    )

    assert std_little.env.get("a") == 2
    assert std_little.env.get("list_val") == 11
    assert std_little.env.get("get_in_test") == 10


def test_unmapped_items_example(std_little: Little):
    std_little.env.define(
        "receipt", {"items": [{"invoice_line_id": 5}, {"invoice_line_id": None}]}
    )
    assert (
        std_little.exec(
            """
(<
  0
  (len
    (filter
      (get receipt :items)
      (fn [:item] '(== None (get item :invoice_line_id))))))
                    """
        )
        is True
    )
