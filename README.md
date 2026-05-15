# Junior AI Study 🎓

Junior AI Study（青少年 AI 学习助手）是一个旨在为青少年提供沉浸式、交互式个性化学习体验的全栈开源项目。项目集成了先进的大语言模型（LLM）能力，并通过创新的**流式语音合成**、**技能挂载驱动**以及**现代化的响应式 UI 设计**，打造了一个“懂教学、能发声、会总结”的数字 AI 教师。

## ✨ 核心特性

- **🧠 技能驱动学习 (Skill-Based Learning)**

  - 系统基于外部的 `yaml` 和 `Markdown` 文件定义不同的“学习技能”（如：中考英语阅读、文言文鉴赏等）。
  - 用户可以自主选择学习技能，AI 教师会自动加载对应的人设、约束和评估标准进行定向辅导。
  - 支持技能详情的富文本浮窗预览。
- **💬 极致流畅的对话体验**

  - **Server-Sent Events (SSE)**：支持 LLM 的毫秒级流式文本输出，无需漫长等待。
  - **智能缓存恢复**：对话状态自动同步至 `sessionStorage` 和 `localStorage`，刷新页面不丢失任何对话进度。
  - **Markdown 原生渲染**：对话内容完美支持代码块、表格、加粗等 Markdown 格式实时渲染。
- **🔊 实时流式语音播报 (Streaming TTS)**

  - 接入微软 `Edge-TTS` 神经网络语音，支持自然逼真的人声朗读。
  - **首创边写边读架构**：前端搭载定制的 `AudioQueuePlayer` (Web Audio API)，通过精准的标点符号（`。！？\n`）进行句读切分，AI 生成这句话的同时立刻合成并播放音频，告别传统的“等全段写完再读”的延迟感。
  - **硬件级播放控制**：提供独立的悬浮播控徽章，支持中途随时**暂停、继续与打断重开**，彻底解决多音频重叠（混音）问题。
- **📂 学习资料自动沉淀**

  - 聊天结束后，系统可根据对话内容自动提炼并生成持久化的 Markdown 格式学习档案（存入本地 `generated/` 目录），方便复习。
- **💅 现代化 UI 体验 (Modern UI/UX)**

  - 基于 CSS 网格与弹性盒的响应式布局，完美适配桌面与移动端屏幕。
  - 运用毛玻璃（Glassmorphism）、微渐变与 Lucide 图标集，提供堪比一流商业软件的视觉与交互反馈。

## 🛠️ 技术栈

### 后端 (Backend)

- **框架**：[FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
- **AI 编排**：LangChain, LangGraph
- **大模型通信**：`langchain_openai` (兼容 DeepSeek/OpenAI 格式接口)
- **语音引擎**：`edge-tts` (异步高性能文字转语音)
- **架构设计**：采用 Service 层单例模式，Lifespan 现代启动生命周期管理，严格的 Pydantic 数据验证。

### 前端 (Frontend)

- **框架**：[Vue 3](https://vuejs.org/) + [Vite](https://vitejs.dev/) + TypeScript
- **路由**：`vue-router` (单页路由，支持 `/`, `/history`, `/twin`)
- **状态管理**：原生 `provide/inject` 模式与 Web Storage API，轻量高效。
- **音频调度**：Web Audio API 自定义音频流调度引擎 (`AudioQueuePlayer`)。

## 🚀 快速启动

### 1. 后端环境配置
```bash
cd backend
cp .env.example .env  # 填写你的 API Key
pip install -r requirements.txt
python main.py
```

### 2. 前端环境配置
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

---

## 🐳 Docker 部署 (推荐)

项目已配置标准 Docker Compose 环境，可一键启动：

```bash
# 1. 确保已安装 Docker 和 Docker Compose
# 2. 配置 backend/.env 环境变量
# 3. 启动
docker-compose up -d --build
```
启动后：
- 前端访问：`http://localhost:8080`
- 后端访问：`http://localhost:8001`

---

## 🌐 Nginx 部署 (子路径挂载)

如果你想把项目挂载到子路径（如 `http://domain.com/junior/`），请参考以下步骤：

1.  **前端打包**：设置环境变量 `VITE_BASE_PATH=/junior/`
    ```bash
    cd frontend
    VITE_BASE_PATH=/junior/ npm run build
    ```
2.  **Nginx 配置**：参考 [nginx.conf.example](./nginx.conf.example)
    - 将 `location /` 改为 `location /junior/`。
    - 确保 `alias` 指向正确的 `dist` 目录。
    - API 转发建议统一使用 `location /api/` 或根据需要调整。

---

## 📁 目录结构
... (保持原样)

```text
junior-ai-study/
├── backend/                  # FastAPI 后端目录
│   ├── app/
│   │   ├── api/routes.py     # 核心路由 (聊天、文件、TTS、技能获取)
│   │   ├── services/         # 业务逻辑层 (LlmService, SkillService, TtsService)
│   │   └── schemas.py        # Pydantic 结构体
│   ├── skills/               # YAML 格式的 AI 技能定义文件夹
│   └── main.py               # 后端应用入口
│
└── frontend/                 # Vue 3 前端目录
    ├── src/
    │   ├── api.ts            # 后端通信接口封装
    │   ├── App.vue           # 全局状态管理与页面骨架
    │   ├── router.ts         # 前端路由配置
    │   ├── style.css         # 全局样式系统与 CSS 变量
    │   ├── utils/
    │   │   └── audioQueue.ts # 流式音频播放引擎
    │   ├── views/            # 路由视图 (AI老师、历史、数字孪生)
    │   └── components/       # 可复用组件 (Markdown渲染器等)
    └── package.json
```

## ⚠️ 注意事项与已知限制

- **TTS 网络请求**：Edge-TTS 依赖微软接口，如果在特定网络环境下遇到 404 或超时问题，请检查网络连通性。
- **本地缓存上限**：由于对话历史依赖浏览器的 `localStorage`，历史记录存储条数受限于浏览器的 5MB 配额（当前代码已做 `slice(0, 50)` 截断保护机制）。
## Linux 脚本启动与停止

仓库根目录已经新增两个脚本：

- [start_pm2.sh](/e:/my_project/git代码/junior-ai-study/start_pm2.sh)：启动前后端并显示 `pm2 status`
- [stop_pm2.sh](/e:/my_project/git代码/junior-ai-study/stop_pm2.sh)：停止并删除前后端 PM2 进程

### 使用方式

先赋予执行权限：

```bash
chmod +x start_pm2.sh stop_pm2.sh
```

启动前后端：

```bash
./start_pm2.sh
```

停止并删除前后端：

```bash
./stop_pm2.sh
```
