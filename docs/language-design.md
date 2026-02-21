# Pfn 语言设计

本文档详细描述 Pfn 语言的核心设计理念和语义。

## 目录

1. [设计原则](#设计原则)
2. [核心语义](#核心语义)
3. [求值策略](#求值策略)
4. [效果系统](#效果系统)
5. [模块系统](#模块系统)
6. [错误处理](#错误处理)
7. [并发模型](#并发模型)

---

## 设计原则

### 1. 纯函数式优先

**引用透明性**: 表达式的值只依赖于其子表达式的值，不依赖任何外部状态。

```pfn
-- 这意味着相同的输入总是产生相同的输出
def double(x: Int) -> Int = x * 2

double(5)  -- 永远是 10，无论何时何地调用
```

**不可变性**: 所有绑定默认不可变，数据结构默认持久化。

```pfn
-- 列表是不可变的
let xs = [1, 2, 3]
let ys = 0 :: xs  -- ys = [0, 1, 2, 3], xs 不变

-- 记录是不可变的
let person = { name: "Alice", age: 30 }
let older = { person with age = 31 }  -- 创建新记录
```

### 2. 表达力与简洁性

**声明式风格**: 描述"是什么"而非"怎么做"。

```pfn
-- 声明式数据处理
def adults(people: List Person) -> List Person =
  people
    |> filter(_.age >= 18)
    |> sortBy(_.name)

-- 等价的命令式 Python（对比）
-- adults = []
-- for p in people:
--     if p.age >= 18:
--         adults.append(p)
-- adults.sort(key=lambda x: x.name)
```

**组合性**: 小函数组合成复杂行为。

```pfn
-- 函数组合
def process = parse |> validate |> transform |> save

-- 或使用组合运算符
def process = parse >> validate >> transform >> save
```

### 3. 安全性

**类型安全**: 编译时捕获大部分错误。

```pfn
-- 类型错误在编译时发现
def add(x: Int, y: Int) -> Int = x + y
add(1, "hello")  -- 编译错误！
```

**空安全**: 没有 null，使用 Option 类型。

```pfn
-- 没有 NullPointerException
def head(xs: List a) -> Option a =
  match xs with
  | [] -> None
  | x :: _ -> Some x
```

**穷尽性检查**: 模式匹配必须覆盖所有情况。

```pfn
type Color = Red | Green | Blue

def toHex(c: Color) -> String =
  match c with
  | Red -> "#FF0000"
  | Green -> "#00FF00"
  -- 编译警告：缺少 Blue 的处理
```

### 4. 实用主义

**渐进式类型**: 与 Python 交互时类型检查可放宽。

```pfn
-- 与动态类型 Python 库交互
import python someLib

@py.dynamic
def callPython(x) = someLib.process(x)  -- 类型检查放宽
```

**性能提示**: 允许在关键路径上给出优化提示。

```pfn
@strict  -- 禁用惰性求值
@inline  -- 内联提示
def criticalPath(x: Int) -> Int = ...
```

---

## 核心语义

### 绑定与作用域

```pfn
-- let 绑定（不可变）
let x = 5
let y = x + 3  -- y = 8

-- 块作用域
let result =
  let a = 1 in
  let b = 2 in
  a + b  -- result = 3

-- 函数绑定
def add(x, y) = x + y

-- 操作符定义
def (x <| f) = f(x)  -- 反向应用
def (f |> x) = f(x)  -- 管道
```

### 函数

**一等函数**: 函数是值，可以传递、返回、存储。

```pfn
-- 高阶函数
def twice(f: a -> a, x: a) -> a = f(f(x))

-- 返回函数
def adder(n: Int) -> Int -> Int =
  def add(x: Int) -> Int = x + n
  add

-- 匿名函数
let double = fn x => x * 2
let add = fn x y => x + y

-- 柯里化（自动）
def add(x: Int, y: Int) -> Int = x + y
let addFive = add(5)  -- Int -> Int
addFive(3)  -- 8
```

### 代数数据类型

**Sum Types (变体类型)**:

```pfn
-- 简单枚举
type Bool = True | False

-- 带数据的变体
type Option a
  | Some a
  | None

type Either l r
  | Left l
  | Right r

type Tree a
  | Leaf
  | Node a (Tree a) (Tree a)
```

**Product Types (积类型)**:

```pfn
-- 记录（命名积类型）
type Person = {
  name: String,
  age: Int,
  email: String
}

-- 元组（位置积类型）
type Point = (Float, Float)
type Triple a = (a, a, a)
```

**递归类型**:

```pfn
-- 链表
type List a
  | Nil
  | Cons a (List a)

-- 二叉树
type Tree a
  | Empty
  | Branch a (Tree a) (Tree a)

-- 表达式 AST
type Expr
  | Lit Int
  | Add Expr Expr
  | Mul Expr Expr
  | Var String
```

**GADTs (广义代数数据类型)**:

```pfn
-- 类型安全的 AST
type Expr a where
  Lit : Int -> Expr Int
  BoolLit : Bool -> Expr Bool
  Add : Expr Int -> Expr Int -> Expr Int
  If : Expr Bool -> Expr a -> Expr a -> Expr a

def eval : Expr a -> a
  | Lit n -> n
  | BoolLit b -> b
  | Add e1 e2 -> eval(e1) + eval(e2)
  | If cond then_ else_ ->
      if eval(cond) then eval(then_) else eval(else_)
```

### 模式匹配

**基础模式**:

```pfn
match x with
| 0 -> "zero"
| 1 -> "one"
| _ -> "many"

match list with
| [] -> "empty"
| [x] -> "one element: " ++ show(x)
| [x, y] -> "two elements"
| x :: xs -> "head is " ++ show(x)

match tuple with
| (a, b) -> a + b

match record with
| { name, age } -> name ++ " is " ++ show(age)
```

**嵌套模式**:

```pfn
type Tree a = Leaf | Node a (Tree a) (Tree a)

def contains(x: a, tree: Tree a) -> Bool where Eq a =
  match tree with
  | Leaf -> False
  | Node y Leaf Leaf -> y == x
  | Node y left right ->
      y == x || contains(x, left) || contains(x, right)
```

**守卫**:

```pfn
def describe(x: Int) -> String =
  match x with
  | n if n < 0 -> "negative"
  | 0 -> "zero"
  | n if n < 10 -> "small positive"
  | _ -> "large positive"
```

**视图模式** (View Patterns):

```pfn
def lookup(key: String, dict: Dict String a) -> Option a =
  match dict with
  | lookup(key) -> Some v -> v  -- 调用 lookup 函数匹配结果
  | _ -> None
```

---

## 求值策略

### 默认：严格求值

Pfn 默认使用严格（及早）求值，与 Python 保持一致。

```pfn
-- 参数在传入前求值
def f(x: Int) = x + 1
f(2 + 3)  -- 先计算 2 + 3 = 5，再调用 f(5)
```

### 惰性求值

显式标记惰性结构：

```pfn
-- 惰性值
lazy val expensiveComputation = computeForHours()

-- 惰性列表（流）
type Stream a
  | Nil
  | Cons a (Lazy (Stream a))

-- 无限流
def naturalsFrom(n: Int) -> Stream Int =
  Cons(n, lazy naturalsFrom(n + 1))

def take(n: Int, s: Stream a) -> List a =
  match (n, s) with
  | (0, _) -> []
  | (_, Nil) -> []
  | (k, Cons x xs) -> x :: take(k - 1, force(xs))
```

### 严格性注解

```pfn
-- 标记参数必须严格求值
def foldl(f: a -> b -> a, init: !a, xs: List b) -> a =
  match xs with
  | [] -> init
  | x :: xs -> foldl(f, f(init, x), xs)
```

---

## 效果系统

Pfn 使用代数效果系统来追踪和管理副作用。

### 效果定义

```pfn
-- 定义效果
effect IO
  input : String -> IO String
  print : String -> IO ()
  readFile : String -> IO String
  writeFile : String -> String -> IO ()

effect State s
  get : State s s
  put : s -> State s ()

effect Throw e
  throw : e -> Throw e a
```

### 效果标注

```pfn
-- 函数的效果签名
def main : IO () = do
  name <- IO.input "Name: "
  IO.print ("Hello, " ++ name)

-- 多种效果
def processFile(path: String) : IO + Throw String String = do
  content <- IO.readFile(path)
  if isValid(content)
    then pure(process(content))
    else Throw.throw("Invalid content")
```

### 效果处理

```pfn
-- IO 处理器（运行时提供）
-- 用户定义的处理器

def runState(init: s, action: State s a) -> (a, s) =
  -- 内置的状态处理器实现
  ...

-- 使用
let (result, finalState) = runState(0, do
  current <- State.get
  State.put(current + 1)
  pure(current)
)
```

---

## 模块系统

### 模块定义

```pfn
-- src/Utils/List.pfn
module Utils.List

-- 导出列表
export head, tail, map, filter, foldl

-- 类型导出
export type List, Nil, Cons

-- 实现
def head(xs: List a) -> Option a = ...

def map(f: a -> b, xs: List a) -> List b = ...
```

### 模块导入

```pfn
-- 完整导入
import Utils.List

List.map(f, xs)

-- 选择性导入
import Utils.List (head, tail, map)

map(f, xs)

-- 别名
import Utils.List as L

L.map(f, xs)

-- 全部导入（不推荐）
import Utils.List exposing (..)
```

### 模块类型（签名）

```pfn
-- 定义模块接口
module type Monoid = sig
  type t
  val empty : t
  val append : t -> t -> t
end

-- 实现模块
module ListMonoid : Monoid where
  type t = List a
  def empty = []
  def append(xs, ys) = xs ++ ys
```

---

## 错误处理

### Result 类型

```pfn
type Result e a
  | Ok a
  | Error e

-- 使用
def divide(x: Float, y: Float) -> Result String Float =
  if y == 0.0
    then Error("division by zero")
    else Ok(x / y)

-- 链式处理
def safeCalc(a: Float, b: Float) -> Result String Float =
  divide(a, b)
    |> map(_.sqrt)
    |> mapError(_ => "calculation failed")
```

### Throw 效果

```pfn
def processFile(path: String) : IO + Throw String String = do
  content <- IO.readFile(path)
  if content == ""
    then Throw.throw("Empty file")
    else pure(content)

-- 捕获
def safeProcess(path: String) : IO String =
  try processFile(path) with
  | Throw.throw(msg) -> pure("Error: " ++ msg)
```

---

## 并发模型

### 协程

```pfn
effect Async
  spawn : Async a -> Async (Async a)
  await : Async a -> Async a

def concurrent(urls: List String) : Async (List String) = do
  tasks <- traverse(Async.spawn o fetch, urls)
  traverse(Async.await, tasks)
```

### 软件事务内存 (STM)

```pfn
effect STM
  readTVar : TVar a -> STM a
  writeTVar : TVar a -> a -> STM ()
  atomically : STM a -> IO a

def transfer(from: TVar Int, to: TVar Int, amount: Int) : STM () = do
  balance <- STM.readTVar(from)
  if balance < amount
    then Throw.throw("Insufficient funds")
    else do
      STM.writeTVar(from, balance - amount)
      currentTo <- STM.readTVar(to)
      STM.writeTVar(to, currentTo + amount)
```

---

## 与其他语言对比

| 特性 | Pfn | Haskell | OCaml | F# | Python |
|------|-----|---------|-------|-----|--------|
| 纯函数式 | ✓ | ✓ | 部分 | 部分 | ✗ |
| 类型推断 | 全局 | 全局 | 全局 | 全局 | 部分 |
| 效果系统 | 代数效果 | Monad | ✗ | ✗ | ✗ |
| 模式匹配 | ✓ | ✓ | ✓ | ✓ | 部分 |
| Python 互操作 | 原生 | ✗ | ✗ | ✗ | — |
| 编译目标 | Python | Native | Native | .NET | — |
| 学习曲线 | 中等 | 高 | 中等 | 中等 | 低 |
