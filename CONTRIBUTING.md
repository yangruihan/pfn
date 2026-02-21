# Pfn 开发原则

本文档定义 Pfn 项目的核心开发原则。所有贡献者必须遵循这些原则。

---

## 核心原则

### 1. 自举优先 (Bootstrap-First)

**目标**: Pfn 编译器最终应使用 Pfn 自身编写。

**意义**:
- 证明语言的实用性
- 发现设计缺陷
- 建立最佳实践
- 增强可信度

**实施策略**:

```
阶段 1: Python 实现编译器
    │
    ▼
阶段 2: 编译器可以编译自身
    │
    ▼
阶段 3: 用 Pfn 重写编译器核心
    │
    ▼
阶段 4: 自举完成
```

**具体要求**:

1. **语言特性优先级**: 优先实现编译器需要用到的特性
   - 代数数据类型（AST 表示）
   - 模式匹配（解析树处理）
   - 高阶函数（编译 pass）
   - 效果系统（IO、错误处理）

2. **自举检查点**: 每个 Phase 结束时，评估自举可行性
   ```bash
   # 最终目标
   pfn compile src/pfn/compiler.pfn -o compiler.py
   ./compiler.py compile src/pfn/compiler.pfn -o compiler2.py
   diff compiler.py compiler2.py  # 应该相同
   ```

3. **最小依赖**: 编译器核心尽量少依赖外部库
   - 标准库可在自举后完善
   - Python 互操作作为 fallback

4. **自举里程碑**:
   - M3.5: 编译器能用 Pfn 语法编写（但用 Python 版编译）
   - M5: 核心编译器用 Pfn 重写
   - M7: 完全自举（M6 之后的下一个大版本）

---

### 2. 测试驱动开发 (Test-Driven Development)

**规则**: 所有代码必须有测试，测试先行。

**工作流程**:

```
1. 编写失败的测试
       │
       ▼
2. 编写最小代码使测试通过
       │
       ▼
3. 重构代码
       │
       ▼
4. 重复
```

**具体要求**:

1. **测试覆盖率**: 
   - 新代码覆盖率要求 > 90%
   - 总体覆盖率 > 80%
   - 关键路径（类型检查、代码生成）要求 100%

2. **测试类型**:
   ```python
   # 单元测试
   tests/unit/test_lexer.py
   tests/unit/test_parser.py
   tests/unit/test_typechecker.py
   
   # 集成测试
   tests/integration/test_compile.py
   
   # 端到端测试
   tests/e2e/test_programs.py
   
   # 自举测试（后期）
   tests/bootstrap/test_self_compile.py
   ```

3. **测试先行示例**:
   ```python
   # 错误: 先写实现
   def add(x, y):
       return x + y
   
   def test_add():
       assert add(1, 2) == 3
   
   # 正确: 先写测试
   def test_add_integers():
       assert add(1, 2) == 3
       
   def test_add_negatives():
       assert add(-1, -2) == -3
   
   # 然后实现
   def add(x: int, y: int) -> int:
       return x + y
   ```

4. **每个 PR 必须包含测试**:
   - 无测试的 PR 不予合并
   - CI 必须通过才能合并

5. **测试驱动开发语言特性**:
   ```pfn
   -- 先写期望的行为（测试）
   test "map preserves length" =
     assert(map(fn x => x, [1, 2, 3]).length == 3)
   
   test "map transforms elements" =
     assert(map(fn x => x * 2, [1, 2, 3]) == [2, 4, 6])
   
   -- 然后实现
   def map(f: a -> b, xs: List a) -> List b = ...
   ```

---

### 3. 特性分支开发 (Feature Branch Workflow)

**规则**: 所有开发在特性分支进行，单测全部通过后合并主干。

**工作流程**:

```
main (主干)
  │
  ├── feature/lexer-string-literals ──► PR ──► CI 通过 ──► 合并
  │
  ├── feature/type-inference ────────► PR ──► CI 通过 ──► 合并
  │
  └── bugfix/parser-error-recovery ──► PR ──► CI 通过 ──► 合并
```

**分支命名规范**:

```
feature/<功能描述>    # 新功能
bugfix/<问题描述>     # Bug 修复
refactor/<重构描述>   # 重构
docs/<文档描述>       # 文档更新
test/<测试描述>       # 测试相关
```

**示例**:
```bash
# 正确
feature/lexer-multiline-string
bugfix/type-inference-recursion
refactor/parser-error-messages

# 错误
fix-bug
update
my-feature
```

**合并条件 (必须全部满足)**:

| 条件 | 要求 |
|------|------|
| 单元测试 | 100% 通过 |
| 集成测试 | 100% 通过 |
| 测试覆盖率 | ≥ 新代码 90% |
| 类型检查 | mypy 无错误 |
| 代码风格 | ruff 无错误 |
| Code Review | 至少 1 人批准 |

**分支操作规范**:

```bash
# 1. 从最新主干创建分支
git checkout main
git pull origin main
git checkout -b feature/my-feature

# 2. 开发并提交（小步提交）
git add .
git commit -m "feat(scope): description"

# 3. 保持分支最新（rebase 优于 merge）
git fetch origin
git rebase origin/main

# 4. 推送并创建 PR
git push origin feature/my-feature
gh pr create

# 5. CI 通过后合并（squash and merge）
# 通过 GitHub UI 或命令行
```

**禁止事项**:

- ❌ 直接在 `main` 分支提交
- ❌ 跳过 PR 直接合并
- ❌ CI 未通过强制合并
- ❌ 无 Code Review 合并
- ❌ 合并冲突未解决

**CI 流水线**:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -e ".[dev]"
      
      - name: Run unit tests
        run: pytest tests/unit -v --cov=src/pfn --cov-fail-under=80
      
      - name: Run integration tests
        run: pytest tests/integration -v
      
      - name: Type check
        run: mypy src/pfn
      
      - name: Lint
        run: ruff check src/pfn
      
      # PR 状态检查：所有步骤通过才允许合并
```

**保护规则 (Branch Protection)**:

`main` 分支设置:
- [x] Require a pull request before merging
- [x] Require approvals (1)
- [x] Require status checks to pass before merging
  - test
  - type check
  - lint
- [x] Require branches to be up to date before merging
- [x] Do not allow bypassing the above settings

---

### 4. 原子提交 (Atomic Commits)

**规则**: 每完成一个任务提交一次，提交信息必须详细清晰。

**核心原则**:

1. **一个提交 = 一个逻辑变更**
   - ✅ 添加一个函数 + 它的测试
   - ✅ 修复一个 bug
   - ✅ 重命名一个变量（全局）
   - ❌ 添加功能 + 修复无关 bug + 重构代码

2. **小步提交，频繁提交**
   ```
   ❌ 一天结束后一次性提交所有更改
   
   ✅ 完成一个小任务就提交：
      - 写完测试 → 提交
      - 实现功能 → 提交
      - 重构代码 → 提交
      - 修复问题 → 提交
   ```

**提交信息格式**:

```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

**类型 (type)**:

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | feat(lexer): add multiline string support |
| `fix` | Bug 修复 | fix(typechecker): fix infinite loop in recursive types |
| `test` | 添加/修改测试 | test(parser): add tests for pattern matching |
| `refactor` | 重构（不改功能） | refactor(codegen): extract common helpers |
| `docs` | 文档更新 | docs(readme): add installation instructions |
| `style` | 代码格式（不改逻辑） | style: format with black |
| `perf` | 性能优化 | perf(infer): optimize constraint solving |
| `chore` | 杂项（构建、依赖） | chore: update dependencies |

**Scope 示例**:

```
lexer, parser, typechecker, infer, codegen, runtime, cli, docs, tests
```

**好的提交信息**:

```bash
# 功能添加
feat(lexer): add support for hexadecimal number literals

Add parsing for hex literals like 0xFF, 0xABCD.
Includes:
- Token type for hex literals
- Lexer rule for hex pattern
- Unit tests for valid and invalid hex literals

Closes #42

# Bug 修复
fix(typechecker): prevent infinite recursion in type unification

When unifying recursive types like `type T = T -> T`, the unifier
would enter an infinite loop. Now tracks visited types to detect
cycles early.

Fixes #128

# 测试
test(parser): add exhaustive tests for lambda expressions

Cover:
- Single param: fn x => x
- Multiple params: fn x y => x + y
- Type annotations: fn (x: Int) => x
- Nested lambdas: fn x => fn y => x + y
```

**不好的提交信息**:

```bash
# ❌ 太模糊
fix bug
update code
wip
asdfasdf

# ❌ 没说明为什么
change variable name

# ❌ 混合多个变更
add feature X, fix bug Y, and refactor Z

# ❌ 只有标题，没有细节（对于复杂变更）
feat(parser): add pattern matching
```

**提交检查清单**:

- [ ] 这是一个单一的逻辑变更吗？
- [ ] 提交信息清楚描述了"做了什么"和"为什么"吗？
- [ ] 相关的 Issue 被引用了吗？
- [ ] 代码能通过测试吗？
- [ ] 提交大小合理（< 400 行为宜）？

**工作流示例**:

```bash
# 实现一个新功能：字符串插值

# Step 1: 先写测试
git add tests/test_string_interpolation.py
git commit -m "test(lexer): add tests for string interpolation

Add test cases for:
- Simple interpolation: \"Hello {name}\"
- Expression interpolation: \"Sum: {a + b}\"
- Nested interpolation: \"User: {user.name}\"

These tests currently fail - implementing feature next."

# Step 2: 实现词法分析
git add src/pfn/lexer/string_interpolation.py
git commit -m "feat(lexer): implement string interpolation tokenization

Parse string interpolation syntax into tokens:
- Detect { } delimiters inside strings
- Handle escape sequences
- Generate INTERP_START, INTERP_END tokens

Tests for lexer now pass."

# Step 3: 实现语法分析
git add src/pfn/parser/expressions.py
git commit -m "feat(parser): parse string interpolation expressions

Build AST nodes for interpolated strings:
- InterpolatedString node with expression list
- StringLiteral and Expression parts
- Error handling for unmatched braces

All string interpolation tests now pass."

# Step 4: 代码生成
git add src/pfn/codegen/expressions.py
git commit -m "feat(codegen): generate Python f-strings from interpolation

Convert Pfn interpolated strings to Python f-strings:
- \"Hello {name}\" → f\"Hello {name}\"
- Handle nested expressions correctly

End-to-end tests for string interpolation pass."

# Step 5: 文档
git add docs/syntax-reference.md
git commit -m "docs(syntax): document string interpolation syntax

Add syntax reference for string interpolation:
- Basic syntax
- Expression support
- Escape sequences"
```

---

## 开发规范

### 提交规范

遵循上述原子提交原则和格式规范。

### PR 检查清单

- [ ] 新代码有对应测试
- [ ] 所有测试通过
- [ ] 覆盖率未下降
- [ ] 类型检查通过 (mypy)
- [ ] 代码风格检查通过 (ruff)
- [ ] 文档已更新（如适用）
- [ ] 自举可行性已评估（如适用）

### 代码审查重点

1. **测试质量**: 测试是否覆盖边界情况？
2. **自举影响**: 这个改动是否影响自举计划？
3. **测试驱动**: 测试是否在实现之前编写？

---

## 自举追踪

当前状态: **Phase 0 - Python 实现**

| 检查点 | 状态 | 备注 |
|--------|------|------|
| 词法分析器 | Python | 后期用 Pfn 重写 |
| 语法分析器 | Python | 后期用 Pfn 重写 |
| 类型检查器 | Python | 后期用 Pfn 重写 |
| 代码生成器 | Python | 后期用 Pfn 重写 |
| 运行时 | Python | 始终保留 Python 版本 |

**自举完成标准**:
- [ ] Pfn 编译器能用 Pfn 语法编写
- [ ] Pfn 版编译器能编译自身
- [ ] 两次编译结果二进制相同
- [ ] 所有测试在自举版本上通过

---

## 参考

- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)
- [Bootstrapping (compilers)](https://en.wikipedia.org/wiki/Bootstrapping_(compilers))
