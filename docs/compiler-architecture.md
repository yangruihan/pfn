# Pfn 编译器架构

本文档详细描述 Pfn 编译器的技术架构和实现细节。

## 目录

1. [编译流程概览](#编译流程概览)
2. [编译器组件](#编译器组件)
3. [中间表示](#中间表示)
4. [类型检查](#类型检查)
5. [代码生成](#代码生成)
6. [运行时系统](#运行时系统)
7. [错误处理](#错误处理)

---

## 编译流程概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Pfn 编译流程                                │
└─────────────────────────────────────────────────────────────────────┘

  源代码 (.pfn)
       │
       ▼
  ┌─────────┐
  │  Lexer  │ ──────────────────────────────────────────┐
  └─────────┘                                          │
       │                                               │
       ▼                                               │
  ┌─────────┐                                          │
  │ Parser  │                                          │ 错误处理
  └─────────┘                                          │
       │                                               │
       ▼                                               │
  ┌──────────────┐                                     │
  │    AST       │                                     │
  └──────────────┘                                     │
       │                                               │
       ▼                                               │
  ┌──────────────┐                                     │
  │  Renamer     │ ──── 解析名称、作用域               │
  └──────────────┘                                     │
       │                                               │
       ▼                                               │
  ┌──────────────┐                                     │
  │ Type Checker │ ──── 类型推断、约束求解             │
  └──────────────┘                                     │
       │                                               │
       ▼                                               │
  ┌──────────────┐                                     │
  │  Effect      │ ──── 效果推断、效果检查             │
  │  Checker     │                                     │
  └──────────────┘                                     │
       │                                               │
       ▼                                               │
  ┌──────────────┐                                     │
  │  Desugar     │ ──── 语法糖展开                     │
  └──────────────┘                                     │
       │                                               │
       ▼                                               │
  ┌──────────────┐                                     │
  │  Core IR     │ ──── 核心 IR (简化 AST)             │
  └──────────────┘                                     │
       │                                               │
       ▼                                               │
  ┌──────────────┐                                     │
  │  Optimizer   │ ──── 优化 pass                      │
  └──────────────┘                                     │
       │                                               │
       ▼                                               │
  ┌──────────────┐                                     │
  │  Code Gen    │ ──── Python 代码生成                │
  └──────────────┘                                     │
       │                                               │
       ▼                                               │
  ┌──────────────┐                                     │
  │ Python AST   │                                     │
  └──────────────┘                                     │
       │                                               │
       ▼                                               │
  ┌──────────────┐                                     │
  │ Python Code  │ ──── 源代码 或 字节码               │
  └──────────────┘                                     │
       │                                               │
       ▼
  可执行 Python 模块
```

---

## 编译器组件

### 1. 词法分析器 (Lexer)

**职责**: 将源代码转换为 Token 流

**实现**:
- 基于 Python 实现
- 支持缩进敏感语法（可选）
- Unicode 支持

```python
# Token 类型
class Token:
    type: TokenType
    value: Any
    span: Span  # 位置信息

# 主要 Token 类型
enum TokenType:
    # 字面量
    INT, FLOAT, STRING, CHAR, BOOL
    
    # 标识符和关键字
    IDENT, KW_DEF, KW_LET, KW_IF, ...
    
    # 操作符
    PLUS, MINUS, ARROW, PIPE, ...
    
    # 分隔符
    LPAREN, RPAREN, LBRACE, RBRACE, ...
    
    # 特殊
    INDENT, DEDENT, NEWLINE, EOF
```

### 2. 语法分析器 (Parser)

**职责**: 将 Token 流转换为 AST

**实现**:
- 递归下降解析器
- Pratt 解析器（用于表达式）
- 错误恢复机制

```python
# AST 节点类型
@dataclass
class Module:
    declarations: List[Declaration]

@dataclass
class DefDecl:
    name: str
    params: List[Param]
    return_type: Optional[Type]
    body: Expr
    span: Span

@dataclass
class TypeDecl:
    name: str
    constructors: List[Constructor]
    span: Span

@dataclass
class Expr:
    ...

@dataclass
class IfExpr:
    cond: Expr
    then_branch: Expr
    else_branch: Expr
    span: Span

@dataclass
class MatchExpr:
    scrutinee: Expr
    cases: List[MatchCase]
    span: Span

@dataclass
class LambdaExpr:
    params: List[Param]
    body: Expr
    span: Span
```

### 3. 重命名器 (Renamer)

**职责**: 解析名称、建立作用域

```python
class Renamer:
    def rename(self, ast: AST) -> AST:
        # 1. 收集所有顶层定义
        # 2. 解析导入
        # 3. 为每个绑定生成唯一符号
        # 4. 解析所有引用
```

### 4. 类型检查器 (Type Checker)

**职责**: 类型推断和类型检查

**实现**:
- Hindley-Milner 类型推断
- Union-Find 约束求解
- 类型类解析

```python
class TypeChecker:
    def check(self, ast: AST) -> TypedAST:
        # 1. 生成类型约束
        # 2. 求解约束
        # 3. 泛化 let 绑定
        # 4. 注入类型信息
        
    def infer(self, expr: Expr) -> Type:
        # 类型推断主算法
```

### 5. 效果检查器 (Effect Checker)

**职责**: 推断和检查效果

```python
class EffectChecker:
    def check(self, ast: TypedAST) -> TypedAST:
        # 1. 收集效果约束
        # 2. 推断效果
        # 3. 验证效果一致性
```

### 6. 去语法糖 (Desugar)

**职责**: 展开语法糖，简化 AST

```python
class Desugarer:
    def desugar(self, ast: TypedAST) -> CoreExpr:
        # 列表推导式 -> map/filter
        # do 记法 -> bind 应用
        # if-then-else -> match
        # 运算符 -> 函数调用
        # 模式匹配 -> case 表达式
```

### 7. 优化器 (Optimizer)

**职责**: 优化中间表示

```python
class Optimizer:
    passes = [
        Inlining(),           # 函数内联
        ConstantFolding(),    # 常量折叠
        DeadCodeElimination(),# 死代码消除
        BetaReduction(),      # Beta 归约
        TailCallOptimization(),# 尾递归优化
        Specialization(),     # 特化
    ]
```

---

## 中间表示

### Core IR

简化的核心语言，用于优化和代码生成：

```python
# Core 表达式
@dataclass
class CoreExpr:
    ...

@dataclass
class Var:
    name: str
    type: Type

@dataclass
class Lit:
    value: Any
    type: Type

@dataclass
class App:
    func: CoreExpr
    arg: CoreExpr
    type: Type

@dataclass
class Lam:
    param: str
    param_type: Type
    body: CoreExpr
    type: Type

@dataclass
class Let:
    name: str
    value: CoreExpr
    body: CoreExpr
    type: Type

@dataclass
class Case:
    scrutinee: CoreExpr
    alts: List[Alt]
    type: Type

@dataclass
class Alt:
    pattern: Pattern
    body: CoreExpr
```

### ANF (A-Normal Form)

用于代码生成的规范化形式：

```python
# 所有中间值都被命名
# x = f(y)
# z = g(x)
# h(z)
```

---

## 类型检查

### 类型推断算法

```python
class TypeInferer:
    # 类型变量
    def fresh_var(self) -> TypeVar:
        return TypeVar(f"t{self.counter.next()}")
    
    # 统一
    def unify(self, t1: Type, t2: Type) -> Subst:
        # t1 = Int, t2 = Int => {}
        # t1 = a, t2 = Int => {a: Int}
        # t1 = a, t2 = b => {a: b}
        # t1 = a -> b, t2 = Int -> c => {a: Int, b: c}
        
    # 实例化
    def instantiate(self, scheme: TypeScheme) -> Type:
        # forall a. a -> a => t1 -> t1
        
    # 泛化
    def generalize(self, env: Env, t: Type) -> TypeScheme:
        # 环境中没有的自由变量被泛化
```

### 类型类解析

```python
class TypeClassResolver:
    def resolve(self, constraint: Constraint) -> Evidence:
        # Eq Int => 内置实现
        # Eq (List a) => 需要 Eq a
        # Eq a => 使用传入的字典
```

---

## 代码生成

### Python AST 生成

```python
class CodeGenerator:
    def generate(self, core: CoreExpr) -> py.AST:
        # 生成 Python AST
        
    def gen_expr(self, expr: CoreExpr) -> py.expr:
        match expr:
            case Var(name, _):
                return py.Name(name)
            case Lit(value, type):
                return self.gen_lit(value, type)
            case App(func, arg, _):
                return py.Call(self.gen_expr(func), [self.gen_expr(arg)])
            case Lam(param, _, body, _):
                return py.Lambda([param], self.gen_expr(body))
            ...
```

### 示例转换

**Pfn 源码**:
```pfn
def add(x: Int, y: Int) -> Int = x + y

def double(x: Int) -> Int = add(x, x)
```

**生成的 Python**:
```python
# 编译时类型检查通过
# 运行时无类型检查

def add(x, y):
    return x + y

def double(x):
    return add(x, x)
```

**代数数据类型**:
```pfn
type Option a
  | Some a
  | None

def map(f, opt) =
  match opt with
  | Some x -> Some(f(x))
  | None -> None
```

**生成的 Python**:
```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar('T')

@dataclass
class Some(Generic[T]):
    value: T

class None_:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

None_ = None_()  # 单例

Option = Union[Some[T], None_]

def map(f, opt):
    if isinstance(opt, Some):
        return Some(f(opt.value))
    else:
        return None_
```

**模式匹配**:
```pfn
match x with
| 0 -> "zero"
| n if n < 0 -> "negative"
| _ -> "positive"
```

**生成的 Python**:
```python
# 使用 match (Python 3.10+) 或 if-elif 链

# Python 3.10+
match x:
    case 0:
        result = "zero"
    case n if n < 0:
        result = "negative"
    case _:
        result = "positive"

# 兼容版本
if x == 0:
    result = "zero"
elif x < 0:
    result = "negative"
else:
    result = "positive"
```

### 尾递归优化

```pfn
-- 尾递归
def factorial(n: Int, acc: Int = 1) -> Int =
  if n <= 1
    then acc
    else factorial(n - 1, n * acc)
```

**生成的 Python**:
```python
def factorial(n, acc=1):
    while True:  # 尾递归转换为循环
        if n <= 1:
            return acc
        n, acc = n - 1, n * acc
```

---

## 运行时系统

### 运行时库结构

```
pfn/runtime/
├── __init__.py
├── core.py          # 核心类型和函数
├── types.py         # 内置类型实现
├── effects.py       # 效果处理器
├── pattern.py       # 模式匹配辅助
├── python_compat.py # Python 互操作
└── utils.py         # 工具函数
```

### 核心运行时

```python
# runtime/core.py

# 惰性值
class Lazy:
    def __init__(self, thunk):
        self._thunk = thunk
        self._value = None
        self._computed = False
    
    def force(self):
        if not self._computed:
            self._value = self._thunk()
            self._computed = True
        return self._value

# 函数工具
def curry(f, n):
    """柯里化 n 参数函数"""
    if n <= 1:
        return f
    return lambda x: curry(lambda *args: f(x, *args), n - 1)

# 模式匹配辅助
def match(value, *cases):
    for pattern, result in cases:
        bindings = try_match(pattern, value)
        if bindings is not None:
            return result(**bindings)
    raise MatchError(f"No pattern matched for {value}")
```

### 效果处理器

```python
# runtime/effects.py

class IO:
    """IO 效果处理器"""
    
    @staticmethod
    def input(prompt: str) -> str:
        return input(prompt)
    
    @staticmethod
    def print(s: str) -> None:
        print(s, end='')
    
    @staticmethod
    def readFile(path: str) -> str:
        with open(path) as f:
            return f.read()

class State:
    """State 效果处理器"""
    
    def __init__(self, init):
        self.value = init
    
    def get(self):
        return self.value
    
    def put(self, value):
        self.value = value
```

---

## 错误处理

### 错误类型

```python
class PfnError(Exception):
    span: Span
    message: str
    hints: List[str]

class LexError(PfnError):
    ...

class ParseError(PfnError):
    ...

class TypeError(PfnError):
    ...

class EffectError(PfnError):
    ...
```

### 错误消息格式

```
error[T001]: Type mismatch in function application
  ┌─ src/main.pfn:10:5
  │
10│   add(1, "hello")
  │       ^^^^^^^^^ expected Int, found String
  │
  = note: function 'add' expects arguments of type (Int, Int)
  = help: consider converting the string to an integer: parseInt("hello")
```

### 错误恢复

```python
class Parser:
    def synchronize(self):
        """错误恢复：跳到下一个同步点"""
        while not self.check(EOF):
            if self.previous().type == NEWLINE:
                return
            if self.check(KW_DEF, KW_LET, KW_TYPE):
                return
            self.advance()
```

---

## 构建系统

### 项目结构

```
pfn/
├── src/
│   ├── pfn/                  # 编译器源码
│   │   ├── lexer/
│   │   ├── parser/
│   │   ├── typechecker/
│   │   ├── effects/
│   │   ├── optimizer/
│   │   └── codegen/
│   └── runtime/              # 运行时库
├── stdlib/                   # 标准库
├── tests/                    # 测试
├── docs/                     # 文档
├── pyproject.toml           # 项目配置
└── setup.py                 # 安装配置
```

### 构建命令

```bash
# 安装开发版本
pip install -e .

# 运行测试
pytest tests/

# 构建文档
mkdocs serve

# 编译 Pfn 文件
pfn compile input.pfn -o output.py

# 运行 Pfn 文件
pfn run main.pfn

# REPL
pfn repl
```

---

## 调试支持

### Source Map

```python
class SourceMap:
    """维护 Pfn 源码到生成 Python 代码的映射"""
    
    mappings: List[Mapping]
    
    def lookup_python_line(self, py_line: int) -> PfnLocation:
        """查找 Python 行对应的 Pfn 位置"""
```

### 调试信息

生成的 Python 代码包含注释，标注源 Pfn 位置：

```python
# line 10: def add(x, y) = x + y
def add(x, y):
    return x + y
```
