# Pfn 类型系统

本文档详细描述 Pfn 的类型系统设计。

## 目录

1. [基础类型](#基础类型)
2. [类型推断](#类型推断)
3. [多态类型](#多态类型)
4. [类型类](#类型类)
5. [高级类型特性](#高级类型特性)
6. [渐进类型](#渐进类型)

---

## 基础类型

### 原始类型

```pfn
-- 整数类型
Int       -- 机器整数（与 Python int 兼容）
Int8      -- 8位整数
Int16     -- 16位整数
Int32     -- 32位整数
Int64     -- 64位整数
BigInt    -- 任意精度整数

-- 浮点类型
Float     -- 64位浮点（与 Python float 兼容）
Float32   -- 32位浮点

-- 其他原始类型
Bool      -- True | False
Char      -- Unicode 字符
String    -- Unicode 字符串

-- 单位类型
Unit      -- 空元组 ()
```

### 复合类型

```pfn
-- 函数类型
a -> b              -- 柯里化函数
(a, b) -> c         -- 多参数函数（语法糖，实际为 a -> b -> c）

-- 元组类型
(a, b)              -- 二元组
(a, b, c)           -- 三元组
()                  -- 单位类型

-- 列表类型
List a              -- 链表
[a]                 -- 语法糖

-- 记录类型
{ name: String, age: Int }  -- 匿名记录
Person              -- 命名记录类型

-- 可选类型
Option a            -- Some a | None
a?                  -- 语法糖
```

### 引用类型

```pfn
-- 引用（用于可变状态，受限使用）
Ref a               -- 可变引用

-- 延迟计算
Lazy a              -- 延迟求值的值

-- 计算类型
IO a                -- IO 计算
State s a           -- 状态计算
```

---

## 类型推断

Pfn 使用 Hindley-Milner 类型推断的扩展版本。

### 推断规则

**变量**:
```pfn
let x = 5           -- 推断为 Int
let y = x + 1       -- 推断为 Int
let f = fn x => x   -- 推断为 a -> a（多态）
```

**函数应用**:
```pfn
def id(x) = x
def f = fn x y => x

id(5)               -- Int
id(True)            -- Bool
f(1)(2)             -- Int
```

**Let 多态**:
```pfn
-- 多态绑定
let id = fn x => x
let a = id(1)       -- Int
let b = id(True)    -- Bool

-- 非多态（lambda 中的类型变量不泛化）
let f = fn g => (g(1), g(True))  -- 类型错误！
```

### 类型注解

```pfn
-- 显式类型注解
def add(x: Int, y: Int) -> Int = x + y

-- 部分注解
def map(f: a -> b, xs: List a) -> List b = ...

-- 类型变量需要显式绑定（在高阶场景）
def foo(f: forall a. a -> a) = (f(1), f("hi"))
```

### 推断算法

1. **生成约束**: 遍历 AST，生成类型约束
2. **统一**: 使用 union-find 算法求解约束
3. **泛化**: 在 let 绑定处泛化类型变量
4. **实例化**: 在使用处实例化多态类型

---

## 多态类型

### 参数多态

```pfn
-- 多态函数
def id(x: a) -> a = x

def fst(x: a, y: b) -> a = x

def map(f: a -> b, xs: List a) -> List b =
  match xs with
  | [] -> []
  | x :: xs -> f(x) :: map(f, xs)

-- 多态数据类型
type Pair a b = MkPair a b
type Tree a = Leaf a | Node (Tree a) (Tree a)
```

### Rank-N 类型

```pfn
-- Rank-1（普通多态）
def f(x: a) -> a = x

-- Rank-2
def g(h: forall a. a -> a) -> (Int, String) =
  (h(1), h("hello"))

-- Rank-3+
def k(h: forall a. (forall b. b -> b) -> a -> a) -> Int =
  h(fn x => x)(42)
```

### 存在类型

```pfn
-- 存在量化
type Showable = exists a. Show a => a

def makeShowable(x: a) -> Showable where Show a = pack x

def showIt(s: Showable) -> String =
  unpack (x, ev) = s in show(x) using ev
```

---

## 类型类

### 定义

```pfn
-- 基础类型类
interface Eq a where
  (==) : a -> a -> Bool
  (!=) : a -> a -> Bool  -- 默认实现
  (!=) x y = not(x == y)

-- 带方法约束的类型类
interface Ord a extends Eq a where
  compare : a -> a -> Ordering
  (<) : a -> a -> Bool
  (<) x y = compare(x, y) == LT

-- 多参数类型类
interface Convert a b where
  convert : a -> b

-- 函数依赖
interface Convert a b | a -> b where
  convert : a -> b
```

### 实现

```pfn
-- 为类型实现类型类
impl Eq Int where
  (==) x y = builtinIntEq(x, y)

impl Eq Bool where
  (==) True True = True
  (==) False False = True
  (==) _ _ = False

-- 条件实现
impl Eq a => Eq (List a) where
  (==) [] [] = True
  (==) (x :: xs) (y :: ys) = x == y && xs == ys
  (==) _ _ = False

-- 多参数实现
impl Convert Int Float where
  convert x = intToFloat(x)
```

### 标准类型类

```pfn
-- 基础
interface Eq a where (==) : a -> a -> Bool
interface Ord a extends Eq a where compare : a -> a -> Ordering
interface Show a where show : a -> String
interface Read a where read : String -> a

-- 数值
interface Num a where
  (+) : a -> a -> a
  (-) : a -> a -> a
  (*) : a -> a -> a
  zero : a

interface Fractional a extends Num a where
  (/) : a -> a -> a
  one : a

-- 函子相关
interface Functor f where
  map : (a -> b) -> f a -> f b

interface Applicative f extends Functor f where
  pure : a -> f a
  (<*>) : f (a -> b) -> f a -> f b

interface Monad m extends Applicative m where
  (>>=) : m a -> (a -> m b) -> m b

-- 折叠
interface Foldable t where
  foldl : (b -> a -> b) -> b -> t a -> b
  foldr : (a -> b -> b) -> b -> t a -> b
  length : t a -> Int

-- 遍历
interface Traversable t extends Functor t, Foldable t where
  traverse : Applicative f => (a -> f b) -> t a -> f (t b)
```

### 高阶类型 (Higher-Kinded Types)

```pfn
-- 类型构造器作为参数
interface Functor (f : * -> *) where
  map : (a -> b) -> f a -> f b

-- 使用
def sequence(m: Monad m, t: Traversable t) : t (m a) -> m (t a) =
  traverse(pure, t)
```

---

## 高级类型特性

### 类型族

```pfn
-- 开放类型族
type family Elem c

type instance Elem (List a) = a
type instance Elem (Set a) = a
type instance Elem String = Char

-- 封闭类型族
type family Flip t where
  Flip (a, b) = (b, a)
  Flip _ = Error
```

### 数据类型族

```pfn
-- 关联类型族
interface Container c where
  type Elem c
  empty : c
  insert : Elem c -> c -> c

-- GADT 实现类型级编程
data Nat = Zero | Succ Nat

type family Add (a: Nat) (b: Nat) : Nat where
  Add Zero n = n
  Add (Succ m) n = Succ (Add m n)
```

### 类型级别字面量

```pfn
-- 类型级别自然数
type Vec (n: Nat) a = ...

def head : Vec (Succ n) a -> a
def tail : Vec (Succ n) a -> Vec n a

-- 类型级别字符串
type Symbol = ...

type Field (s: Symbol) r = ...
```

### 依赖类型（有限支持）

```pfn
-- 单例类型
data SBool (b: Bool) where
  STrue : SBool True
  SFalse : SBool False

-- 索引类型
data Vec (n: Nat) a where
  VNil : Vec Zero a
  VCons : a -> Vec n a -> Vec (Succ n) a

def vhead : Vec (Succ n) a -> a
  | VCons x _ -> x

def vtail : Vec (Succ n) a -> Vec n a
  | VCons _ xs -> xs

-- 类型安全的 append
def vappend : Vec m a -> Vec n a -> Vec (Add m n) a
  | VNil, ys -> ys
  | VCons x xs, ys -> VCons x (vappend(xs, ys))
```

---

## 渐进类型

### 动态类型桥接

```pfn
-- Dynamic 类型
type Dynamic = exists a. TypeRep a => a

def toDyn : a -> Dynamic where Typeable a
def fromDyn : Dynamic -> Option a where Typeable a

-- 与 Python 交互
type PyAny = Dynamic  -- Python 的动态类型

def callPython(f: PyAny, args: List PyAny) -> PyAny
```

### 类型强制

```pfn
-- 安全转换
def safeCast(a -> b) : a -> Option b

-- 与 Python 交互时的类型强制
@py.coerce
def pyFunc(x: Int) -> String = ...  -- 允许运行时类型转换
```

### 模式类型（行多态）

```pfn
-- 行多态记录
type Row r = { | r }  -- 开放记录类型

def getName : { name: String | r } -> String
  | { name } -> name

-- 可以接受任何有 name 字段的记录
getName({ name: "Alice", age: 30 })  -- OK
getName({ name: "Bob" })             -- OK
getName({ age: 30 })                 -- 类型错误
```

---

## 类型错误消息

Pfn 致力于提供清晰的类型错误消息：

```pfn
-- 示例代码
def bad(x) =
  if x then "hello" else 42

-- 类型错误消息
┌─ example.pfn:2:3
│
2 │   if x then "hello" else 42
│   ^^^^^^^^^^^^^^^^^^^^^^^^^^^
│
│ Type mismatch in conditional:
│   Both branches must have the same type
│
│   Then branch: String
│   Else branch: Int
│
│ Suggestion: Make both branches return the same type:
│   if x then "hello" else "42"
```

---

## 类型系统扩展点

### 用户自定义类型检查器

```pfn
-- 契约系统（可选）
contract NonEmpty a where
  check : a -> Bool

def head(xs: List a) -> a requires NonEmpty xs =
  match xs with
  | x :: _ -> x
```

### 类型级别编程

```pfn
-- 类型级计算
type family Length (xs: [k]) : Nat where
  Length [] = Zero
  Length (_ :: xs) = Succ (Length xs)

-- 使用类型级计算进行编译时检查
def replicate : (n: Nat) -> a -> Vec n a
```
