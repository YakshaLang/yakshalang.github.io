# YAMA 0002 - Adding support for stack allocated structs

- Author(s): Bhathiya Perera
- Status   : ✅

## Problem

```yaksha
class Enemy:
    x: int
    y: int
    hit_points: int

def main() -> int:
    enemies: Array[Enemy] = arrnew("Enemy", 2)
    enemies[0] = Enemy()
    enemies[1] = Enemy()
    return 0
```

Given a structure like above, it makes no sense to allocate individual objects in heap all the time.
We can avoid it by using `Tuple` however we lose the information about field names then. 
Keep in mind that the Tuple's in Yaksha are mutable (Mutable `Tuple`s are what we have at the moment, may or may not change in future).

## Suggestions

### Suggestion 1

```yaksha
@namedtuple
class Enemy:
    x: int
    y: int
    hit_points: int
```

- Pro:
  - Consistent syntax
  - Does not introduce a new keyword
- Con:
  - No way to tell that this get allocated in stack?

### Suggestion 2

```yaksha
@dataclass
class Enemy:
    x: int
    y: int
    hit_points: int
```

- Pro:
  - Consistent syntax
  - Does not introduce a new keyword
  - Familiarity 
- Con:
  - No way to tell that this get allocated in stack?
  - Looks like python but different might make it confusing

### Suggestion 3

```yaksha
class Enemy:
    x: int
    y: int
    hit_points: int
Enemy()     # << allocate on stack
new Enemy() # << allocate on heap
```

- Pro:
  - Similar to how C++ works. 
  - `new` - `del` pairing
- Con:
  - Need to rewrite everything to follow this convention
- Note⚠️⚠️: 
  - Perhaps reconsider this approach at some point

### Suggestion 4 ✅

```yaksha
@onstack
class Enemy:
    x: int
    y: int
    hit_points: int
# Rename @dotaccess to @onstack
# And use that for this purpose
Enemy() # This is disallowed. Just create a variable and you can use it.
```

- Pro:
  - Defines that this is different from a normal class
  - Clearly visible that this get allocated on stack
- Con:
  - Require changes to how @dotaccess works currently

## Conclusion

I am thinking suggestion 4 is the best approach.

## Update

Additionally Yaksha now supports `struct` keyword. That act as a syntax sugar for `@onstack class`.