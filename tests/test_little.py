import pytest
from littlelang import Little


@pytest.fixture
def base_little() -> Little:
    return Little()


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


def test_map(base_little: Little):
    assert base_little.exec('{:one 1 3 "hello" "five" 3.4}') == {
        "one": 1,
        3: "hello",
        "five": 3.4,
    }
