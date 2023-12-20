# YAMA 0001 - Exposing C enums/#defines/consts

- Author(s): Bhathiya Perera
- Status   : ✅

## Problem

In C we can define enums such as below.

```c
// Simple
enum something1 {
  SOMETHING1,
  ANOTHER1
};

// Separate typedef
enum something2 {
  SOMETHING2,
  ANOTHER2
};
typedef enum something2 something2_t;

// Combined
typedef enum
{
  SOMETHING3,
  ANOTHER3
} something3_t;
```

Currently we can use something like

<!-- Note using Python for syntax highlighting, below is Yaksha code -->

```yaksha
SOMETHING: Const[int] = 0
ANOTHER: Const[int] = 1
```

This however make it annoying to maintain, as we now have a copy of the enum value.

We can use below as well.

```yaksha
@nativemacro("SOMETHING")
def something() -> int:
    pass
```

This does not copy the value, but make it annoying to use the API as now we need to access this as `something()`.

## Suggestions

### Suggestion 1

```yaksha
# Expose enum value / #define value
nativexp "SOMETHING" as SOMETHING: Const[int]

# Some simple constant calculations
nativexp """1 + 1""" as TWO: Const[int]
```

- Pro:
  - Clearly define that this is a native expression
- Con:
  - Looks different

### Suggestion 2

```yaksha
TWO: Const[int] = ccode """1 + 1"""
```

- Pro:
  - Consistent syntax
  - Clearly define that this is a native expression (ccode)
- Con:
  - None

### Suggestion 3

```yaksha
TWO: Const[int] <- nativexp """1 + 1"""
```

- Pro:
  - Clearly define that this is a native expression
- Con:
  - Looks different

### Suggestion 4

```yaksha
nativexp """1 + 1""" -> TWO: Const[int]
```

- Pro:
  - None
- Con:
  - Looks different

### Suggestion 5

```yaksha
TWO: Const[int] = nativexp """1 + 1"""
```

- Pro:
  - Consistent syntax
  - Clearly define that this is a native expression (ccode)
- Con:
  - New keyword is introduced

This would compile to 

```c
#define yk__TWO (1 + 1)
```

## Conclusion

I'm going with suggestion 2 as it uses already existing keywords and also at the same time looks consistent with current constants. 
