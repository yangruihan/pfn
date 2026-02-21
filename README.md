# Pfn

**Pfn** (Pure Functional Native) 是一门纯函数式、静态类型、编译为 Python 的现代编程语言。

## 设计目标

- **纯函数式**: 不可变数据、引用透明、无副作用（通过效果系统控制）
- **现代化**: 强大的类型推断、代数数据类型、模式匹配、类型类
- **Python 生态无缝集成**: 直接使用 Python 库，双向互操作
- **高性能编译**: 编译为优化的 Python 代码，支持 AOT 和 JIT
- **自举**: 编译器最终使用 Pfn 自身编写

## 快速示例

```pfn
-- 基础函数定义
def add(x: Int, y: Int) -> Int = x + y

-- 代数数据类型
type Option a
  | Some a
  | None

type Result e a
  | Ok a
  | Error e

-- 模式匹配
def safeDiv(x: Float, y: Float) -> Result String Float =
  if y == 0.0
    then Error "division by zero"
    else Ok (x / y)

-- 类型类
interface Show a where
  show : a -> String

impl Show Int where
  show x = toString x

-- Python 互操作
import python math
import python numpy as np

def pythagorean(a: Float, b: Float) -> Float =
  math.sqrt(a * a + b * b)

-- IO 操作（效果系统）
effect IO
  input : String -> IO String
  print : String -> IO ()
  readFile : String -> IO String

def main : IO () = do
  name <- IO.input "What's your name? "
  IO.print ("Hello, " ++ name ++ "!")
```

## 核心特性

| 特性 | 描述 |
|------|------|
| 类型推断 | Hindley-Milner + 扩展，几乎不需要显式注解 |
| 代数数据类型 | Sum types, Product types, GADTs |
| 模式匹配 | 穷尽性检查，嵌套模式 |
| 类型类 | ad-hoc 多态，高阶类型 |
| 效果系统 | 追踪副作用，纯函数与 IO 分离 |
| 渐进类型 | 与 Python 互操作时可放宽类型检查 |
| 编译优化 | 惰性求值优化，尾递归优化，内联 |

## 文档目录

- [语言设计](docs/language-design.md) - 核心设计理念和语义
- [类型系统](docs/type-system.md) - 类型系统详细设计
- [Python 互操作](docs/python-interop.md) - 与 Python 的互操作机制
- [语法参考](docs/syntax-reference.md) - 完整语法说明
- [编译器架构](docs/compiler-architecture.md) - 编译器实现细节
- [开发路线图](docs/roadmap.md) - 开发计划和时间表
- [贡献指南](CONTRIBUTING.md) - 开发原则和贡献规范

## 项目结构

```
pfn/
├── docs/                    # 设计文档
├── src/
│   ├── parser/              # 解析器
│   ├── typechecker/         # 类型检查器
│   ├── infer/               # 类型推断
│   ├── effects/             # 效果系统
│   ├── ir/                  # 中间表示
│   ├── codegen/             # Python 代码生成
│   ├── runtime/             # 运行时库
│   └── cli/                 # 命令行工具
├── stdlib/                  # 标准库
├── examples/                # 示例代码
└── tests/                   # 测试套件
```

## 设计哲学

### 1. 渐进式采用

Pfn 可以与现有 Python 代码库共存：

```pfn
-- 导入 Python 模块
import python pandas as pd
import python flask

-- 导出给 Python 使用
@export
def processData(df: Py DataFrame) -> Py DataFrame =
  df.filter(row => row.age > 18)
```

### 2. 实用主义纯函数式

- 默认不可变，但提供性能优化提示
- 效果系统允许在需要时"打破"纯度
- 与 Python 互操作时自动处理可变性

### 3. 零运行时开销（尽可能）

- 编译为 Python 源码，无解释器
- 数据结构映射到 Python 原生类型
- 可选的运行时支持惰性求值

## 许可证

MIT License
