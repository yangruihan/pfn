# Pfn 示例项目

本目录包含使用 Pfn 语言编写的示例项目，展示语言的各种特性和应用场景。

## 目录结构

```
examples/
├── cli/           # 命令行工具示例
│   └── todo.pfn   # Todo 列表管理器
├── web/           # Web 应用示例
│   └── api.pfn    # REST API 服务器
├── data/          # 数据处理示例
│   └── analysis.pfn  # CSV 数据分析工具
├── hello.pfn      # Hello World 示例
└── typed.pfn      # 类型注解示例
```

## 示例说明

### 1. CLI 工具: Todo 列表管理器 (`cli/todo.pfn`)

一个功能完整的命令行 Todo 列表应用，展示:

- 命令行参数解析
- 文件 I/O 操作
- 状态管理
- 用户交互

运行方式:
```bash
pfn run examples/cli/todo.pfn
```

### 2. Web 应用: REST API 服务器 (`web/api.pfn`)

一个简单的 REST API 服务器，展示:

- Flask 集成
- HTTP 路由定义
- JSON 处理
- 错误处理

运行方式:
```bash
pfn run examples/web/api.pfn
# 访问 http://localhost:5000
```

### 3. 数据处理: CSV 分析工具 (`data/analysis.pfn`)

一个 CSV 数据分析工具，展示:

- Pandas 集成
- 数据清洗和转换
- 统计计算
- 命令行参数处理

运行方式:
```bash
pfn run examples/data/analysis.pfn data.csv --clean --output result.json
```

## 学习路径

1. **入门**: 从 `hello.pfn` 开始，了解基本语法
2. **类型系统**: 查看 `typed.pfn`，学习类型注解
3. **CLI 开发**: 研究 `cli/todo.pfn`，学习命令行工具开发
4. **Web 开发**: 学习 `web/api.pfn`，了解 Web 应用开发
5. **数据处理**: 探索 `data/analysis.pfn`，掌握数据处理技巧

## 更多资源

- [入门教程](../docs/tutorials/getting-started.md)
- [类型系统教程](../docs/tutorials/type-system-tutorial.md)
- [Python 互操作教程](../docs/tutorials/python-interop-tutorial.md)
- [标准库文档](../stdlib/)
