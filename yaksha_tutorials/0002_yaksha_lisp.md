# YakshaLisp and macros in Yaksha

- Author(s): Bhathiya Perera

`YakshaLisp` is the builtin macro processing system in the `Yaksha` language. In this tutorial we will go through `YakshaLisp` basics, some builtin functions and how you can use those.


# What makes YakshaLisp different from Yaksha

From the point of view of `Yaksha` language. `YakshaLisp` exist only during the compilation phase. Most of the programming languages consist of a DSL that acts as the meta programming layer. Think `YakshaLisp` as such DSL that exist to generate code.


# YakshaLisp

Before we take a look at how to write macros, we need to understand how YakshaLisp works.

## Defining and setting a value

```yaksha
(def a 1)  # <--- a is initialized to 1
(setq a 2) # <--- a value is changed to 2 
           # a is now set to 2
```

Shortcut.

```yaksha
(= a 1)   # <--- def or setq
```

## Q-expressions

```yaksha
(def a (quote 1 2 3))
(def b {1 2 3})
(== a b) # <---- truthy
```

Q-expressions are inspired by the make your own lisp book's Q expressions. (However, we also do have special forms)

