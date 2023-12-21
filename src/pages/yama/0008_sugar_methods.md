---
title: Sugar methods
author: Bhathiya Perera
layout: '../../layouts/YamaPostLayout.astro'
---

# YAMA 0008 - Sugar methods

- Author(s): Bhathiya Perera
- Status   : Draft

## Idea 01 - Arrow

```yaksha
struct Banana:
    color: int
    origin: int

def display(b: Ptr[Banana]) -> None:
    return

def main() -> int:
    b: Banana = ...
    b->display()
    return 0
```

## Idea 02 - Dot ✅

```yaksha
@onstack
class Banana:
    color: int
    origin: int

def display(b: Ptr[Banana]) -> None:
    return

def main() -> int:
    b: Banana = ...
    b.display()
    return 0
```

If `@onstack` or `struct` then we need to use `Ptr[DataType]` otherwise `DataType` can be used. 
Going with `.` as it is already valid AST. Additionally, we can find the method during `type checking` and desugar it.

```yaksha
display(getref(b))
```