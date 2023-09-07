# YAMA 0005 - DSL macros for Yaksha

- Author(s): Bhathiya Perera
- Status   : In Progress

<!-- different languages for code blocks are used to get maximum syntax matching for free, please ignore -->

## Problem

Macros allow for compile time code generation. Yaksha already supports multiple ways of exposing and defining `C` macros. However, `C` macros are not easy to use. Other than for exposing things written in `C` one should avoid using `C` macros in Yaksha (`@nativexxx`).

## Proposal

YakshaLisp would be a language of it's own. Capable of executing at compile time of Yaksha (and also as a command line interpreter).

### WHY?

* Lisp is a great language for meta programming.
* Lisp can be used to manipulate lists. (List processing 😄)
* Token list to token list transformation is a good fit for lisp.
* Simplest form of syntax to learn.
* Yak-shaving is fun. (Did you see what I did there? 😄)
* Feels nicer and user friendly than `C` macros and `@nativexxx` in Yaksha.

### Command line interpreter

Use YakshaLisp as it's own programming language.

* `yaksha lisp` - Run YakshaLisp interpreter REPL (Just YakshaLisp code, no macros!{} required) 
* `yaksha lisp <file>` - Execute just YakshaLisp code. (Don't use macros!{} here)

### DSL macros

DSL macros get a list of tokens and outputs a list of tokens. This allows for more complex logic to be written in YakshaLisp macros.

Any DSL macro inside `{}` will be also expanded. 

Most nested macro invocation will be expanded first. These macros can call other macros as you call a function and support iteration and recursion. These macros will only be expanded once.

#### Builtin functionality of YakshaLisp

* Printing to console ✅
* Reading from console ✅ - Requires `enable_print` to be called, before calling `print` and `println`, console output of `yaksha compile` maybe altered using this. Therefore, this is disabled by default.
* Reading/writing text files ✅
* Strings, decimal Integers ✅
* List manipulation ✅
* Maps (string -> value only) ✅
* Map literals, and manipulation ✅
* Working with Yaksha tokens ✅
* Iteration ✅
* Conditions - if, cond ✅
* Few functional built ins - map, reduce, range ✅
* Q-Expressions inspired by [Build Your Own Lisp](http://www.buildyourownlisp.com/) lisp dialect. ✅ (This is somewhat similar to `'(+ 1 2 3)`)
* Eval and parse ✅
* Token generation for Yaksha ✅
* Executing commands ❌ (not started, planned) - Will be disabled by default.
* Macros for YakshaLisp ✅
* Imports ✅
* Hygienic macros - gensym ✅ / metagensym 🟡
* Garbage collection ✅

## Item 1 - Initial DSL macro support ✅

```python
# ╔═╗┌─┐┌┬┐┌─┐┬┬  ┌─┐  ╔╦╗┬┌┬┐┌─┐
# ║  │ ││││├─┘││  ├┤    ║ ││││├┤
# ╚═╝└─┘┴ ┴┴  ┴┴─┘└─┘   ╩ ┴┴ ┴└─┘
# ╔═╗┬┌─┐┌─┐  ╔╗ ┬ ┬┌─┐┌─┐
# ╠╣ │┌─┘┌─┘  ╠╩╗│ │┌─┘┌─┘
# ╚  ┴└─┘└─┘  ╚═╝└─┘└─┘└─┘
macros!{
    (defun to_fb (n) (+ (if (== n 1) "" " ") (cond
        ((== 0 (modulo n 15)) "FizzBuzz")
        ((== 0 (modulo n 3)) "Fizz")
        ((== 0 (modulo n 5)) "Buzz")
        (true (to_string n))
        )))
    (defun fizzbuzz () (list (yk_create_token YK_TOKEN_STRING (reduce + (map to_fb (range 1 101))))))
    (yk_register {dsl fizzbuzz fizzbuzz})
}

def main() -> int:
    println(fizzbuzz!{})
    return 0
```

## Item 2 - Hygienic DSL macros using `gensym` ✅ and `metagensym` 🟡

* `gensym` - This is not a function unlike `metagensym`, simply return a name such as `$a` (any valid Yaksha IDENTIFIER prefixed with `$`) and it will be replaced with a unique symbol. ✅
* `metagensym` - Generates a unique symbol to be used in YakshaLisp code.

## Item 3 - Macros for YakshaLisp via `metamacro` ✅

Did you ever think that your meta programming might benefit from meta-meta programming?

Macros get all parameters non-evaluated. The output from macro will be evaluated (in calling scope) and needs to be a list of expressions.
Other than that it is similar to a `defun`. Metamacros are executed similarly to functions and can also call other `metamacros` or `defuns`.

If you consider just YakshaLisp as it's own language, this allows you to meta program in YakshaLisp during runtime of YakshaLisp.

* `(is_callable my_meta)` --> `false`, this is `true` only for `builtins`, `def`, `lambda`.

```python
macros!{
    (metamacro twice (x) (+ (list x) (list x)))
    # since x is an expression (non evaluated), it can be converted to {}
    # by simply calling list. 
    # x ----> (= value (+ value 1))) # as an expr
    # (list x) ---> {(= value (+ value 1))}
    # (+ (list x) (list x)) ---> {
    #    (= value (+ value 1)) (= value (+ value 1))
    #    }
    # now evaluated in calling scope
    # (eval {...}) --> increase value by 1 twice
    (= value 1)
    (twice (= value (+ value 1)))
    # This would set success
    (if (== value 3) (= success 1))
}

def main() -> int:
    return 0
```

```scheme
(twice (println "Hello")) ----> (eval {(println "Hello") (println "Hello")})
```

## Item 4 - Import macros from other files ✅

```python
import libs.macro as m
macros!{
    (enable_print)
    (m.twice (println "Hello"))
}

def main() -> int:
    return 0
```

## Item 5 - Execute commands (not started, planned) ❌

Will be disabled by default. Can be enabled by a setting a flag in `yaksha.toml` or setting an environment variable `YAKSHA_SERIOUSLY_ENABLE_SHELL_EXEC` to `True`.

```python
import libs.macro.shell as m

def main() -> int:
    m.execute!{"echo Hello World"}
    println(m.readout!{"echo Hello World", "Failed"})
    return 0
```

## Item 6 - Tracing macro expansion and debugging (not started, planned) ❌

Allow Yaksha compiler to output macro expansion steps. This will be useful for debugging macros.

Design TBD.

Some tracing features are supported by YakshaLisp if DEBUG is enabled during compilation of Yaksha, but this does not look nice and only useful for Yaksha/YakshaLisp language development. Perhaps these DEBUG features can be made to output more readable output and enable/disable with a flag instead of `#ifdef DEBUG`.

## Item 7 - Garbage collection ✅

YakshaLisp will have a simple mark and sweep garbage collector. This will be used to manage memory allocated by YakshaLisp.