# YAMA 0010 - Numbers auto casting when widening

- Author(s): Bhathiya Perera
- Status   : ✅

Following casting is suggested for basic binary mathematical operations.

Assignment would follow same casting style, except lhs needs to be wider.

Bitwise operations would require manual casting to same data type.

```text
    .-------------. 
    |    bool     | 
    '.-----------.' 
     |          .V-.
     |          |i8|
     |          '.-'
    .V----------.|  
    |    u8     ||  
    '.---------.'|  
    .V-------. | |  
    |  u16   | | |  
    '.------.' | |  
    .V----. |  | |  
    | u32 | |  | |  
    '.---.' |  | |  
    .V--.|  |  | |  
    |u64||  |  | |  
    '.--'|  |  | |  
.---.|   |  |  | |  
|f64||   |  |  | |  
'^--'|   |  |  | |  
.'---V-. |  |  | |  
| f32  | |  |  | |  
'^-----' |  |  | |  
.'-------V-.|  | |  
|   i64    ||  | |  
'^---------'|  | |  
.'----------V-.| |  
|     i32     || |  
'^------------'| |  
.'-------------V-V-.
|       i16        |
'------------------'
```