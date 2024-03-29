---
title: Getting started
author: Bhathiya Perera
layout: '../../layouts/TutorialLayout.astro'
---

## Setting things up

### Downloading

* Head to [releases](https://github.com/YakshaLang/Yaksha/releases)
* Pick an archive format you like `.7z` or `.zip` (both has same content and `.7z` is almost always likely to be smaller in size)
* Since this is a new language we recommend you always download latest version. Please expect things to not work.

### Installing

* After download is completed you can extract the archive. Here are few ways:
  - Windows: use [7zip application](https://www.7-zip.org/)
  - GNU/Linux: use `7za` or `unzip` depending on archive format.
* Now you can add `bin` directory to PATH.
* If you are in GNU/Linux ensure that binaries in the `bin` directory have `+x` (executable) permission assigned. `chmod +x *`

### Basics of Yaksha Programming Language

#### Hello World

Steps:

First save below code to a file named "hello.yaka"

```yaksha
def main() -> int:
    println("Hello World!")
    return 0
```

In Yaksha we use `.yaka` extension for source files. Also, we use `->` to denote return type of a function.
Additionally entry point of a program is `main` function. Main function must always return an `int` value. In this case we return `0` to indicate that program has exited successfully. Additionally we use `println` builtin function to print a line to standard output.

Now you can compile it using `yaksha` command.

```bash
yaksha build -R hello.yaka
```

Internally `yaksha build` command will invoke `carpntr` binary included in the distribution. `carpntr` is the builder tool for Yaksha. It will compile the source file and generate a binary named `hello` in the current directory. Additionally it will generate a `hello.c` file which is the `C` code generated by the compiler. You can inspect this file to see how the compiler works. `-R` option for `carpntr` (or `yaksha build`) will execute the binary after compilation.

`carpntr` (or `yaksha build`) has many options. You can see them by running `yaksha build --help` or `carpntr --help`. Under the hood `carpntr` uses bundled `zig` compiler (with `zig cc`) and compile `c` code to a binary.

#### Comments

Yaksha programming language use `#` as an indicator for starting a comment.

```yaksha
# This is a comment
def main() -> int:
    a = "Hello # This is not a comment"
    println(a)
    # We can also omit return here
    0
```

#### Data types

Yaksha has many data types. Here are few of them:

- `int`: 32 bit signed integer (Examples: `1`, `100i32`)
- `float`: 32 bit floating point number (Examples: `1.0f`, `100.0f`)
- `bool`: Boolean value (Examples: `True`, `False`)
- `str`: partially memory managed string type. (You need to cleanup if you assign to a struct/class or into an array) (Examples: `"Hello World!"`, `"""Hello World!"""`)
- `sr`: a reference to a string.
- `None`: represents `NULL` value or `void`

You can find more data types and how to use them in the documentation. Since this is a tutorial we will not cover them here.

About `str`:

`str` is a partially memory managed string type. This means that if you just use `str` without assigning it to `struct/class/arrays` or any other data structures you don't need to worry about memory management. However, if you do, you need to cleanup. `str` implementation uses lot of copying and deletions. This is not the most efficient way to do things. However, it is the easiest way to do things. 

About `None`:

`None` compiles to either `NULL` or `void` depending on the context. You can use `None` to indicate that a function does not `return` anything. You can also compare heap structures with `None` to check if they are `NULL`.

#### Builtin functions

Out of the box Yaksha provides few builtin functions. Builtin functions compile to various things, therefore they cannot be referenced to create `Function[...]` variables. 

Here are few of them:

- `println`: prints a line to standard output
- `print`: prints to standard output (no line ending)

#### Variables

You can create a variable by simply using a let statement.
Statements such as `a = 1` can be either a let statement or an assignment.

```yaksha
def main() -> int:
    a = 1      # let
    b: int = 2 # let
    a += 2
    a += b
    b = a      # assignment
    println(b)
    return 0
```

When creating a variable, an identifier should be on the left hand side.

```yaksha
a = 10
```

This make above statement valid. 

```yaksha
10 = 20
```

However, a statement such as above is invalid.

You will get an error message like `test_file.yaka:2:8 at "=" --> Invalid assignment target!` 

Following will not even parse

```yaksha
10: int = 20
```

This will generate an error such as `test_file.yaka:2:7 at ":" --> Expect new line after value for expression.`

Ambiguity in assignment vs let.

Parser does not know if `a = 10` is an assignment or a let statement. So it is up to the later steps of the compiler to determine if `a` is already defined or not. And based on the outcome, type of `a` is inferred and can be promoted to a let statement. However, unlike languages such as `Python` type of `a` cannot be changed later on. Once defined it should remain same type.

#### Statements

Yaksha support various statements such as loops (`for` and `while`), `if` statements, `break`, `continue`, `return`, `defer`, `del`, `def`, `pass`, `import` and `class` (or `struct`) statements.

See below for a sample usage of a while loop.

```yaksha
def main() -> int:
    while True:
        println("loop")
        break
    return 0
```

In above example we are using a `def` statement to create our `main` function. Which will be the entry point of any Yaksha program. `while` statement will be executed once printing the world `loop` in your terminal emulator / console. Program will `return 0` to indicate success.

#### Defining a function

```yaksha
def add(a: int, b: int) -> int: a + b
```

Above is an example of how we can define a function called `add` which can add two integers `a` and `b` and return `a + b`. In above function we have omitted `return` statement as that can be inferred by the compiler.

```python
def function_name(p1: dt1, p2: dt2, ...) -> return_datatype:
    ... 
    # body of the function
    ...
```

Standard functions look like above. `p1, p2` are parameters and `dt1, dt2` are associated data types.

There are two possible ways of passing arguments to a function. `by value` and `by reference`. Primitive data types (and `str`) are always passed `by value`. (By value means a new copy is created when invoking a function). Additionally `Tuple` data types and `struct`s are also passed `by value`. Objects created from `class`es are passed `by reference`. Additionally `Ptr`, `Array` and `AnyPtr` will be passed by reference as well. `sr` works same as a reference.

Now let's try and use our `add` function.

```yaksha
def add(a: int, b: int) -> a + b

def main() -> int:
    println(add(1, 2))
    return 0
```

#### Defining a struct

```yaksha
struct A:
    a: int

def main() -> int:
    item: A
    item.a = 0
    return 0
```

When a structure is created, values are initialised to be of garbage values. You can also assign values to this immediately. 

#### Scopes

Yaksha scopes are created with blocks. Variables created inside the scopes are not leaked outside. If you need any variable to be accessed outside, you need to ensure that the variable is first created outside.

```yaksha
if a == 5:
    b: int = 5
else:
    b: int = 10
println(b)    # ❌ <----- you cannot access b
```

Correct usage would be

```yaksha
b: int = 10
if a == 5:
    b = 5
println(b)
```

This way you can access `b` afterwards. 

#### Importing libraries

Yaksha comes with builtin libraries. Standard libraries can be accessed under `libs` namespace.  Additionally`raylib` for raylib and `w4` for wasm4 library.

```yaksha
import libs.console

def factorial(x: int) -> int:
    if x <= 0:
        return 1
    return x * factorial(x - 1)

def main() -> int:
    a = 0
    while a < 10:
        console.cyan("factorial")
        console.red("(")
        print(a)
        console.red(") = ")
        println(factorial(a))
        a = a + 1
    return 0

```

Above code sample calculates factorial in a recursive manner. `libs.console` allow us to access cross platform `console/terminal emulator` functionality. You can use functions such as `console.cyan(string)` to print coloured text.

##### How import works

`import libs.c` -> this will add `c` as a globally accessible namespace for content of `libs.c`. 

If you use something like `import libs.c as clib` then globally accessible namespace would be `clib`

Accessing as `libs.console.cyan` is invalid. You should use `your_alias_here.cyan` or `console.cyan`


