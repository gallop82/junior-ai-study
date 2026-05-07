# 初中学习智能体计划

## 1. 项目目标

构建一个面向初中学习场景的 AI 智能体应用。

第一版只完成这个闭环：

```text
选择老师 -> 查看并选择 skills -> 提问 -> 智能体回答 -> 可选生成 Markdown 文件
```

技术栈：

- 后端：FastAPI + LangGraph
- 前端：Vue 3 + TypeScript + Vite
- 数据来源：后端本地 skills + 已有微信文章数据库
- 文件生成：Markdown

## 2. 已确认内容

- 智能体编排使用 LangGraph。
- 前端需要同时适配手机端和 PC 端。
- 微信公众号文章已有成熟数据库，后端对接现有数据库。
- skills 由你自己放在后端。
- 前端只展示 skills 列表、功能说明，并允许用户选择。
- 前端不提供新增、编辑、删除 skills 的功能。

## 3. 第一版功能范围

### 3.1 Skills

后端负责读取本地 skills。

前端展示：

- skill 名称
- skill 功能说明
- 适用学科
- 是否选中

对话时，前端只传 `skill_ids`，后端根据 `skill_ids` 加载完整 skill 内容。

建议目录：

```text
backend/app/data/skills/
```

建议 skill 文件格式：

```markdown
---
id: error_notebook
name: 错题本拆解
subject: math
description: 分析错题原因，生成复盘建议。
---

## 使用场景

学生需要整理错题、分析错因时使用。

## 回答规则

1. 先定位错因
2. 再给正确思路
3. 最后给巩固练习
```

### 3.2 老师问答

老师问答第一版保持简单。

用户选择一个老师后，可以向老师提问。老师回答时优先使用已接入的微信文章内容；如果用户选择了 `websearch` 相关 skill，也可以通过该 skill 查找外部内容。

第一版老师内容可以为空。

在微信公众号数据库正式接入前，老师只作为一个问答身份和前端展示入口存在。接入完成后，再通过老师 ID 关联真实公众号文章内容。

老师配置只保留必要字段：

- 老师 ID
- 老师名称
- 简短说明
- 关联公众号标识，可为空

建议目录：

```text
backend/app/data/teachers/
```

建议 teacher 文件格式：

```yaml
id: math_teacher_a
name: 林老师
description: 初中数学问答老师。
wechat_account_id:
```

### 3.3 微信文章数据库对接

后端增加文章检索服务。

职责：

- 根据老师关联的公众号账号查询文章
- 根据学生问题查询相关文章
- 将相关文章片段提供给 LangGraph 回答节点

建议模块：

```text
backend/app/repositories/wechat_article_repository.py
backend/app/services/article_retriever.py
```

微信公众号未接入前，该检索服务可以返回空结果。

如果用户选择了 `websearch` skill，智能体可以走 websearch skill 的规则查找内容。

第一版只做一种确定的微信文章检索方式，具体方式待确认。

### 3.4 LangGraph 流程

第一版 LangGraph 节点：

```text
start
  -> load_teacher
  -> load_skills
  -> retrieve_articles
  -> maybe_use_websearch_skill
  -> answer
  -> maybe_generate_file
end
```

节点职责：

- `load_teacher`：加载老师画像和风格规则
- `load_skills`：加载用户选择的 skills
- `retrieve_articles`：从微信文章数据库取相关材料；未接入时返回空
- `maybe_use_websearch_skill`：如果选择了 websearch skill，则按 skill 规则补充外部材料
- `answer`：生成面向初中生的回答
- `maybe_generate_file`：按用户选择生成 Markdown 文件

### 3.5 文件生成

第一版只生成 Markdown 文件。

文件类型：

- 错题本
- 学习计划
- 知识点讲义
- 作文修改稿
- 阅读理解答题模板

文件保存到后端本地目录。

建议目录：

```text
backend/generated/
```

### 3.6 前端

前端做一个响应式学习工作台。

PC 端布局：

```text
左侧：老师 + skills
中间：对话
右侧：生成文件
```

手机端布局：

```text
顶部：当前老师和操作入口
主体：对话
底部或抽屉：skills 和文件列表
```

第一版页面能力：

- 查看老师入口
- 选择老师提问
- 老师内容为空时显示“等待公众号内容接入”
- 查看 skills 列表
- 选择 skills
- 输入问题
- 查看回答
- 开关是否生成文件
- 查看生成文件列表

## 4. API 草案

```text
GET  /api/health
GET  /api/skills
GET  /api/teachers
POST /api/chat
GET  /api/generated-files
GET  /api/generated-files/{id}
```

`POST /api/chat` 请求示例：

```json
{
  "question": "帮我整理这道数学错题",
  "teacher_id": "math_teacher_a",
  "skill_ids": ["error_notebook"],
  "generate_file": true,
  "history": []
}
```

响应示例：

```json
{
  "answer": "...",
  "teacher": {},
  "used_skills": [],
  "articles": [],
  "files": []
}
```

## 5. 开发步骤

### Step 1: 确认技术细节

确认 LLM、数据库、skills 格式、teacher 格式、文件生成规则。

### Step 2: 搭建后端骨架

- FastAPI 项目结构
- 配置管理
- Pydantic schemas
- API 路由

### Step 3: 实现 skills 读取

- 读取后端本地 skill 文件
- 返回 skill 摘要列表
- chat 时加载完整 skill 内容

### Step 4: 实现老师配置读取

- 读取 teacher 配置
- 返回老师列表
- chat 时加载老师基础信息
- 老师未关联公众号内容时允许空材料回答

### Step 5: 对接微信文章数据库

- 实现数据库连接
- 实现文章检索
- 返回回答所需的文章片段
- 微信文章未接入前，检索结果允许为空

### Step 6: 实现 LangGraph

- 定义 state
- 实现 `load_teacher`
- 实现 `load_skills`
- 实现 `retrieve_articles`
- 实现 `maybe_use_websearch_skill`
- 实现 `answer`
- 实现 `maybe_generate_file`

### Step 7: 实现文件生成

- 生成 Markdown
- 保存文件
- 返回文件元数据
- 提供文件读取接口

### Step 8: 实现前端工作台

- PC 响应式布局
- 手机响应式布局
- 老师选择
- skills 展示和选择
- 对话交互
- 文件列表

### Step 9: 联调验证

- 验证后端 API
- 验证 LangGraph 流程
- 验证微信文章检索
- 验证前端手机端和 PC 端显示
- 验证 Markdown 文件生成

## 6. 当前需要确认

我们先按下面顺序确认。

### 6.1 LLM

需要确认：

- 使用哪家模型服务？
- 是否兼容 OpenAI API 格式？
- 是否有 `base_url`？
- 模型名称是什么？

### 6.2 微信文章数据库

需要确认：

- 数据库类型是什么？
- 后端如何连接？
- 文章表结构是什么？
- 是否已有 embedding？
- 是否已有知识点、学科、年级、公众号账号等标签？
- 第一版检索方式用关键词、标签、全文索引，还是向量检索？

### 6.3 Skills

需要确认：

- skill 文件使用 Markdown + frontmatter，还是 YAML/JSON？
- skill 是否按学科分类？
- skill 是否允许声明输出文件类型？

### 6.4 老师配置

需要确认：

- teacher 文件使用 YAML 还是 JSON？
- 老师和微信文章数据库如何关联？
- 老师初始为空时，前端展示文案怎么写？
- `websearch` 是否作为一个普通 skill 放在后端 skills 目录？

### 6.5 文件生成

需要确认：

- 第一版是否只生成 Markdown？
- 文件是否需要按老师、日期、学科分目录？
- 文件内容是否需要记录引用过的微信文章？

### 6.6 前端风格

需要确认：

- 整体风格偏学生端，还是教师工作台？
- PC 端是否固定三栏？
- 手机端 skills 和文件列表用抽屉还是 tab？

## 7. 当前约定

在以上细节确认前，不开始写项目代码。
