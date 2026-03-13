# 贡献指南

感谢你愿意参与这个项目。

## 提交前建议

1. 先阅读 [README.md](README.md) 了解项目结构
2. 如修改接口行为，请同步更新文档
3. 如修改知识入库逻辑，请确认 `scripts/ingest.py` 与 `server.py` 的数据格式保持一致
4. 提交前至少运行一次基础语法检查

推荐执行：

```bash
python -m py_compile server.py scripts/ingest.py scripts/interactive_client.py scripts/load_test.py scripts/test_server.py scripts/verify_update.py
```

## 分支与提交建议

- 每个功能或修复尽量单独提交
- 提交信息尽量清晰说明目的
- 避免把 `.env`、生成产物或临时调试文件提交到仓库

## Pull Request 建议

PR 描述建议包含以下内容：

- 改动目的
- 主要改动点
- 是否影响接口或知识库格式
- 验证方式

## 文档要求

以下情况请同步更新文档：

- 修改接口结构
- 修改部署方式
- 修改知识库结构
- 修改 Java 迁移相关逻辑
