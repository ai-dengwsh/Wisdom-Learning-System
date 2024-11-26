# 智慧学习系统 (Wisdom Learning System)

一个基于人工智能的自适应编程学习系统，帮助用户更高效地学习编程知识。

## 功能特点

- 🎯 智能题目推荐
  - 基于用户能力水平动态调整题目难度
  - 考虑用户的学习进度和疲劳度
  - 个性化的学习路径规划

- 📚 丰富的题库资源
  - 自动抓取最新题目
  - 多样的题目类型和难度等级
  - 详细的解题思路和最佳实践

- 🎓 自适应学习路径
  - 定制化的学习计划
  - 进度追踪和数据分析
  - 实时调整学习策略

- 📊 学习数据分析
  - 详细的学习统计
  - 能力水平评估
  - 学习效果可视化

## 技术栈

- 后端：
  - Python 3.8+
  - Flask
  - SQLAlchemy
  - Playwright

- 前端：
  - HTML5
  - TailwindCSS
  - JavaScript

- 数据库：
  - SQLite

## 快速开始

1. 克隆项目
```bash
git clone https://github.com/ai-dengwsh/Wisdom-Learning-System.git
cd Wisdom-Learning-System
```

2. 安装依赖
```bash
pip install -r requirements.txt
playwright install
```

3. 初始化数据库
```bash
python init_db.py
```

4. 运行项目
```bash
python run.py
```

5. 访问系统
打开浏览器访问 http://localhost:5000

## 项目结构

```
Wisdom-Learning-System/
├── app.py                 # Flask应用主文件
├── models.py             # 数据模型定义
├── services.py           # 业务逻辑服务
├── education_spider.py   # 爬虫模块
├── templates/            # 前端模板
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── ...
├── static/              # 静态资源
├── tests/               # 测试文件
└── requirements.txt     # 项目依赖
```

## 主要功能模块

### 1. 用户管理
- 用户注册和登录
- 个人信息管理
- 学习进度追踪

### 2. 题目管理
- 自动题目抓取
- 题目分类和标签
- 难度等级划分

### 3. 学习路径
- 自定义学习计划
- 进度追踪
- 阶段性目标设置

### 4. 数据分析
- 学习时间统计
- 正确率分析
- 能力水平评估

## 开发计划

- [x] 基础功能实现
- [x] 用户系统开发
- [x] 题目爬虫模块
- [x] 学习路径功能
- [ ] 代码评测系统
- [ ] AI辅导功能
- [ ] 移动端适配
- [ ] 社区互动功能

## 贡献指南

1. Fork 本仓库
2. 创建新的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情 
