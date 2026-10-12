# Gemini·星空猫娘（Gemini Starlight Neko）

> DeepSeek Harness Web GUI 的「Gemini 星空」主题皮肤：双子星图与星盘背景、科技蓝紫 UI 覆盖层、昼夜双形态猫耳立绘。

纯展示层客户端插件——`apply()` 设置 `data-dsh-gemini-skin` 作用域、按亮/暗主题自动切换背景与立绘、以独立透明层挂载角色形象。effect 销毁器还原全部 CSS/DOM 写入；不注入服务、不发出 Cordis 事件、不触达模型请求。

## 特性

- **昼夜双形态猫耳角色**：
  - **浅色模式（白天）**：挂载「星空全息猫耳魔法使」立绘，手托全息星图魔方，清新灵动。
  - **深色模式（夜晚）**：挂载「紫之星图猫耳少女」立绘，手持双子座星图古籍，微光闪烁。
- **全景双子星盘 × 星云背景**：
  - 右侧呈现天体星盘、双子座星位与旋转星系，左侧高透留白保障聊天气泡极佳可读性。
- **Gemini 科技蓝紫 UI 覆盖层**：
  - 极光紫（#7b68ee）× 薰衣草淡紫 × 晨曦晶白，DSH 原生 Token 全覆盖。
- **全息星芒 Favicon**：
  - 角色发饰同款全息四角星芒钻石徽标，随皮肤激活自动替换标签页图标。
- **科技折角侧栏装饰（gemini-corners）**。
- **完全离线单文件**：
  - 素材全内嵌（WebP / PNG data URI），单文件 `lib/client.js` 仅 ~1.28MB，零外部网络请求。

## 安装方式

### 方式一：DSH 第三方插件管理（本地离线导入）
1. 在 DSH 网页端进入「设置 → 第三方插件管理」。
2. 点击「离线导入」，选择生成的离线 zip 包 `dsh-skin-gemini-starlight-neko.zip`。
3. 重启 DSH 服务器后即可生效。

### 方式二：本地目录安装
```sh
dsh plugin --profile web add 'C:\Users\shxvx\.dsh\skin-src\dsh-skin-gemini'
```
安装后重启一次 DSH 服务器，在「设置 → 插件」确认启用。

## 目录结构

```text
dsh-skin-gemini/
├── package.json          # 插件元信息与 dsh.client 声明
├── skin.json             # 皮肤注册清单（皮肤管理器读取）
├── cordis.patch.yml      # 插件名册补丁
├── build_client.py       # 构建器（素材 WebP 化 + CSS 内联）
├── verify_assets.py      # 换图后自检（校验内联素材与 assets/ 一致）
├── gemini.css            # 皮肤核心样式表
├── lib/
│   ├── index.js          # Host 半部（空 apply 桩）
│   └── client.js         # 纯客户端单文件 Bundle
├── assets/               # 原始与处理后的素材资产
│   ├── bg-light.png      # 浅色背景画卷
│   ├── bg-dark.png       # 深色背景画卷
│   ├── bg-light.bak.png  # 浅色背景旧版备份（超宽横幅，未参与构建）
│   ├── bg-dark.bak.png   # 深色背景旧版备份（超宽横幅，未参与构建）
│   ├── character-light.png # 白天立绘（透明 RGBA）
│   ├── character-dark.png  # 夜间立绘（透明 RGBA）
│   └── favicon.png       # 星芒 Favicon
└── preview/              # 明暗预览图
    ├── light.webp
    └── dark.webp
```

## 更换背景/立绘

素材是**构建时内联**进 `lib/client.js` 的 data URI，因此换图 = 替换 `assets/` 下的同名文件 + 重新构建：

```sh
# 1) 用新图覆盖 assets/bg-light.png 或 assets/bg-dark.png（保持同名同扩展名）
# 2) 重新构建（需 Pillow）
& "C:\Users\shxvx\AppData\Local\Programs\Python\Python313\python.exe" build_client.py
# 3) 自检：内联尺寸是否与新图一致
& "C:\Users\shxvx\AppData\Local\Programs\Python\Python313\python.exe" verify_assets.py
# 4) 重启 DSH 服务器后生效
```

`build_client.py` 的 `REQUIRED_ASSETS` 固定读取 `bg-light.png` / `bg-dark.png` / `character-light.png` / `character-dark.png` / `favicon.png`；
若要换文件名，需同步修改该字典。背景由 CSS `var(--gemini-bg-art) right center / cover` 引用，建议新背景主体偏右、左侧留白以便聊天文本可读。
