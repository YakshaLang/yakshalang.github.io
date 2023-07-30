# YAMA 0008 - Sugar methods

- Author(s): Bhathiya Perera
- Status   : Draft

## Idea 01 - Arrow

```python
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

```python
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

```python
display(getref(b))
```