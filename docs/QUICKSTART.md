# 中国古典谋略经典知识库 - 企业版

[![内容质量检查](https://github.com/your-org/classical-strategy-db/actions/workflows/content-check.yml/badge.svg)](https://github.com/your-org/classical-strategy-db/actions/workflows/content-check.yml)
[![许可证：MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![版本](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/your-org/classical-strategy-db/releases)

企业级中国古典谋略经典知识库，提供系统化的古代智慧现代化应用解决方案。

## 🚀 快速开始

### 学习者
```bash
# 克隆仓库
git clone https://github.com/your-org/classical-strategy-db.git
cd classical-strategy-db

# 按照推荐路径学习
# 1. 三十六计 (入门)
# 2. 孙子兵法 (进阶)
# 3. 道德经 (深化)
# 4. 资治通鉴 (验证)
```

### 企业部署
```bash
# 方案 A：内部培训系统
git clone <repository-url> classical-strategy-db
# 集成到企业 LMS 学习管理系统

# 方案 B：质量验证
python scripts/validate-content.py
```

### 开发者
```bash
# 安装依赖（无）
# 运行测试
python scripts/validate-content.py

# 贡献内容
# 1. Fork 仓库
# 2. 创建分支 feature/new-article
# 3. 参考 templates/article-template.md 创建内容
# 4. 提交 Pull Request
```

## 📚 内容体系

| 模块 | 篇章数 | 难度 | 场景 |
|------|--------|------|------|
| 孙子兵法 | 13 篇 | ⭐⭐⭐⭐ | 战略规划、竞争分析 |
| 三十六计 | 6 套 36 计 | ⭐⭐ | 谈判技巧、危机处理 |
| 道德经 | 8 主题 | ⭐⭐⭐⭐⭐ | 领导力哲学、组织文化 |
| 资治通鉴 | 8 主题 | ⭐⭐⭐⭐ | 历史洞察、周期判断 |

## 🔧 工具脚本

| 脚本 | 用途 |
|------|------|
| `scripts/validate-content.py` | 内容质量验证（检查 Front Matter、章节结构、字数等） |
| `scripts/bulk-upgrade.py` | 批量升级内容到 v2.0 标准格式 |
| `templates/article-template.md` | 企业级标准文章模板 |

## 📋 质量标准

每篇文档必须包含：
- ✅ YAML Front Matter（title, book, chapter, tags, version 等 12 个字段）
- ✅ 一句话精髓（≤30 字）
- ✅ 核心思想分层解读（≥3 层）
- ✅ 现代案例深度解析（≥2 个）
- ✅ 可操作的行动指南
- ✅ 延伸思考与相关章节推荐

当前状态：**35/35 篇内容通过企业级质量验证** ✅

## 🤝 贡献

详见 [CONTRIBUTING.md](../CONTRIBUTING.md) 和 [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)。

## 📄 许可证

MIT License - 详见 [LICENSE](../LICENSE) 文件。

## 📞 联系

- 📧 Email: contact@classical-strategy.example.com
- 🌐 Website: https://classical-strategy.example.com

---

**让古代智慧赋能现代决策，打造企业级战略思维引擎。**
