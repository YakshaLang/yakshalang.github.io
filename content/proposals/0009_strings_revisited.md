# YAMA 0009 - Strings revisited

- Author(s): Bhathiya Perera
- Status   : Draft

Strings in programming languages are tough to design. You can make things simple by using it like a value type (Copying and deleting it). However, value like strings come at a cost as it does large number of alloc/dealloc resulting in fragmented memory. In WASM4 or embedded (potential future scenario) cases, this kind of alloc/dealloc is not acceptable.

This is an all or nothing proposal. Need to support all scenarios explained below. After this is completed, libs/runtime needs to rewritten to use new `sr` data type instead of `str` data type.

There is also an invisible string data type `literal` that is only available at compile time (`a: literal = "hi"` is invalid).
This type will be auto-magically converted to `sr`.

This is considered to avoid wasting time doing - runtime concatenation and runtime comparison of `literal`s.

**Breaking changes** - `a = "hello"` results in `a`'s data type to be `sr` instead of `str` and `sr` is now a builtin data type.

## Few areas to explore

### String reference

* String reference does not own the underlying heap allocated memory of a string. 
* No need to delete or duplicate. 
* But it is dangerous to store it in a structure as it might be invalid later on.

### Static storage strings

* Immutable static strings that lives in the static storage, lasts for the whole life time of the program.
* No need to de-allocate.
* Can store as a reference anywhere you like.
* Not copied when passing.

### String buffers

* Mutable string that owns memory.
* Not copied when passing to a function.
* Can use same underlying `yk__sds` as data structure.

### Semi managed value like strings

* What `str` represents in Yaksha.
* What is semi-managed? you need to manually de-allocate when a copy is added to a container.

### String literals

* This is a `"Hello World"` like string literal in Yaksha.
* This is currently automatically converted to `str`.
* We can consider string literals to be static storage strings.
* Length is known at compile time.

### Library/runtime use

* Runtime functionality will not need to de-allocate strings. Once we switch to use of `sr` data type.

## Implementation

### Underlying data structure

```c
struct yk__bstr { // Yaksha Base String
    union {
        yk__sds h;              // reference to a heap allocated string
        const char * s;         // reference to a statically allocated string
        char* c;                // reference to c.CStr that is heap allocated
    };
    size_t l;
    enum yk__bstr_type { yk__bstr_str, yk__bstr_static, yk__bstr_cstr } t;
};
```

### Yaksha

First we assume we have something like below defined, that takes the new data type `sr` as an argument.

`literal` is a hidden data type -- this cannot be used by end users directly. (Internally represented as `:s:`)

#### Legend

* ✅ - Completed
* N - No allocation should happen here (except in Windows due to need to convert to utf16).
* A - Alloc/Dealloc happens
* C - Compile time
* ! - Type-checking / compile error

```yaksha
def do_something(s: sr) -> int: # N
    print("Printing sr: ")      # N
    println(s)                  # N 
    return 0

def takes_str(s: str) -> int:   # A (arg is copied here and deleted in the function)
    print("Printing str: ")     # N
    println(s)                  # N
    return 0
```

#### Create `sr` data type ✅

* Have it compile to `struct yk__bstr`

#### Passing a `literal` to `sr` ✅

```yaksha
def main() -> int:
    do_something("Oi")           # N     
    return 0
```

#### Passing an `str` to `sr` and creating a `str` with `literal` ✅

```yaksha
def main() -> int:
    s: str = "Oi"                # A
    s2: str = "Ha"               # A
    do_something(s)              # N
    do_something(s2)             # N
    return 0
```

#### Passing a `literal`/`sr` to `str` ✅

```yaksha
def main() -> int:
    do_something("Oi")           # A
    a: sr = "ha"                 # A
    takes_str(a)                 # N
    takes_str("Oi oi")           # N
    return 0
```

#### Variable using `sr` as data type ✅

```yaksha
def main() -> int:
    oi = "Oi"                    # A
    do_something(oi)             # A
    takes_str("Oi oi")           # N
    return 0
```

#### Concatenation of `str`s --> `str` ✅

```yaksha
def main() -> int:
    s: str = "Oi"                # N
    s2: str = " Hello"           # N
    takes_str(s + s2)            # NN
    return 0
```

#### Concatenation of `literal`s --> `literal` ✅

```yaksha
def main() -> int:
    do_something("Oi" + " Hello there" + " Another") # NC
    takes_str("Oi" + " Hello there" + " Another")    # AC
    return 0
```

#### Concatenation of 2 or more `sr`s --> `str` ✅

```yaksha
def main() -> int:               # A  
    a: sr = "Hi"                 # A
    b: sr = " there"             # A
    do_something(a + b + a)      # NA
    takes_str(a + b)             # NN
    return 0
```

#### Concatenation of 2 or more of mixed `str`, `sr` and `literal`s --> `str` ✅

```yaksha
def main() -> int:
    a: str = "Hello"             # N
    b: sr = " World"             # A  
    c = a + b + " Hehe"          # NNN
    do_something(c)              # A  
    takes_str(c)                 # N
    d = "Ha " + b + " " + a      # NNNN
    takes_str(d)                 # N
    do_something(d)              # A
    return 0
```

#### Comparison of `literal`s (`"a" == "a"`) --> `bool` ✅

```yaksha
def main() -> int:
    println("a" == "a")          # AC  
    println("a" == "b")          # AC
    println("a" != "a")          # AC
    println("a" != "b")          # AC
    return 0
```

#### Comparison of mixed `str`, `sr` and `literal`s --> `bool` ✅

```yaksha
def main() -> int:
    a: str = "a"                 # N 
    b: sr = "oi"                 # A
    println(b == b)              # A
    println(a == a)              # A
    println((a == b) or (a != b))# AA
    println("a" == a)            # AA
    println(b != a)              # AA
    println(b != "x")            # AA
    return 0
```

#### Wrap/Unwrap `c.CStr`, `Const[Ptr[Const[c.Char]]]` as `sr`

* Create a simple wrapper function in libs.c to wrap `c.CStr`   --> `getref_cstr`
* Create a simple wrapper function in libs.c to unwrap `c.CStr` --> `unref_cstr`
* Create a simple wrapper function in libs.c to wrap `Const[Ptr[Const[c.Char]]]`   --> `getref_ccstr`
* Create a simple wrapper function in libs.c to unwrap `Const[Ptr[Const[c.Char]]]` --> `unref_ccstr`

#### print/println will support -> `literal`, `sr` and `str`. ✅

* See `do_something` and `take_str`

#### Wrap `Array[u8]` as `sr`

* Create a simple wrapper function in libs.strings to wrap `getref_u8a`

#### Wrap `Ptr[u8]` as `sr`

* Create a simple wrapper function in libs.strings to wrap `getref_u8p`

#### Compare with None ✅

```yaksha
def main() -> int:
    a: sr = "a"                  # N
    b: str = "b"                 # A 
    println(a == None)           # N  
    println(b == None)           # N
    println("a" != None)         # NC
    println("a" == None)         # NC
    println(None != a)           # N
    println(None != b)           # N
    println(None == "a")         # NC
    println(None != "a")         # NC 
    return 0
```

## Additional tasks

* Update documentation explaining `sr` data type.