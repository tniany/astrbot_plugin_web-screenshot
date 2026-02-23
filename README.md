# API网页截图插件

![GitHub release](https://img.shields.io/github/v/release/tniany/astrbot_plugin_web-screenshot)
![GitHub stars](https://img.shields.io/github/stars/tniany/astrbot_plugin_web-screenshot)
![GitHub forks](https://img.shields.io/github/forks/tniany/astrbot_plugin_web-screenshot)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/github/license/tniany/astrbot_plugin_web-screenshot)

基于外部API提供网页截图功能的AstrBot插件，适用于OneBot QQ机器人

## 🚀 功能介绍

- 📸 支持网页截图功能
- 🎨 支持自定义图片格式（png/webp）
- 📏 支持自定义视窗尺寸
- ⚡ 基于ScreenshotSnap API，响应速度快
- 📱 适用于OneBot QQ机器人平台
- 🔧 简单易用的命令行接口
- 📦 轻量级设计，无额外依赖

## 📥 安装方法

### 方法一：通过AstrBot插件市场安装
1. 打开AstrBot管理面板
2. 进入插件市场
3. 搜索"API网页截图"
4. 点击安装按钮

### 方法二：手动安装
1. 下载本插件的zip包
2. 解压到AstrBot的`data/plugins`目录
3. 重启AstrBot

## 📖 使用方法

### 基础用法
```bash
/截图 <url>
```

**示例：**
```bash
/截图 https://www.baidu.com
```

### 自定义格式和尺寸
```bash
/截图 <url> format=<format> width=<width> height=<height>
```

**参数说明：**
- `url`：要截图的网站URL（必需）
- `format`：图片格式，支持png（默认）和webp
- `width`：视窗宽度，范围100-3840（默认1920）
- `height`：视窗高度，范围100-2160（默认1080）

**示例：**
```bash
/截图 https://www.google.com format=webp width=1280 height=720
```

### 指令别名
插件支持以下指令别名：
- `/截图`
- `/网页截图`
- `/截图网页`

## 🔧 技术实现

- **API服务**：使用[ScreenshotSnap](https://screenshotsnap.com/zh)提供的免费截图API
- **开发语言**：Python 3.10+
- **依赖库**：httpx 0.27.0
- **兼容平台**：OneBot QQ机器人
- **代码结构**：模块化设计，易于维护和扩展

## 📁 项目结构

```
astrbot_plugin_web-screenshot/
├── main.py          # 插件核心实现
├── metadata.yaml    # 插件配置信息
├── requirements.txt # 依赖项声明
└── README.md        # 项目说明文档
```

## ❓ 常见问题

### 1. 截图失败怎么办？
- 检查URL是否正确
- 检查网络连接是否正常
- 网站可能对截图服务有限制

### 2. 截图速度慢怎么办？
- 截图速度取决于目标网站的加载速度
- 建议使用较小的尺寸以提高速度

### 3. 支持哪些网站？
- 支持大部分公开可访问的网站
- 不支持需要登录的网站
- 不支持需要验证码的网站

## ⚠️ 注意事项

- 本插件使用的是第三方免费API，可能存在请求限制
- 截图内容的版权归原网站所有，请合理使用
- 请勿滥用截图功能，避免对目标网站造成不必要的负担
- 插件仅用于学习和研究目的，请勿用于商业用途

## 📄 许可证

本插件采用MIT许可证开源

## 🤝 贡献

欢迎提交Issue和Pull Request来帮助改进这个插件！

1. Fork本仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个Pull Request

## 📞 作者信息

- **作者**：浅月tniay
- **GitHub**：[https://github.com/tniany/astrbot_plugin_web-screenshot](https://github.com/tniany/astrbot_plugin_web-screenshot)
- **反馈**：如有问题或建议，请在GitHub仓库提交Issue

## 📖 更新日志

### v1.2.2.1
- 修复插件导入失败问题
- 优化消息发送方式
- 更新API调用逻辑
- 美化代码结构和文档

## 🎯 鸣谢

- [AstrBot](https://astrbot.app/) - 强大的多平台聊天机器人框架
- [ScreenshotSnap](https://screenshotsnap.com/zh) - 免费的网站截图API服务

---

**使用说明：** 插件安装后，直接在QQ聊天中使用`/截图`指令即可开始使用网页截图功能。

** Enjoy! 🎉 **