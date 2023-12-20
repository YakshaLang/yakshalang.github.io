---
title: YakshaLisp and macros in Yaksha
author: Bhathiya Perera
layout: '../../layouts/TutorialLayout.astro'
---

`YakshaLisp` is the builtin macro processing system in the `Yaksha` language. In this tutorial we will go through `YakshaLisp` basics, some builtin functions and how you can use those.


## What makes YakshaLisp different from Yaksha

From the point of view of `Yaksha` language. `YakshaLisp` exist only during the compilation phase. Most of the programming languages consist of a DSL that acts as the meta programming layer. Think `YakshaLisp` as such DSL that exist to generate code.


## YakshaLisp basics

Before we take a look at how to write macros, we need to understand how YakshaLisp works.

You can execute YakshaLisp REPL by running `yaksha lisp` command. (This is a very simple REPL)

### Defining and setting a value

```scheme
(def a 1)  # <--- a is initialized to 1
(setq a 2) # <--- a value is changed to 2 
           # a is now set to 2
```

Shortcut.

```scheme
(= a 1)   # <--- def or setq
```

### S-expressions

```scheme
(def a 1)  # <--- this is an S-expression
```

### Q-expressions

```scheme
(def a (quote 1 2 3))
(def b {1 2 3})
(== a b) # <---- truthy
```

Q-expressions are inspired by the make your own lisp. (However, we also do have special forms). 

#### Difference between `list`, `quote` and `Q-Expressions`

```scheme
(def a (list 1 2 3)) # <--- a is created with `list`
(def b {1 2 3})      # <--- b created with `{}`
(def c (quote 1 2 3))# <--- c is created with `quote`
(== a b)             # <--- ==/!= type mismatch
(== b c)             # <--- truthy
(== (map eval b) a)  # <--- truthy
```

Individual elements in Q-expressions are not evaluated. However, if you want to evaluate them, you can use `eval` function with `map` function.

`(quote ...)` is same as `{...}`. However, `quote` is a function with a special form.

```yaksha
(map eval {(+ 0 1) (+ 1 1) (+ 1 2)}) # <---- {1 2 3}
```

### Builtin values

* `nil` - falsey value, it is same as `{}`
* `true` - truthy value, it is same as `1`
* `false` - falsey value, it is same as `0`
* `newline` - newline character, either `"\r\n"` or `"\n"`

### Simple builtins

```scheme
(def a (+ 1 2)) # <----- a is 3
(def b (- 2 1)) # <----- b is 1
(def c (* 2 3)) # <----- c is 6
(def d (/ 6 2)) # <----- d is 3
```

### Comparison builtins

```scheme
(def a (== 1 1)) # <----- a is true
(def b (!= 1 1)) # <----- b is false
(def c (< 1 2))  # <----- c is true
(def d (> 1 2))  # <----- d is false
(def e (<= 1 2)) # <----- e is true
(def f (>= 1 2)) # <----- f is false
```

### Logical builtins

```scheme
(def a (and true true))  # <----- a is true
(def b (and true false)) # <----- b is false
(def c (or true false))  # <----- c is true
(def d (or false false)) # <----- d is false
(def e (not true))       # <----- e is false
(def f (not false))      # <----- f is true
```

### If builtin

```scheme
(def a (if true 1 2)) # <----- a is 1
(def b (if false 1 2))# <----- b is 2
(def c (if true 1))   # <----- c is 1
(def d (if false 1))  # <----- d is nil (same as {})
```

## DSL macros

Currently YakshaLisp can be used to write DSL macros. In this tutorial we will go through how to write a simple DSL macro.

```yaksha
macros! {
    # Get an integer_decimal token 7
    (defun ymacro_get () (list (ykt_integer_decimal 7)))
    # create a DSL macro named get! that executes above (defun ymacro_get...) function
    (yk_register {dsl get ymacro_get})
}

def main() -> int:
    e1 = array("int", 4, 5, 6, get!{})
    for i: int in e1:
        println(i)
    del e1
    return 0

```

This should print 4, 5, 6, 7 in individual lines. `yk_register` is a builtin function that registers a DSL macro. `dsl` is the type of the macro. `get` is the name of the macro. `ymacro_get` is the `YakshaLisp` function that executes when the macro is called.