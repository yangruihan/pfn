# Pfn 入门教程

本教程将帮助你快速上手 Pfn 语言。

## 目录

1. [安装与环境配置](#安装与环境配置)
2. [第一个程序](#第一个程序)
3. [基础语法](#基础语法)
4. [函数定义](#函数定义)
5. [数据类型](#数据类型)
6. [模式匹配](#模式匹配)
7. [列表操作](#列表操作)
8. [类型注解](#类型注解)
9. [模块系统](#模块系统)
10. [下一步](#下一步)

---

## 安装与环境配置

### 系统要求

- Python 3.11+
- pip 或 uv 包管理器

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourorg/pfn.git
cd pfn

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# 安装依赖
pip install -e ".[dev]"
```

### 验证安装

```bash
# 运行测试
make test

# 启动 REPL
pfn repl
```

---

## 第一个程序

创建文件 `hello.pfn`:

```pfn
def main() = "Hello, World!"
```

运行程序:

```bash
pfn run hello.pfn
# 输出: Hello, World!
```

---

## 基础语法

### 注释

```pfn
-- 单行注释

{- 
  多行注释
  可以跨越多行
-}
```

### 字面量

```pfn
-- 整数
42
-17
0xFF  -- 十六进制

-- 浮点数
3.14
-0.001
1.0e10

-- 字符串
"Hello, World!"
"多行\n字符串"

-- 字符
'a'
'\n'
'\t'

-- 布尔值
True
False
```

### 变量绑定

```pfn
-- let 绑定
let x = 5
let y = x + 3

-- 块表达式
let result =
  let a = 1 in
  let b = 2 in
  a + b
-- result = 3
```

---

## 函数定义

### 基本函数

```pfn
-- 无类型注解
def add(x, y) = x + y

-- 带类型注解
def add(x: Int, y: Int) -> Int = x + y

-- 多行函数体
def factorial(n: Int) -> Int =
  if n <= 1
    then 1
    else n * factorial(n - 1)
```

### 匿名函数

```pfn
-- 单参数
let double = fn x => x * 2

-- 多参数
let add = fn x y => x + y

-- 带类型注解
let add = fn (x: Int) (y: Int) => x + y
```

### 柯里化

Pfn 函数默认柯里化:

```pfn
def add(x: Int, y: Int) -> Int = x + y

-- 部分应用
let addFive = add(5)
addFive(3)  -- 8

-- 管道操作
5 |> add(3)  -- 8
```

### 函数组合

```pfn
-- 组合运算符
def (.) f g x = f(g(x))

let addOne x = x + 1
let double x = x * 2

let addOneThenDouble = double . addOne
addOneThenDouble(3)  -- 8
```

---

## 数据类型

### 代数数据类型 (ADT)

```pfn
-- 枚举类型
type Color
  | Red
  | Green
  | Blue

-- 带数据的变体
type Option a
  | Some a
  | None

type Result e a
  | Ok a
  | Error e

-- 递归类型
type List a
  | Nil
  | Cons a (List a)

-- 二叉树
type Tree a
  | Leaf
  | Node a (Tree a) (Tree a)
```

### 记录类型

```pfn
-- 定义记录
type Person = {
  name: String,
  age: Int,
  email: String
}

-- 创建记录
let alice = { name: "Alice", age: 30, email: "alice@example.com" }

-- 字段访问
alice.name  -- "Alice"
alice.age   -- 30

-- 记录更新
let older = { alice with age = 31 }
```

### 元组

```pfn
-- 创建元组
let point = (1.0, 2.0)
let triple = (1, "hello", True)

-- 访问元素
let (x, y) = point
let (a, b, c) = triple

-- 辅助函数
fst point  -- 1.0
snd point  -- 2.0
```

---

## 模式匹配

### 基本模式

```pfn
def describe(x: Int) -> String =
  match x with
    0 -> "zero"
    1 -> "one"
    _ -> "many"

def maybeDouble(opt: Option Int) -> Int =
  match opt with
    Some x -> x * 2
    None -> 0
```

### 嵌套模式

```pfn
def firstTwo(xs: List a) -> Option (a, a) =
  match xs with
    x :: y :: _ -> Some(x, y)
    _ -> None

def deepMatch(tree: Tree Int) -> Int =
  match tree with
    Leaf -> 0
    Node x Leaf Leaf -> x
    Node x left right -> x + deepMatch(left) + deepMatch(right)
```

### 守卫

```pfn
def categorize(n: Int) -> String =
  match n with
    x if x < 0 -> "negative"
    0 -> "zero"
    x if x < 10 -> "small"
    x if x < 100 -> "medium"
    _ -> "large"
```

### 列表模式

```pfn
def sum(xs: List Int) -> Int =
  match xs with
    [] -> 0
    x :: xs -> x + sum(xs)

def take(n: Int, xs: List a) -> List a =
  match (n, xs) with
    (0, _) -> []
    (_, []) -> []
    (n, x :: xs) -> x :: take(n - 1, xs)
```

---

## 列表操作

### 创建列表

```pfn
-- 字面量
let empty = []
let numbers = [1, 2, 3, 4, 5]

-- Cons 操作符
let list = 1 :: 2 :: 3 :: []

-- 范围
let range = [1..10]
let evens = [2, 4..20]
```

### 常用函数

```pfn
-- 映射
map (x => x * 2) [1, 2, 3]  -- [2, 4, 6]

-- 过滤
filter (x => x > 2) [1, 2, 3, 4]  -- [3, 4]

-- 折叠
foldl (+) 0 [1, 2, 3]  -- 6
foldr (++) "" ["a", "b", "c"]  -- "abc"

-- 查找
head [1, 2, 3]  -- Just 1
tail [1, 2, 3]  -- Just [2, 3]
elem 2 [1, 2, 3]  -- True

-- 长度
length [1, 2, 3]  -- 3

-- 反转
reverse [1, 2, 3]  -- [3, 2, 1]

-- 连接
concat [[1, 2], [3, 4]]  -- [1, 2, 3, 4]
[1, 2] ++ [3, 4]  -- [1, 2, 3, 4]
```

### 列表推导

```pfn
-- 基本推导
[x * 2 | x <- [1..5]]  -- [2, 4, 6, 8, 10]

-- 带条件
[x | x <- [1..10], x % 2 == 0]  -- [2, 4, 6, 8, 10]

-- 多变量
[(x, y) | x <- [1..3], y <- [1..2]]
-- [(1,1), (1,2), (2,1), (2,2), (3,1), (3,2)]
```

---

## 类型注解

### 基本类型

```pfn
-- 原始类型
x: Int
x: Float
x: String
x: Bool
x: Char

-- 函数类型
f: Int -> Int
f: Int -> String -> Bool

-- 多态类型
id: a -> a
const: a -> b -> a
flip: (a -> b -> c) -> b -> a -> c
```

### 参数化类型

```pfn
-- 列表
xs: List Int
xs: List String
xs: List (List Int)

-- Option
opt: Option Int
opt: Option String

-- Result
res: Result String Int
res: Result Error User

-- 元组
pair: (Int, String)
triple: (Int, String, Bool)

-- 记录
person: { name: String, age: Int }
```

### 类型变量

```pfn
-- 多态函数
def id(x: a) -> a = x

def fst(pair: (a, b)) -> a =
  match pair with
    (x, _) -> x

def map(f: a -> b, xs: List a) -> List b = ...
```

### 类型约束

```pfn
-- 类型类约束
def show(x: a) -> String where Show a = ...

def eq(x: a, y: a) -> Bool where Eq a = ...

def compare(x: a, y: a) -> Ordering where Ord a = ...
```

---

## 模块系统

### 定义模块

```pfn
-- src/Utils/Math.pfn
module Utils.Math

-- 导出
export add, subtract, multiply

-- 实现
def add(x, y) = x + y
def subtract(x, y) = x - y
def multiply(x, y) = x * y
```

### 导入模块

```pfn
-- 完整导入
import Utils.Math

Math.add(1, 2)

-- 选择性导入
import Utils.Math (add, subtract)

add(1, 2)

-- 别名
import Utils.Math as M

M.add(1, 2)

-- 全部导入
import Utils.Math exposing (..)

add(1, 2)
```

---

## 下一步

恭喜你完成了 Pfn 入门教程！接下来你可以:

1. 阅读 [类型系统教程](./type-system-tutorial.md) 深入了解类型推断
2. 学习 [Python 互操作](./python-interop-tutorial.md) 与 Python 生态集成
3. 查看 [示例项目](../../examples/) 学习实际应用
4. 阅读 [标准库文档](../../stdlib/) 了解可用模块

### 推荐练习

1. 实现一个简单的计算器
2. 编写一个列表排序函数
3. 创建一个处理 JSON 数据的程序
4. 实现一个简单的命令行工具

### 获取帮助

- 查看 [API 文档](../api/)
- 在 GitHub 上提问
- 加入社区讨论
