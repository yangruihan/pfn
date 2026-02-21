# Pfn Python 互操作设计

本文档详细描述 Pfn 与 Python 的互操作机制。

## 目录

1. [设计目标](#设计目标)
2. [导入 Python 模块](#导入-python-模块)
3. [类型映射](#类型映射)
4. [调用 Python 函数](#调用-python-函数)
5. [导出给 Python](#导出给-python)
6. [对象系统互操作](#对象系统互操作)
7. [错误处理](#错误处理)
8. [性能考虑](#性能考虑)

---

## 设计目标

1. **零成本抽象**: Pfn 类型映射到 Python 原生类型，无额外包装
2. **类型安全**: 尽可能提供静态类型检查
3. **渐进式采用**: 可以在任何地方混合 Pfn 和 Python
4. **完整生态**: 所有 Python 库都可以使用

---

## 导入 Python 模块

### 基础导入

```pfn
-- 导入整个模块
import python math
import python os
import python sys

-- 使用
math.sqrt(16.0)  -- 4.0
os.getcwd()
```

### 别名导入

```pfn
import python numpy as np
import python pandas as pd

np.array([1, 2, 3])
pd.DataFrame({ "a": [1, 2] })
```

### 选择性导入

```pfn
import python math (sqrt, sin, cos)

sqrt(16.0)
```

### from 导入

```pfn
import python os.path (join, exists)

join("dir", "file.txt")
```

### 导入子模块

```pfn
import python sklearn.linear_model
import python sklearn.linear_model as lm

lm.LinearRegression()
```

### 条件导入

```pfn
import python? optional_lib  -- 如果不存在，返回 None

match optional_lib with
| Some lib -> lib.doSomething()
| None -> fallback()
```

---

## 类型映射

### Pfn 到 Python

| Pfn 类型 | Python 类型 | 说明 |
|----------|-------------|------|
| `Int` | `int` | 直接映射 |
| `Float` | `float` | 直接映射 |
| `Bool` | `bool` | 直接映射 |
| `String` | `str` | 直接映射 |
| `Char` | `str` (长度1) | 直接映射 |
| `List a` | `list` | 直接映射 |
| `Tuple a b` | `tuple` | 直接映射 |
| `{ a: A, b: B }` | `dict` | 字典映射 |
| `Unit` | `None` | 直接映射 |
| `Option a` | `a \| None` | 可能的 None |
| `a -> b` | `Callable` | 函数对象 |
| `PyAny` | `Any` | 动态类型 |

### Python 到 Pfn

```pfn
-- 类型包装
type Py a           -- 包装 Python 对象，保留原始类型信息
type PyAny          -- 任意 Python 对象（动态）
type PyModule       -- Python 模块
type PyClass        -- Python 类
type PyCallable     -- Python 可调用对象

-- 示例
def usePyObj(obj: Py Dict) -> Int =
  -- 安全访问 Python 字典
  ...
```

### 类型转换

```pfn
-- 安全转换
def toPfn : Py a -> Option b where Convertible a b
def toPy : a -> Py b where Convertible a b

-- 强制转换（运行时检查）
def unsafeToPfn : Py a -> b

-- 示例
import python json

def parseJson(s: String) -> Result String (Py Dict) =
  try
    Ok(json.loads(s))
  catch e =>
    Error("Invalid JSON: " ++ str(e))
```

---

## 调用 Python 函数

### 基础调用

```pfn
import python math

def distance(x1: Float, y1: Float, x2: Float, y2: Float) -> Float =
  math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))
```

### 关键字参数

```pfn
import python requests

def fetchData(url: String) -> Py Response =
  requests.get(
    url,
    timeout = 30,
    headers = { "User-Agent": "Pfn/1.0" }
  )
```

### 可变参数

```pfn
import python builtins

def pyPrint(...args: List PyAny) -> Unit =
  builtins.print(*args)
```

### 方法调用

```pfn
import python pandas as pd

def processData(df: Py DataFrame) -> Py DataFrame =
  df
    .dropna()
    .groupby("category")
    .agg({ "value": "sum" })
```

### 属性访问

```pfn
import python sys

def getVersion() -> String =
  sys.version
```

---

## 导出给 Python

### 函数导出

```pfn
-- 导出函数
@py.export
def add(x: Int, y: Int) -> Int = x + y

-- 导出为特定名称
@py.export(name = "add_numbers")
def add(x: Int, y: Int) -> Int = x + y
```

```python
# Python 中使用
from mymodule import add

result = add(1, 2)  # 3
```

### 类型导出

```pfn
@py.export
type Point = {
  x: Float,
  y: Float
}

@py.export
def distance(p1: Point, p2: Point) -> Float =
  math.sqrt((p2.x - p1.x) ** 2 + (p2.y - p1.y) ** 2)
```

```python
# Python 中使用
from mymodule import Point, distance

p1 = Point(x=0, y=0)
p2 = Point(x=3, y=4)
print(distance(p1, p2))  # 5.0
```

### 模块导出

```pfn
-- 导出整个模块
@py.export
module Utils =
  def add(x, y) = x + y
  def mul(x, y) = x * y
  type Point = { x: Float, y: Float }
```

```python
# Python 中使用
from mymodule import Utils

Utils.add(1, 2)  # 3
Utils.mul(3, 4)  # 12
```

### 回调函数

```pfn
-- Pfn 函数作为 Python 回调
import python threading

def startThread(callback: Int -> String) -> Py Thread =
  threading.Thread(target = fn x => py.export(callback)(x))

-- 使用
let thread = startThread(fn x => "Got: " ++ show(x))
```

---

## 对象系统互操作

### 创建 Python 类

```pfn
@py.class
class Counter =
  @py.attr
  val count: Ref Int

  @py.init
  def new() = { count = ref 0 }

  @py.method
  def increment(self) : Unit =
    self.count := !self.count + 1

  @py.method
  def get(self) : Int = !self.count
```

```python
# Python 中使用
from mymodule import Counter

c = Counter()
c.increment()
print(c.get())  # 1
```

### 继承 Python 类

```pfn
import python collections

@py.inherits(collections.abc.MutableMapping)
class MyDict =
  @py.attr
  val data: Py Dict

  @py.init
  def new() = { data = {} }

  @py.method
  def __getitem__(self, key: String) -> PyAny = self.data[key]

  @py.method
  def __setitem__(self, key: String, value: PyAny) : Unit =
    self.data[key] = value

  @py.method
  def __delitem__(self, key: String) : Unit =
    del self.data[key]

  @py.method
  def __iter__(self) : PyIterator =
    iter(self.data)

  @py.method
  def __len__(self) : Int =
    len(self.data)
```

### 实现 Python 协议

```pfn
-- 实现迭代器协议
@py.export
type Range =
  @py.iter
  def __iter__(self: Range) : RangeIterator

@py.export
type RangeIterator =
  @py.iter
  def __iter__(self: RangeIterator) : RangeIterator

  @py.next
  def __next__(self: RangeIterator) : Int
```

### 装饰器

```pfn
-- 使用 Python 装饰器
import python functools

@functools.lru_cache(maxsize = 128)
def expensiveComputation(n: Int) -> Int =
  -- ... 复杂计算
  n * n

-- 定义装饰器供 Python 使用
@py.export
def memoize(f: a -> b) -> a -> b =
  cache = {}
  fn x =>
    match cache.get(x) with
    | Some y -> y
    | None ->
        let y = f(x)
        cache[x] = y
        y
```

---

## 错误处理

### Python 异常转换

```pfn
-- Python 异常转换为 Pfn Result
import python json

def safeParse(s: String) : Result String (Py Dict) =
  py.try
    Ok(json.loads(s))
  catch ValueError as e =>
    Error("ValueError: " ++ str(e))
  catch Exception as e =>
    Error("Error: " ++ str(e))
```

### Pfn 错误导出为 Python 异常

```pfn
@py.export
def divide(x: Float, y: Float) : Float =
  if y == 0.0
    then py.raise(ValueError("Division by zero"))
    else x / y
```

```python
# Python 中
from mymodule import divide

try:
    divide(1, 0)
except ValueError as e:
    print(e)  # Division by zero
```

### 异常类型映射

| Pfn 类型 | Python 异常 |
|----------|-------------|
| `Error String` | `RuntimeError` |
| `ValueError` | `ValueError` |
| `TypeError` | `TypeError` |
| `KeyError` | `KeyError` |
| `IndexError` | `IndexError` |

---

## 性能考虑

### 零开销映射

```pfn
-- 这些类型直接映射，无运行时开销
let x: Int = 5          -- Python int
let y: Float = 3.14     -- Python float
let z: String = "hello" -- Python str
let xs: List Int = [1, 2, 3]  -- Python list
```

### 批量操作

```pfn
-- 避免频繁的 Pfn-Python 边界跨越
-- 不推荐
def slowSum(xs: List Int) : Int =
  foldl((a, b) => a + py.int(b), 0, xs)  -- 每次都调用 Python

-- 推荐
def fastSum(xs: List Int) : Int =
  foldl((a, b) => a + b, 0, xs)  -- 纯 Pfn 实现
```

### 延迟求值

```pfn
-- 使用生成器避免创建中间列表
import python itertools

def lazyMap(f: a -> b, xs: PyIterator) : PyIterator =
  itertools.imap(f, xs)
```

### 内存视图

```pfn
-- 使用内存视图避免数据复制
import python numpy as np

def processArray(arr: Py ndarray) : Py ndarray =
  arr[0:100]  -- 零拷贝视图
```

---

## 互操作示例

### 使用 NumPy

```pfn
import python numpy as np

def matrixOps() : Py ndarray =
  let a = np.array([[1, 2], [3, 4]])
  let b = np.array([[5, 6], [7, 8]])
  np.dot(a, b)  -- 矩阵乘法
```

### 使用 Flask

```pfn
import python flask

app = flask.Flask(__name__)

@app.route("/")
@py.export
def index() : String =
  "<h1>Hello from Pfn!</h1>"

@app.route("/api/data")
@py.export
def getData() : Py Dict =
  { "status": "ok", "data": [1, 2, 3] }

def main : IO () =
  app.run(host = "0.0.0.0", port = 5000)
```

### 使用 Pandas

```pfn
import python pandas as pd

def analyzeData(csvPath: String) : Py DataFrame =
  df = pd.read_csv(csvPath)
  df
    .query("age > 18")
    .groupby("city")
    .agg({ "salary": "mean" })
    .sort_values("salary", ascending = False)
```

### 使用 asyncio

```pfn
import python asyncio

async def fetchUrls(urls: List String) : List String =
  py.await_all(
    urls |> map(fn url => fetchUrl(url))
  )

async def fetchUrl(url: String) : String =
  py.await(
    aiohttp.ClientSession().get(url)
      .then(fn r => r.text())
  )
```
