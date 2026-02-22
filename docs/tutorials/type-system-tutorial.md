# Pfn 类型系统教程

本教程深入介绍 Pfn 的类型系统，包括类型推断、类型类和高级类型特性。

## 目录

1. [类型推断基础](#类型推断基础)
2. [代数数据类型](#代数数据类型)
3. [类型类](#类型类)
4. [多态类型](#多态类型)
5. [高级类型特性](#高级类型特性)
6. [类型错误调试](#类型错误调试)

---

## 类型推断基础

### Hindley-Milner 类型推断

Pfn 使用 Hindley-Milner 算法进行类型推断，大多数情况下不需要显式类型注解:

```pfn
-- 编译器自动推断类型
def add(x, y) = x + y
-- 推断为: add : Num a => a -> a -> a

def double(x) = x * 2
-- 推断为: double : Num a => a -> a

def first(pair) =
  match pair with
    (x, _) -> x
-- 推断为: first : (a, b) -> a
```

### 类型注解

虽然类型推断很强大，但有时需要显式注解:

```pfn
-- 消除歧义
def parse(s: String) -> Int = ...

-- 文档目的
def process(data: List User) -> Result Error Report = ...

-- 约束类型
def specificAdd(x: Int, y: Int) -> Int = x + y
```

### Let 多态

```pfn
-- let 绑定是多态的
let id x = x
in (id 1, id "hello")  -- OK: (Int, String)

-- lambda 参数不是多态的
fn f => (f 1, f "hello")  -- 类型错误!
```

---

## 代数数据类型

### Sum Types (和类型)

Sum types 表示"或"关系:

```pfn
-- 简单枚举
type Direction
  | North
  | South
  | East
  | West

-- 带数据的变体
type Shape
  | Circle Float           -- 半径
  | Rectangle Float Float  -- 宽度, 高度
  | Triangle Float Float Float  -- 三边

-- 使用
def area(shape: Shape) -> Float =
  match shape with
    Circle r -> 3.14159 * r * r
    Rectangle w h -> w * h
    Triangle a b c ->
      let s = (a + b + c) / 2
      in sqrt(s * (s - a) * (s - b) * (s - c))
```

### Product Types (积类型)

Product types 表示"和"关系:

```pfn
-- 记录类型
type Person = {
  name: String,
  age: Int,
  address: Address
}

-- 元组类型
type Point = (Float, Float)
type Triple a = (a, a, a)

-- 使用
let person = { name: "Alice", age: 30, address: ... }
let point = (1.0, 2.0)
```

### 递归类型

```pfn
-- 链表
type List a
  | Nil
  | Cons a (List a)

-- 二叉树
type Tree a
  | Leaf
  | Node a (Tree a) (Tree a)

-- 表达式 AST
type Expr
  | Lit Int
  | Var String
  | Add Expr Expr
  | Mul Expr Expr
  | Let String Expr Expr

-- 求值
def eval(env: Dict String Int, expr: Expr) -> Int =
  match expr with
    Lit n -> n
    Var x -> Dict.getOrElse x 0 env
    Add e1 e2 -> eval(env, e1) + eval(env, e2)
    Mul e1 e2 -> eval(env, e1) * eval(env, e2)
    Let x e body ->
      let v = eval(env, e)
      in eval(Dict.insert x v env, body)
```

### GADTs (广义代数数据类型)

GADTs 允许更精确的类型约束:

```pfn
-- 类型安全的表达式
type Expr a where
  Lit : Int -> Expr Int
  BoolLit : Bool -> Expr Bool
  Add : Expr Int -> Expr Int -> Expr Int
  If : Expr Bool -> Expr a -> Expr a -> Expr a

-- 类型安全的求值
def eval : Expr a -> a
  | Lit n -> n
  | BoolLit b -> b
  | Add e1 e2 -> eval(e1) + eval(e2)
  | If cond then_ else_ ->
      if eval(cond) then eval(then_) else eval(else_)
```

---

## 类型类

### 定义类型类

```pfn
-- 基本类型类
interface Show a where
  show : a -> String

interface Eq a where
  eq : a -> a -> Bool
  neq : a -> a -> Bool

-- 带默认实现
interface Eq a where
  eq : a -> a -> Bool
  neq x y = not (eq x y)
```

### 实现类型类

```pfn
-- 为 Int 实现 Show
impl Show Int where
  show x = toString x

-- 为 Bool 实现 Eq
impl Eq Bool where
  eq True True = True
  eq False False = True
  eq _ _ = False

-- 为自定义类型实现
type Color = Red | Green | Blue

impl Show Color where
  show Red = "Red"
  show Green = "Green"
  show Blue = "Blue"

impl Eq Color where
  eq Red Red = True
  eq Green Green = True
  eq Blue Blue = True
  eq _ _ = False
```

### 标准类型类

```pfn
-- Eq: 相等比较
interface Eq a where
  (==) : a -> a -> Bool
  (!=) : a -> a -> Bool

-- Ord: 有序比较
interface Eq a => Ord a where
  compare : a -> a -> Ordering
  (<) : a -> a -> Bool
  (<=) : a -> a -> Bool
  (>) : a -> a -> Bool
  (>=) : a -> a -> Bool
  min : a -> a -> a
  max : a -> a -> a

-- Show: 字符串表示
interface Show a where
  show : a -> String

-- Functor: 映射
interface Functor f where
  map : (a -> b) -> f a -> f b

-- Applicative: 应用
interface Functor f => Applicative f where
  pure : a -> f a
  (<*>) : f (a -> b) -> f a -> f b

-- Monad: 绑定
interface Applicative m => Monad m where
  (>>=) : m a -> (a -> m b) -> m b
  join : m (m a) -> m a
```

### 类型类约束

```pfn
-- 函数约束
def sort(xs: List a) -> List a where Ord a = ...

def showAll(xs: List a) -> String where Show a =
  join ", " (map show xs)

-- 多重约束
def sortAndShow(xs: List a) -> String where (Ord a, Show a) =
  showAll(sort(xs))
```

### 类型类继承

```pfn
-- Ord 继承 Eq
interface Eq a => Ord a where
  compare : a -> a -> Ordering

-- Num 继承 Show 和 Eq
interface (Show a, Eq a) => Num a where
  (+) : a -> a -> a
  (-) : a -> a -> a
  (*) : a -> a -> a
  (/) : a -> a -> a
  negate : a -> a
```

---

## 多态类型

### 参数多态

```pfn
-- 完全多态
def id(x: a) -> a = x

def const(x: a, y: b) -> a = x

def flip(f: a -> b -> c) -> b -> a -> c =
  fn x y => f y x
```

### 约束多态

```pfn
-- 带类型类约束
def max(x: a, y: a) -> a where Ord a =
  if x > y then x else y

def sum(xs: List a) -> a where Num a =
  foldl (+) 0 xs
```

### 高阶类型

```pfn
-- 类型构造器作为参数
def mapM(m: Monad m, f: a -> m b, xs: List a) -> m (List b) =
  match xs with
    [] -> pure []
    x :: xs ->
      f x >>= fn y =>
        mapM(m, f, xs) >>= fn ys =>
          pure (y :: ys)
```

### 存在类型

```pfn
-- 隐藏具体类型
type Showable = exists a. Show a => a

def showAny(s: Showable) -> String = show(s)

let things: List Showable = [1, "hello", True]
map showAny things  -- ["1", "hello", "True"]
```

---

## 高级类型特性

### 行多态

```pfn
-- 记录行多态
def getName(r: { name: String | rest }) -> String = r.name

let alice = { name: "Alice", age: 30 }
let bob = { name: "Bob", email: "bob@example.com" }

getName(alice)  -- "Alice"
getName(bob)    -- "Bob"
```

### Rank-N Types

```pfn
-- Rank-2 类型
def runST(action: forall s. ST s a) -> a = ...

-- Rank-3 类型
def foo(f: (forall a. a -> a) -> Int) -> Int = ...
```

### 类型族

```pfn
-- 关联类型
interface Container c where
  type Elem c
  empty : c
  insert : Elem c -> c -> c
  member : Elem c -> c -> Bool

impl Container (List a) where
  type Elem (List a) = a
  empty = []
  insert x xs = x :: xs
  member x xs = elem x xs
```

### 约束种类

```pfn
-- 类型约束
type NonEmpty a = { xs: List a | length xs > 0 }

def head(xs: NonEmpty a) -> a =
  match xs with
    x :: _ -> x

-- 编译时验证
head([1, 2, 3])  -- OK
head([])         -- 编译错误!
```

---

## 类型错误调试

### 常见类型错误

#### 类型不匹配

```
错误: 类型不匹配
  期望: Int
  实际: String
  在表达式: x + 1
  其中 x : String
```

解决方法: 检查变量类型，确保操作数类型一致。

#### 无法推断类型

```
错误: 无法推断类型变量 a
  在表达式: []
  需要更多类型信息
```

解决方法: 添加类型注解 `[] : List Int`。

#### 类型类约束不满足

```
错误: 类型 Int 不满足约束 Show
  在表达式: show x
```

解决方法: 为该类型实现相应的类型类。

### 调试技巧

1. **添加类型注解**: 在关键位置添加类型注解帮助编译器
2. **拆分表达式**: 将复杂表达式拆分为多个 let 绑定
3. **检查类型签名**: 确保函数类型签名正确
4. **使用 REPL**: 在 REPL 中测试表达式的类型

```pfn
-- 在 REPL 中
> :t map
map : (a -> b) -> List a -> List b

> :t [1, 2, 3]
[1, 2, 3] : List Int

> :t fn x => x + 1
fn x => x + 1 : Num a => a -> a
```

---

## 练习

1. 定义一个 `BinaryTree a` 类型并实现 `map` 函数
2. 为自定义类型实现 `Show` 和 `Eq` 类型类
3. 使用 GADT 定义一个类型安全的 DSL
4. 实现一个使用行多态的记录操作函数

---

## 下一步

- 学习 [Python 互操作](./python-interop-tutorial.md)
- 查看 [标准库源码](../../stdlib/) 了解类型系统的实际应用
- 阅读 [类型系统设计文档](../type-system.md) 了解实现细节
