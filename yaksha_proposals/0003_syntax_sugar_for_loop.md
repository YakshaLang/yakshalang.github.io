# YAMA 0003 - For loop / loop

- Author(s): Bhathiya Perera
- Status   : ✅

<!-- different languages for code blocks are used to get maximum syntax matching for free, please ignore -->

## Problem

Yaksha programming language does not offer a `for` syntax sugar. This is annoying for someone coming from Python or other languages that has this feature. 
We have `foreach` builtin and `while` loop, which can be used at the moment. `for` can make certain things easy.


### Use case 1 - for each element in array ✅

How it works now
```python
items: Array[int] = get_it()

c: int = 0
length: int = len(items)

while c < length:
    if items[c] == 2:
        c += 1 
        continue
    println(items[c])
    c += 1
```

Syntax sugar (we will keep compulsory data types for now)

```python
for item: int in get_it(): # get_it should return Array[T]
    if item == 2:
        continue
    println(item)
```

Desugared 

```python
yy__1t: Array[int] = get_it()
yy__2t: int = 0
yy__3t: int = len(yk__1t)

while yy__2t < yy__3t:
    ccode """#define yy__item yy__1t[yy__2t]\n// desugar begin"""
    expose_native item: int      # To expose what we put in above C code
    if item == 2:
        yy__2t += 1
        continue                 # Continue must increase the counter
    println(item)
    ccode """#undef yy__item\n// desugar end"""
    yy__2t += 1               # Increase count at the very end
```


### Use case 2 - endless loops ✅

Syntax sugar

```python
for:
    game_step()
    log_stuff()
```

Desugared

```python
while True:
    game_step()
    log_stuff()
```

### Use case 3 - custom iterators / iterables ⚠️(deferred at this step)

Syntax sugar

```python
def next_book(x: Books) -> Book:
    pass
  
def has_next_book(x: Books) -> bool:
    pass

def process() -> None:
    books: Books = get_it()
    it: Iterator[Book] = iterator("Book", books, next_book, has_next_book)
    for element: Book in it:
        print_book(element)
```

### Use case 4 - range for loops ⚠️(deferred at this step)

Syntax sugar

```python
# Example 1
r: Range[int] = range(1, 5, 2)
for i: int in r:
    if i == 1: # do not print 1
       continue
    println(i)

# Example 2
for i: int in range(1, 5, 2):
    if i == 1: # do not print 1
       continue
    println(i)
```

Desugared

```python
r: Tuple[int, int, int]
r[0] = 1
r[1] = 5
r[2] = 2

hidden__c = r[0]
while hidden__c < r[1]:
    i: int = hidden__c
    if i == 1:
        hidden__c += r[2]
        continue
    println(i)
    hidden__c += r[2]
```

## Conclusion

Iterators/Ranges are deferred for now. It would be better to come up with a generic `Iterator` approach for these.

At the moment I think endless loops and simple foreach style loops should be implemented.
