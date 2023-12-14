# YakshaLisp and macros in Yaksha

- Author(s): Bhathiya Perera

`YakshaLisp` is the builtin macro processing system in the `Yaksha` language. In this tutorial we will go through `YakshaLisp` basics, some builtin functions and how you can use those.


## What makes YakshaLisp different from Yaksha

From the point of view of `Yaksha` language. `YakshaLisp` exist only during the compilation phase. Most of the programming languages consist of a DSL that acts as the meta programming layer. Think `YakshaLisp` as such DSL that exist to generate code.


## YakshaLisp

Before we take a look at how to write macros, we need to understand how YakshaLisp works.

You can execute YakshaLisp REPL by running `yaksha lisp` command. (This is a very simple REPL)

### Defining and setting a value

```yaksha
(def a 1)  # <--- a is initialized to 1
(setq a 2) # <--- a value is changed to 2 
           # a is now set to 2
```

Shortcut.

```yaksha
(= a 1)   # <--- def or setq
```

### S-expressions

```yaksha
(def a 1)  # <--- this is an S-expression
```

### Q-expressions

```yaksha
(def a (quote 1 2 3))
(def b {1 2 3})
(== a b) # <---- truthy
```

Q-expressions are inspired by the make your own lisp. (However, we also do have special forms). 

#### Difference between `list`, `quote` and `Q-Expressions`

```yaksha
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
