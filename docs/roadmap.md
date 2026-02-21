# Pfn 开发路线图

本文档描述 Pfn 语言的开发计划和时间表。

## 核心开发原则

> 详细说明见 [CONTRIBUTING.md](../CONTRIBUTING.md)

### 1. 自举优先 (Bootstrap-First)

**终极目标**: Pfn 编译器使用 Pfn 自身编写。

```
Python 实现 → 编译自身 → Pfn 重写 → 自举完成
```

**自举里程碑**:
- M6.5: 编译器能用 Pfn 语法编写
- M7: 完全自举

### 2. 测试驱动开发 (TDD)

**规则**: 所有代码必须有测试，测试先行。

```
编写失败测试 → 最小实现 → 重构 → 重复
```

**要求**:
- 新代码覆盖率 > 90%
- 无测试的 PR 不予合并
- 每个功能模块有对应测试套件

### 3. 特性分支开发 (Feature Branch)

**规则**: 所有开发在特性分支进行，单测全部通过后合并主干。

```
feature/* → PR → CI 通过 → 合并 main
```

**合并条件**:
- ✅ 单元测试 100% 通过
- ✅ 集成测试 100% 通过
- ✅ 覆盖率 ≥ 90%
- ✅ 类型检查通过
- ✅ Code Review 通过

### 4. 原子提交 (Atomic Commits)

**规则**: 每完成一个任务提交一次，提交信息详细清晰。

```
一个提交 = 一个逻辑变更
小步提交，频繁提交
```

**提交格式**:
```
<type>(<scope>): <subject>

[body - 详细说明]
```

**示例**:
```
feat(lexer): add multiline string support

Add parsing for triple-quoted strings.
Includes token type, lexer rule, and unit tests.

Closes #42
```

---

## 总体时间线

| 阶段 | 时间 | 主要目标 |
|------|------|----------|
| Phase 0: 基础设施 | 第 1-2 周 | 项目结构、构建系统 |
| Phase 1: 核心编译器 | 第 3-8 周 | 词法分析、语法分析、基础类型检查 |
| Phase 2: 类型系统 | 第 9-14 周 | 完整类型推断、类型类 |
| Phase 3: Python 互操作 | 第 15-18 周 | Python 模块导入、类型映射 |
| Phase 4: 效果系统 | 第 19-22 周 | 效果推断、效果处理器 |
| Phase 5: 优化与工具 | 第 23-26 周 | 优化器、IDE 支持 |
| Phase 6: 标准库与生态 | 第 27-30 周 | 标准库、文档、示例 |
| **Phase 7: 自举** | **第 31-40 周** | **用 Pfn 重写编译器** |

---

## Phase 0: 基础设施 (第 1-2 周)

### 目标
建立项目基础设施和开发环境。

### 任务清单

- [ ] **项目结构**
  - 创建目录结构
  - 配置 pyproject.toml
  - 设置 CI/CD (GitHub Actions)

- [ ] **开发工具**
  - 配置 pytest 测试框架
  - 配置 mypy 类型检查
  - 配置 ruff/black 代码风格

- [ ] **文档系统**
  - 配置 MkDocs
  - 编写贡献指南
  - 编写开发指南

### 交付物
```
pfn/
├── src/pfn/
│   └── __init__.py
├── tests/
│   └── test_placeholder.py
├── docs/
│   └── index.md
├── pyproject.toml
├── .github/workflows/ci.yml
└── README.md
```

---

## Phase 1: 核心编译器 (第 3-8 周)

### 目标
实现词法分析器和语法分析器，能够解析基础 Pfn 代码。

### 第 3-4 周: 词法分析器

- [ ] **Token 定义**
  ```python
  # src/pfn/lexer/tokens.py
  class TokenType(Enum):
      INT, FLOAT, STRING, CHAR
      IDENT, KEYWORD
      OPERATOR, PUNCTUATION
      ...
  ```

- [ ] **Lexer 实现**
  ```python
  # src/pfn/lexer/lexer.py
  class Lexer:
      def tokenize(self, source: str) -> List[Token]
  ```

- [ ] **测试**
  ```python
  # tests/test_lexer.py
  def test_integers()
  def test_strings()
  def test_operators()
  def test_identifiers()
  ```

### 第 5-6 周: 语法分析器

- [ ] **AST 定义**
  ```python
  # src/pfn/parser/ast.py
  @dataclass
  class Module: ...
  @dataclass
  class DefDecl: ...
  @dataclass
  class Expr: ...
  ```

- [ ] **Parser 实现**
  ```python
  # src/pfn/parser/parser.py
  class Parser:
      def parse(self, tokens: List[Token]) -> Module
  ```

- [ ] **基础表达式解析**
  - 字面量
  - 变量引用
  - 函数应用
  - let 绑定
  - if-then-else
  - lambda

### 第 7-8 周: 基础代码生成

- [ ] **简单代码生成器**
  ```python
  # src/pfn/codegen/simple.py
  class SimpleCodegen:
      def generate(self, ast: AST) -> str
  ```

- [ ] **CLI 工具**
  ```python
  # src/pfn/cli.py
  def compile(source: str) -> str
  def run(source: str) -> None
  ```

- [ ] **端到端测试**
  ```pfn
  // examples/hello.pfn
  def main() = "Hello, World!"
  ```
  
  ```bash
  pfn run examples/hello.pfn
  # Hello, World!
  ```

### 交付物

- 能解析基础 Pfn 语法
- 能生成简单 Python 代码
- 能运行 "Hello World" 示例

---

## Phase 2: 类型系统 (第 9-14 周)

### 目标
实现完整的 Hindley-Milner 类型推断和类型类系统。

### 第 9-10 周: 类型系统基础

- [ ] **类型定义**
  ```python
  # src/pfn/types/types.py
  class Type: ...
  class TInt(Type): ...
  class TVar(Type): ...
  class TFun(Type): ...
  class TApp(Type): ...
  ```

- [ ] **类型环境**
  ```python
  # src/pfn/types/env.py
  class TypeEnv:
      def extend(self, name: str, scheme: TypeScheme)
      def lookup(self, name: str) -> TypeScheme
  ```

### 第 11-12 周: 类型推断

- [ ] **推断算法**
  ```python
  # src/pfn/typechecker/infer.py
  class TypeInferer:
      def infer(self, expr: Expr, env: TypeEnv) -> Type
      def unify(self, t1: Type, t2: Type) -> Subst
  ```

- [ ] **约束求解**
  ```python
  # src/pfn/typechecker/unify.py
  class Unifier:
      def solve(self, constraints: List[Constraint]) -> Subst
  ```

- [ ] **Let 多态**
  ```python
  def generalize(env: TypeEnv, t: Type) -> TypeScheme
  def instantiate(scheme: TypeScheme) -> Type
  ```

### 第 13-14 周: 类型类

- [ ] **类型类定义**
  ```python
  # src/pfn/typechecker/typeclass.py
  class TypeClass:
      name: str
      parameters: List[str]
      methods: Dict[str, Type]
      superclasses: List[TypeClass]
  ```

- [ ] **实例解析**
  ```python
  # src/pfn/typechecker/instances.py
  class InstanceResolver:
      def resolve(self, constraint: Constraint) -> Evidence
  ```

- [ ] **字典传递**
  ```python
  # 类型类方法调用转换为字典传递
  # show(x) -> show(x, dict[Show, Int])
  ```

### 交付物

- 完整的类型推断
- 支持类型类 (Eq, Ord, Show, Functor, Monad 等)
- 详细的类型错误消息

---

## Phase 3: Python 互操作 (第 15-18 周)

### 目标
实现与 Python 的双向互操作。

### 第 15-16 周: Python 模块导入

- [ ] **导入语法**
  ```pfn
  import python math
  import python numpy as np
  ```

- [ ] **类型映射**
  ```python
  # src/pfn/python/types.py
  PYTHON_TO_PFN = {
      'int': TInt(),
      'float': TFloat(),
      'str': TString(),
      'list': TList(),
      ...
  }
  ```

- [ ] **运行时导入**
  ```python
  # src/pfn/python/importer.py
  def import_module(name: str) -> PyModule
  ```

### 第 17-18 周: 数据类型映射

- [ ] **双向转换**
  ```python
  # src/pfn/python/convert.py
  def to_python(value: Any, type: Type) -> Any
  def from_python(value: Any, type: Type) -> Any
  ```

- [ ] **导出机制**
  ```pfn
  @py.export
  def myFunc(x: Int) -> Int = x + 1
  ```

### 交付物

- 能导入和使用 Python 标准库
- 能导入和使用第三方库 (numpy, pandas 等)
- 能导出 Pfn 函数给 Python 使用

---

## Phase 4: 效果系统 (第 19-22 周)

### 目标
实现代数效果系统。

### 第 19-20 周: 效果定义

- [ ] **效果语法**
  ```pfn
  effect IO
    input : String -> IO String
    print : String -> IO ()
  ```

- [ ] **效果推断**
  ```python
  # src/pfn/effects/infer.py
  class EffectInferer:
      def infer(self, expr: Expr) -> Effect
  ```

### 第 21-22 周: 效果处理

- [ ] **内置处理器**
  ```python
  # src/pfn/runtime/effects.py
  class IOHandler:
      def handle(self, op: str, args: List[Any]) -> Any
  ```

- [ ] **自定义处理器**
  ```pfn
  handler MyHandler =
    handle input(prompt) => "default"
  ```

### 交付物

- 完整的效果系统
- IO、State、Throw 等内置效果
- 自定义效果处理器

---

## Phase 5: 优化与工具 (第 23-26 周)

### 目标
实现优化器和开发工具。

### 第 23-24 周: 优化器

- [ ] **Core IR**
  ```python
  # src/pfn/ir/core.py
  class CoreExpr: ...
  ```

- [ ] **优化 Pass**
  ```python
  # src/pfn/optimizer/passes.py
  class Inlining: ...
  class ConstantFolding: ...
  class DeadCodeElimination: ...
  class TailCallOptimization: ...
  ```

### 第 25-26 周: 开发工具

- [ ] **REPL**
  ```python
  # src/pfn/repl.py
  class REPL:
      def run(self)
  ```

- [ ] **Language Server**
  ```python
  # src/pfn/lsp/
  # 实现部分 LSP 协议
  ```

- [ ] **VSCode 插件**
  - 语法高亮
  - 类型提示
  - 跳转到定义

### 交付物

- 基础优化器
- REPL 环境
- VSCode 插件 (基础版)

---

## Phase 6: 标准库与生态 (第 27-30 周)

### 目标
构建标准库和生态系统。

### 第 27-28 周: 标准库

- [ ] **核心模块**
  ```pfn
  // stdlib/Prelude.pfn
  // stdlib/List.pfn
  // stdlib/Option.pfn
  // stdlib/Result.pfn
  // stdlib/String.pfn
  // stdlib/Dict.pfn
  ```

### 第 29-30 周: 文档和示例

- [ ] **教程**
  - 入门教程
  - 类型系统教程
  - Python 互操作教程

- [ ] **示例项目**
  - CLI 工具
  - Web 应用
  - 数据处理

### 交付物

- 完整标准库
- 详细文档
- 示例项目

---

## Phase 7: 自举 (第 31-40 周)

### 目标
使用 Pfn 重写编译器，实现自举。

### 第 31-34 周: 编译器子集重写

- [ ] **用 Pfn 编写词法分析器**
  ```pfn
  // src/pfn/bootstrap/Lexer.pfn
  module Lexer
  
  def tokenize(source: String) -> List Token = ...
  ```

- [ ] **用 Pfn 编写语法分析器**
  ```pfn
  // src/pfn/bootstrap/Parser.pfn
  module Parser
  
  def parse(tokens: List Token) -> Module = ...
  ```

- [ ] **自举测试**
  ```python
  # tests/bootstrap/test_lexer_bootstrap.py
  def test_lexer_produces_same_output():
      py_lexer = PythonLexer()
      pfn_lexer = PfnLexer()  # 编译后的 Pfn 版本
      assert py_lexer.tokenize(source) == pfn_lexer.tokenize(source)
  ```

### 第 35-38 周: 完整编译器重写

- [ ] **用 Pfn 编写类型检查器**
  ```pfn
  // src/pfn/bootstrap/TypeChecker.pfn
  module TypeChecker
  
  def infer(expr: Expr, env: TypeEnv) -> Type = ...
  ```

- [ ] **用 Pfn 编写代码生成器**
  ```pfn
  // src/pfn/bootstrap/Codegen.pfn
  module Codegen
  
  def generate(core: CoreExpr) -> String = ...
  ```

### 第 39-40 周: 自举验证

- [ ] **自举测试**
  ```bash
  # 步骤 1: Python 版编译器编译 Pfn 版编译器
  python -m pfn compile src/pfn/bootstrap/Compiler.pfn -o compiler_v1.py
  
  # 步骤 2: Pfn 版编译器编译自身
  python compiler_v1.py compile src/pfn/bootstrap/Compiler.pfn -o compiler_v2.py
  
  # 步骤 3: 验证两次编译结果相同
  diff compiler_v1.py compiler_v2.py  # 应该相同
  ```

- [ ] **自举持续集成**
  ```yaml
  # .github/workflows/bootstrap.yml
  - name: Bootstrap Test
    run: |
      python -m pfn compile src/pfn/bootstrap/Compiler.pfn -o c1.py
      python c1.py compile src/pfn/bootstrap/Compiler.pfn -o c2.py
      diff c1.py c2.py
  ```

### 交付物

- 完整的 Pfn 版编译器
- 自举验证通过
- 所有测试在自举版本上通过

---

## 技术选型

### 编译器实现

| 组件 | 技术选型 | 理由 |
|------|----------|------|
| 语言 | Python 3.11+ | 与目标语言一致，便于互操作 |
| 解析器 | 手写递归下降 + Pratt | 可控性强，错误恢复容易 |
| 类型推断 | Union-Find | 标准 HM 算法 |
| AST | dataclasses | 简洁，类型安全 |
| 测试 | pytest | 标准选择 |

### 运行时

| 组件 | 技术选型 | 理由 |
|------|----------|------|
| 类型表示 | dataclasses | Python 原生支持 |
| 模式匹配 | match (Python 3.10+) | 原生支持 |
| 惰性求值 | 自定义 Lazy 类 | 简单可控 |

---

## 里程碑

| 里程碑 | 目标日期 | 标志 |
|--------|----------|------|
| M1: Hello World | 第 8 周末 | 能运行 hello.pfn |
| M2: 类型检查 | 第 14 周末 | 完整类型推断 |
| M3: Python 互操作 | 第 18 周末 | 能用 numpy |
| M4: 效果系统 | 第 22 周末 | IO 操作可用 |
| M5: 工具完善 | 第 26 周末 | REPL + VSCode |
| M6: Alpha 发布 | 第 30 周末 | 可用于实验 |
| **M7: 自举完成** | 第 40 周末 | 编译器自举 |

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 类型推断复杂度超预期 | 延期 | 先实现简化版本，逐步完善 |
| Python 互操作边界问题 | 功能受限 | 渐进类型，动态类型回退 |
| 效果系统实现困难 | 功能简化 | 可选效果追踪，默认放宽 |
| 性能不达标 | 可用性差 | 关键路径优化，C 扩展 |

---

## 贡献指南

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/yourorg/pfn.git
cd pfn

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 运行类型检查
mypy src/pfn
```

### 代码风格

- 使用 black 格式化
- 使用 ruff 检查
- 保持测试覆盖率 > 80%

### 提交规范

```
feat: 添加新功能
fix: 修复 bug
docs: 文档更新
refactor: 代码重构
test: 测试相关
```
