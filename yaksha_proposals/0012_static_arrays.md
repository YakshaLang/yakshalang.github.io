# YAMA 0012 - Static arrays

- Author(s): Bhathiya Perera
- Status   : Draft

Static arrays are an important feature in C. Allowing us to create arrays in the stack and pass them around without worrying about memory management. This is a proposal to add static arrays to Yaksha.

 Problem with arrays in C is that it decays to pointers. This is a problem when passing arrays to functions. And we need to pass the size of the array as well. Another problem is array size is not considered part of the data type (as it decays, information is lost).
 
So in Yaksha I would prefer to have a data type that mentions the size of the array as well. `FixedArr[u8,10]` would be different from `FixedArr[u8,20]`. 

```yaksha
def receive_a(item_a: FixedArr[int, 3]) -> int:
    item_a[0] + item_a[2]

def main() -> int:
    a = fixedarr(1, 2, 3)
    b = fixedarr(1, 2, 3, receive_a(a))
    for (i = 0; i < len(b); i++): # <----------- len(b) simply becomes 4
        println(b[i])
    println(a[4]) # <------ this will result in an error
    0
```

## Phase 1 - Initial fixed array support

* Add support for the data type fixedarr(...) builtin.
* Add support for setting and getting individual items.
* Add support for passing to other functions.
* Add support for compiling `len(x)` to an integer.
* Add support for checking if a passed in literal integer is larger than allowed.
* Note this will not be checked in runtime
* `FixedArr[Const[int]]` <--------- elements cannot be updated

## Phase 2 - Add support for more builtins
* Add foreach and other builtins that expect `Array`s to work with `FixedArr`
* Add to documentation
* Add support for intellij and other editors
* Double check this works in structs.
* Add support for things like `float[3]` etc in raylib wrapper generator using `FixedArr`.