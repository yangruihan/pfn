# Pfn Python 互操作教程

本教程介绍如何在 Pfn 中使用 Python 库，以及如何将 Pfn 代码导出给 Python 使用。

## 目录

1. [导入 Python 模块](#导入-python-模块)
2. [调用 Python 函数](#调用-python-函数)
3. [类型映射](#类型映射)
4. [导出给 Python](#导出给-python)
5. [高级用法](#高级用法)
6. [最佳实践](#最佳实践)

---

## 导入 Python 模块

### 基本导入

```pfn
-- 导入 Python 标准库
import python math
import python json
import python os

-- 使用
math.sqrt(16.0)  -- 4.0
json.dumps({ "name": "Alice" })  -- "{\"name\": \"Alice\"}"
```

### 带别名导入

```pfn
-- 使用别名
import python numpy as np
import python pandas as pd

-- 使用
let arr = np.array([1, 2, 3])
let df = pd.DataFrame({ "a": [1, 2, 3] })
```

### 导入子模块

```pfn
-- 导入子模块
import python collections.abc
import python sklearn.linear_model

-- 使用
let model = sklearn.linear_model.LinearRegression()
```

### 选择性导入

```pfn
-- 导入特定函数
import python math (sqrt, sin, cos)

sqrt(16.0)  -- 4.0
sin(0.0)    -- 0.0
cos(0.0)    -- 1.0
```

---

## 调用 Python 函数

### 基本调用

```pfn
-- 调用 Python 函数
import python math

def pythagorean(a: Float, b: Float) -> Float =
  math.sqrt(a * a + b * b)

pythagorean(3.0, 4.0)  -- 5.0
```

### 位置参数

```pfn
import python builtins

-- 位置参数
builtins.max(1, 2, 3)  -- 3
builtins.min(1, 2, 3)  -- 1
```

### 关键字参数

```pfn
import python json

-- 关键字参数
json.dumps({ "a": 1 }, indent=2)
-- 输出:
-- {
--   "a": 1
-- }
```

### 可变参数

```pfn
import python builtins

-- *args
builtins.print("Hello", "World", sep=", ")
-- 输出: Hello, World

-- **kwargs
let options = { "sep": "-", "end": "!\n" }
builtins.print("a", "b", **options)
-- 输出: a-b!
```

### 方法调用

```pfn
import python builtins

-- 字符串方法
let s = "hello"
s.upper()           -- "HELLO"
s.replace("l", "L") -- "heLLo"

-- 列表方法
let lst = [1, 2, 3]
lst.append(4)       -- [1, 2, 3, 4]
lst.pop()           -- 4, lst = [1, 2, 3]
```

---

## 类型映射

### 基本类型映射

| Python 类型 | Pfn 类型 |
|------------|---------|
| `int` | `Int` |
| `float` | `Float` |
| `str` | `String` |
| `bool` | `Bool` |
| `list` | `List a` |
| `tuple` | `(a, b, ...)` |
| `dict` | `Dict k v` |
| `set` | `Set a` |
| `None` | `()` |

### 自动转换

```pfn
import python math

-- Python int -> Pfn Int
let x: Int = math.floor(3.7)  -- 3

-- Python float -> Pfn Float
let y: Float = math.pi  -- 3.14159...

-- Python str -> Pfn String
import python builtins
let s: String = builtins.str(123)  -- "123"

-- Python list -> Pfn List
import python builtins
let lst: List Int = builtins.list([1, 2, 3])
```

### 动态类型

当 Python 类型不确定时，使用 `Py` 类型:

```pfn
import python someLib

-- 动态类型
def process(data: Py a) -> Py b =
  someLib.process(data)

-- 类型检查放宽
@py.dynamic
def callPython(x) = someLib.process(x)
```

### 类型注解推断

```pfn
import python math

-- 从 Python 类型注解推断
-- def sqrt(x: float) -> float
math.sqrt : Float -> Float

-- 从 docstring 推断 (如果可用)
import python numpy as np
np.array : List a -> Py ndarray
```

---

## 导出给 Python

### 基本导出

```pfn
-- 使用 @py.export 装饰器
@py.export
def add(x: Int, y: Int) -> Int = x + y

@py.export
def greet(name: String) -> String = "Hello, " ++ name
```

### 在 Python 中使用

```python
# main.py
from pfn_exports import add, greet

print(add(1, 2))      # 3
print(greet("Alice")) # Hello, Alice
```

### 导出类型

```pfn
-- 导出类型定义
@py.export
type Point = {
  x: Float,
  y: Float
}

@py.export
def distance(p1: Point, p2: Point) -> Float =
  let dx = p2.x - p1.x
  let dy = p2.y - p1.y
  in math.sqrt(dx * dx + dy * dy)
```

```python
# Python 中使用
from pfn_exports import Point, distance

p1 = Point(x=0.0, y=0.0)
p2 = Point(x=3.0, y=4.0)
print(distance(p1, p2))  # 5.0
```

### 导出模块

```pfn
-- src/Math/Stats.pfn
module Math.Stats

@py.export
def mean(xs: List Float) -> Float =
  sum(xs) / length(xs)

@py.export
def variance(xs: List Float) -> Float =
  let m = mean(xs)
  in sum(map (x => (x - m) ** 2) xs) / length(xs)
```

```python
# Python 中使用
from pfn_exports import Math_Stats

data = [1.0, 2.0, 3.0, 4.0, 5.0]
print(Math_Stats.mean(data))      # 3.0
print(Math_Stats.variance(data))  # 2.0
```

---

## 高级用法

### 回调函数

```pfn
import python functools

-- 传递 Pfn 函数给 Python
def applyTwice(f: Int -> Int, x: Int) -> Int =
  f(f(x))

-- 在 Python 中使用
import python someLib
someLib.process(callback=applyTwice)
```

### 异常处理

```pfn
import python builtins

-- 捕获 Python 异常
def safeDiv(x: Float, y: Float) -> Result String Float =
  try
    Ok (x / y)
  catch
    ZeroDivisionError -> Error "division by zero"
    e -> Error (show e)
```

### 上下文管理器

```pfn
import python builtins

-- 使用 with 语句
def readFile(path: String) -> IO String = do
  handle <- builtins.open(path, "r")
  content <- handle.read()
  handle.close()
  pure(content)

-- 或使用 bracket
def safeReadFile(path: String) : IO String =
  IO.bracket
    (builtins.open(path, "r"))
    (handle => handle.close())
    (handle => handle.read())
```

### 类和对象

```pfn
import python dataclasses

-- 创建 Python 类实例
let point = dataclasses.dataclass({ "x": 1.0, "y": 2.0 })

-- 访问属性
point.x  -- 1.0
point.y  -- 2.0
```

---

## 最佳实践

### 1. 类型安全边界

```pfn
-- 在边界处进行类型验证
def safeParse(s: String) -> Result String Int =
  import python builtins
  try
    let n = builtins.int(s)
    if n >= 0
      then Ok n
      else Error "negative number"
  catch
    ValueError -> Error "invalid integer"
```

### 2. 封装 Python 调用

```pfn
-- 封装 Python 库为 Pfn 风格 API
module Data.CSV

import python pandas as pd

def readCSV(path: String) -> Result String (List (Dict String String)) =
  try
    let df = pd.read_csv(path)
    Ok (df.to_dict("records"))
  catch
    e -> Error (show e)

def writeCSV(path: String, data: List (Dict String String)) -> Result String () =
  try
    let df = pd.DataFrame(data)
    df.to_csv(path, index=False)
    Ok ()
  catch
    e -> Error (show e)
```

### 3. 错误处理

```pfn
-- 使用 Result 类型处理 Python 错误
def callPythonSafely(f: Py a -> Py b, x: Py a) -> Result String (Py b) =
  try
    Ok (f(x))
  catch
    Exception as e -> Error (show e)
```

### 4. 性能优化

```pfn
-- 批量操作减少跨边界调用
import python numpy as np

-- 不好: 多次跨边界
def slowSum(xs: List Float) -> Float =
  foldl (+) 0.0 xs

-- 好: 一次跨边界
def fastSum(xs: List Float) -> Float =
  let arr = np.array(xs)
  in np.sum(arr)
```

### 5. 文档化类型

```pfn
-- 为 Python 函数添加类型文档
{-|
  计算数组的标准差
  
  参数:
    xs: 数值列表
  
  返回:
    标准差
  
  Python 等价:
    import numpy as np
    np.std(xs)
-}
def stdDev(xs: List Float) -> Float =
  import python numpy as np
  np.std(np.array(xs))
```

---

## 练习

1. 使用 `requests` 库实现一个 HTTP 客户端
2. 使用 `pandas` 处理 CSV 数据
3. 将 Pfn 实现的排序函数导出给 Python 使用
4. 封装一个 Python 库为 Pfn 风格 API

---

## 下一步

- 查看 [示例项目](../../examples/) 了解实际应用
- 阅读 [Python 互操作设计文档](../python-interop.md) 了解实现细节
- 学习 [效果系统](../language-design.md#效果系统) 处理 IO 操作
