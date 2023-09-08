# Little Lang

A little language intended to be easy to implement, use, and understand.

Little has no keywords. Everything is a function. This design is intended to make it very easy to extend the language with functionality that the user needs.

Little is inspired by Lisp and Clojure. Expressions are surrounded by paranthesis where the first element is the function to be executed and subsequent elements are arguments.

## Syntax

* **Numbers**. Integers and floats are represented as numbers in code such as `35` and `2.96`.
* **Strings**. Strings are surrounded by double quotes and can include escape characters to represent newlines `\n`, tabs `\t`, quotes `\"`, and backslahes `\\`.
* **Symbols**. Symbols are a convenience to separate keys and variable definitions from strings. Symbols start or end with `:` such as `:key` or `key:`. Under the hood, they are just strings.
* **Expressions**. Expressions are surrounded by paranthesis. The first item within the paranthesis is the function to be executed and the other items, separated by whitespace, are the arguments. Example: `(+ 4 8)` will call the `+` function with `4` and `8` as arguments.
* **Quoted Code**. Quoted code allows code itself to be passed as an argument to functions, usually for delayed execution. You can quote code by putting `'` in front of any piece of code. Example: `(fn [:a :b] '(+ a b))`. The second part of the expression is a quoted piece of code which is sent to the `fn` function. The `fn` function is responsible for executing that code.
* **Lists/Vectors**. You can define a list/vector using brackets with items separated by whitespace. Example: `[3 4 5]`
* **Maps**. You can define maps/dictionaries using curly braces with keys and values separated by whitespace. For convenience and for purposes of interoperability with JSON, you can use colons after key names and you can use commas (considered whitespace) between entries. These examples are equivalent: `{:key "value" :key2 2 }`, `{key: "value" key2: 2}`, `{"key": "value", "key2": 2}`
* **Whitespace**. Spaces, tabs, newlines, and commas are all considered to be whitespace.
* **Identifiers**. Identifiers (variable names) are only used when you want to reference the value of an identifier. For example `x` will lookup the value of `x` from the environment. This includes functions, values, etc. Aside from alphanumeric characters, the following characters are valid in an identifier: `_-/*+-!?$><=;:`.

## Usage

```Python
from littlelang import LittleWithStd

little = LittleWithStd()

little.exec('(print "Hello, world!")')

```
