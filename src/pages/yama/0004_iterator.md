---
title: Iterators
author: Bhathiya Perera
layout: '../../layouts/YamaPostLayout.astro'
---

# YAMA 0004 - Iterators

- Author(s): Bhathiya Perera
- Status   : Draft

## Problem

We would like to introduce support for iterators, such that it allows Yaksha to simply iterate arbitrary content. 

### Use case 1 - custom iterators / iterables

Syntax sugar

```yaksha
def next_book(x: Ptr[Books]) -> Book:
    pass

def has_next_book(x: Ptr[Books]) -> bool:
    pass

def process() -> None:
    books: Books = get_it()
    # Books is the mutable state that is passed to next_book and has_next_book
    # Book is the type that is returned from the next_book
    it: Iterator[Book] = iterator(books, next_book, has_next_book)

    for element: Book in it:
        print_book(element)
```

Desugared

```yaksha
def next_book(x: Ptr[Books]) -> Book:
    pass

def has_next_book(x: Ptr[Books]) -> bool:
    pass

def process() -> None:
    books: Books = get_it()

    it: Tuple[Books, .., ..]
    it[0] = books
    it[1] = next_book
    it[2] = has_next_book

    while (it[1])(getref(it[0])):
        element: Book = (it[2])(getref(it[0]))
        print_book(element)
```

### Use case 2 - range for loops

Syntax sugar

```yaksha
# Example 1
r: Iterator[int] = range(1, 5, 2)
for i: int in r:
    if i == 1: # do not print 1
       continue
    println(i)

# Example 2 (would desugar similarly)
for i: int in range(1, 5, 2):
    if i == 1: # do not print 1
       continue
    println(i)
```

Desugared

```yaksha
r: Tuple[Tuple[int, int, int, int], .., ..]
yy__1t: Tuple[int, int, int, int]
yy__1t[0] = 1       # start
yy__1t[1] = 5       # stop *non inclusive
yy__1t[2] = 2       # step
yy__1t[3] = yy__1t[0] # current item
r[0] = yy__1t
r[1] = yk__next_range
r[2] = yk__has_range

while (r[1])(getref(r[0])):
    i: int = (r[2])(getref(r[0]))
    if i == 1:
        continue
    println(i)
```

## Conclusion

Iterators make a fine addition to foreach loop. 