# Pfn 语法参考

本文档提供 Pfn 语言的完整语法参考。

## 目录

1. [词法结构](#词法结构)
2. [类型语法](#类型语法)
3. [表达式](#表达式)
4. [模式](#模式)
5. [声明](#声明)
6. [模块](#模块)
7. [效果系统语法](#效果系统语法)
8. [Python 互操作语法](#python-互操作语法)

---

## 词法结构

### 注释

```pfn
-- 单行注释

{- 多行注释
   可以嵌套 {- 像这样 -}
-}

--- 文档注释（用于函数和类型）
--- 描述函数的功能
def add(x: Int, y: Int) -> Int = x + y
```

### 标识符

```pfn
-- 常规标识符
myVariable
myFunction
MyType
MyModule

-- 操作符标识符
+
-
*
/
<>
==>
-->

-- 反引号操作符使用
x `add` y  -- 等价于 add(x, y)
```

### 关键字

```
def let in where if then else
match with type interface impl
import export module
effect do
forall exists
data family
True False
```

### 字面量

```pfn
-- 整数
42
0xFF      -- 十六进制
0o77      -- 八进制
0b1010    -- 二进制
1_000_000 -- 下划线分隔

-- 浮点数
3.14
1.0e10
1.0e-10

-- 字符
'a'
'\n'
'\t'
'\x41'    -- ASCII
'\u{1F600}' -- Unicode

-- 字符串
"hello"
"multi\
line"     -- 续行

-- 原始字符串
r"raw\nstring"

-- 多行字符串
"""
multi
line
string
"""

-- 布尔
True
False

-- 单位
()
```

---

## 类型语法

### 基础类型

```pfn
Int
Float
Bool
Char
String
Unit
```

### 类型变量

```pfn
a          -- 单字母（约定：小写）
elem       -- 描述性名称
```

### 函数类型

```pfn
a -> b
Int -> String
Int -> Int -> Int        -- 柯里化
(Int, Int) -> Int        -- 元组参数（语法糖）
```

### 元组类型

```pfn
()
(a, b)
(Int, String, Bool)
```

### 列表类型

```pfn
[a]
List Int
List (List Int)
```

### 记录类型

```pfn
{ x: Int, y: Int }
{ name: String, age: Int }
{ | r }                  -- 行多态（开放记录）
{ name: String | r }     -- 部分指定
```

### 可选类型

```pfn
Option a
a?                       -- 语法糖
```

### 泛型类型

```pfn
List a
Map k v
Tree a
```

### 高阶类型

```pfn
(* -> *)
(* -> * -> *)
```

### forall/exists

```pfn
forall a. a -> a
exists a. Show a => a
forall a b. a -> b -> a
```

### 类型约束

```pfn
Show a => a -> String
(Eq a, Show a) => a -> a -> String
```

---

## 表达式

### 变量引用

```pfn
x
myVariable
List.map  -- 限定名
```

### 字面量

```pfn
42
3.14
"hello"
'a'
True
()
```

### 函数应用

```pfn
f(x)
f(x, y)          -- 多参数
f x              -- 无括号（柯里化）
f x y            -- 等价于 f(x)(y)
```

### 中缀操作符

```pfn
x + y
x * y + z        -- 优先级
x |> f           -- 管道
f <| x           -- 反向管道
x ++ y           -- 字符串/列表连接
```

### 操作符优先级

| 优先级 | 操作符 | 结合性 |
|--------|--------|--------|
| 1 (最低) | `|>` | 左 |
| 2 | `||` | 右 |
| 3 | `&&` | 右 |
| 4 | `==`, `!=`, `<`, `>`, `<=`, `>=` | 无 |
| 5 | `::` | 右 |
| 6 | `++` | 右 |
| 7 | `+`, `-` | 左 |
| 8 | `*`, `/`, `%` | 左 |
| 9 (最高) | 单目 `-`, `!` | - |

### Lambda 表达式

```pfn
fn x => x + 1
fn x y => x + y
\x => x + 1            -- 短语法
\x y => x + y
\(x, y) => x + y       -- 模式解构
```

### let 表达式

```pfn
let x = 5 in x + 1

let x = 5
let y = 10
x + y

-- let 块
let
  x = 5
  y = 10
in
  x + y
```

### if 表达式

```pfn
if x > 0 then "positive" else "non-positive"

if x > 0 then
  "positive"
else if x < 0 then
  "negative"
else
  "zero"
```

### match 表达式

```pfn
match x with
| 0 -> "zero"
| 1 -> "one"
| _ -> "many"

match xs with
| [] -> "empty"
| [x] -> "one"
| x :: y :: _ -> "two or more"

match point with
| (x, y) -> x + y

match person with
| { name, age } -> name ++ " is " ++ show(age)
```

### 块表达式

```pfn
-- 序列表达式（最后一个表达式的值作为结果）
let result =
  let x = 1
  let y = 2
  x + y
```

### do 记法

```pfn
do
  x <- IO.input "Name: "
  y <- IO.input "Age: "
  IO.print(x ++ ", " ++ y)

-- 等价于
IO.input("Name: ") >>= fn x =>
  IO.input("Age: ") >>= fn y =>
    IO.print(x ++ ", " ++ y)
```

### 列表表达式

```pfn
[1, 2, 3]
[x | x <- [1, 2, 3], x > 1]        -- 列表推导式
[x * 2 | x <- [1..10], even(x)]    -- 带条件
[(x, y) | x <- [1..3], y <- [1..3]] -- 多生成器
```

### 范围表达式

```pfn
[1..10]      -- 1 到 10
[1, 3..10]   -- 1, 3, 5, 7, 9（步长 2）
['a'..'z']   -- 字符范围
```

### 记录表达式

```pfn
{ name: "Alice", age: 30 }
{ person with age = 31 }           -- 记录更新
{ .. person }                      -- 展开
```

### 元组表达式

```pfn
(1, 2)
(1, "hello", True)
```

### 访问表达式

```pfn
person.name        -- 字段访问
tuple.0            -- 元组索引
xs[0]              -- 列表/数组索引
xs[1:5]            -- 切片
xs[::-1]           -- 反转切片
```

### 类型注解

```pfn
x : Int
(x, y) : (Int, Int)
fn x => x : a -> a
```

---

## 模式

### 字面量模式

```pfn
0
42
"hello"
True
```

### 变量模式

```pfn
x
_                    -- 通配符（忽略绑定）
```

### 元组模式

```pfn
(x, y)
(x, y, z)
```

### 列表模式

```pfn
[]
[x]
[x, y]
[x, y, ...]          -- 剩余模式
x :: xs              -- cons 模式
```

### 记录模式

```pfn
{ name, age }
{ name: n, age: a }
{ x, y, ... }        -- 宽松匹配
```

### 构造器模式

```pfn
Some x
None
Ok value
Error msg
Node left value right
```

### 别名模式

```pfn
p @ (x, y)           -- p 是整个元组的别名
```

### 嵌套模式

```pfn
Some (x, y)
Node Leaf x Leaf
{ person: { name } }
```

### 守卫

```pfn
| x if x > 0 -> "positive"
| x if even(x) -> "even"
```

---

## 声明

### 值绑定

```pfn
let x = 5
let y: Int = 10
```

### 函数定义

```pfn
def add(x, y) = x + y
def add(x: Int, y: Int) -> Int = x + y

-- 模式匹配定义
def head([]) = None
def head(x :: _) = Some x

-- where 子句
def quadraticRoots(a, b, c) =
  (root1, root2) where
    d = b * b - 4 * a * c
    root1 = (-b + sqrt(d)) / (2 * a)
    root2 = (-b - sqrt(d)) / (2 * a)
```

### 类型定义

```pfn
-- 类型别名
type StringList = List String
type Point = (Float, Float)

-- Sum 类型
type Option a
  | Some a
  | None

-- 带字段名
type Person =
  { name: String
  , age: Int
  , email: String
  }

-- GADT
type Expr a where
  Lit : Int -> Expr Int
  Add : Expr Int -> Expr Int -> Expr Int
```

### 类型类定义

```pfn
interface Eq a where
  (==) : a -> a -> Bool
  (!=) : a -> a -> Bool
  (!=) x y = not(x == y)   -- 默认实现

interface Ord a extends Eq a where
  compare : a -> a -> Ordering
```

### 类型类实现

```pfn
impl Eq Int where
  (==) x y = builtinIntEq(x, y)

impl Eq a => Eq (List a) where
  (==) [] [] = True
  (==) (x :: xs) (y :: ys) = x == y && xs == ys
  (==) _ _ = False
```

### 效果定义

```pfn
effect IO
  input : String -> IO String
  print : String -> IO ()
  readFile : String -> IO String

effect State s
  get : State s s
  put : s -> State s ()
```

---

## 模块

### 模块定义

```pfn
module MyModule

export add, mul, Point

-- 导出所有
export ..

-- 导出类型和构造器
export type Point, MkPoint

-- 定义
def add(x, y) = x + y
def mul(x, y) = x * y
type Point = MkPoint Float Float
```

### 模块导入

```pfn
import MyModule
import MyModule (add, mul)
import MyModule as M
import MyModule exposing (..)

-- Python 模块
import python math
import python numpy as np
import python os.path (join, exists)
```

### 模块类型

```pfn
module type Monoid = sig
  type t
  val empty : t
  val append : t -> t -> t
end

module ListMonoid : Monoid where
  type t = List a
  def empty = []
  def append(xs, ys) = xs ++ ys
```

---

## 效果系统语法

### 效果标注

```pfn
-- 单一效果
def main : IO () = ...

-- 多效果
def process : IO + State Int + Throw String String = ...

-- 效果变量
def foo : e + IO () = ...
```

### 效果处理

```pfn
try expr with
| handler1 => ...
| handler2 => ...
```

### do 记法

```pfn
do
  x <- action1
  y <- action2
  pure(x + y)

-- let 绑定（无绑定）
do
  action1
  action2
  pure result
```

---

## Python 互操作语法

### 导入

```pfn
import python module_name
import python module_name as alias
import python module.submodule (name1, name2)
```

### Python 类型

```pfn
Py a           -- 包装的 Python 对象
PyAny          -- 动态类型
PyModule       -- Python 模块
PyCallable     -- Python 可调用对象
PyIterator     -- Python 迭代器
```

### 注解

```pfn
@py.export              -- 导出给 Python
@py.export(name = "x")  -- 导出为指定名称
@py.class               -- Python 类
@py.inherits(Parent)    -- 继承 Python 类
@py.attr                -- 属性
@py.method              -- 方法
@py.init                -- 构造器
@py.static              -- 静态方法
@py.property            -- 属性 getter
@py.coerce              -- 允许类型强制
```

### Python 表达式

```pfn
py.raise(Exception("error"))  -- 抛出异常
py.await(async_expr)          -- await
py.await_all([...])           -- asyncio.gather
py.super()                    -- super() 调用
```

---

## 运算符定义

```pfn
-- 中缀运算符
def (x |> f) = f(x)
def (f <| x) = f(x)

-- 自定义优先级
infixl 7 |>
infixr 8 <|

-- 自定义运算符
def (x <+> y) = x ++ y

-- 单目运算符
def (!x) = not(x)
prefix 9 !
```
