<div align="center">
  <img src="[logo.png](https://youke.xn--y7xa690gmna.cn/s1/2026/02/24/699ca6d405401.webp)" width="120" height="120" alt="Web Screenshot">
  
  <h1>Web Screenshot 插件</h1>
  
  <p>
    <a href="https://github.com/tniany/astrbot_plugin_web-screenshot">
      <img src="https://img.shields.io/github/stars/tniany/astrbot_plugin_web-screenshot.svg?style=social" alt="GitHub Stars">
    </a>
    <a href="https://github.com/tniany/astrbot_plugin_web-screenshot">
      <img src="https://img.shields.io/github/forks/tniany/astrbot_plugin_web-screenshot.svg?style=social" alt="GitHub Forks">
    </a>
    <a href="https://github.com/tniany/astrbot_plugin_web-screenshot/blob/master/LICENSE">
      <img src="https://img.shields.io/github/license/tniany/astrbot_plugin_web-screenshot.svg" alt="License">
    </a>
  </p>
  
  <p>
    <strong>基于外部API提供网页截图功能的AstrBot插件，适用于OneBot QQ机器人</strong>
  </p>
  
  <p>
    <a href="#-功能特性">功能特性</a> •
    <a href="#-安装方法">安装方法</a> •
    <a href="#-插件配置">插件配置</a> •
    <a href="#-使用方法">使用方法</a> •
    <a href="#-示例">示例</a> •
    <a href="#-技术实现">技术实现</a>
  </p>
</div>

## 📋 功能特性

- ✅ 提供网页截图功能
- ✅ 支持自定义图片格式（png, webp）
- ✅ 支持自定义视窗尺寸
- ✅ 支持切换消息发送方式（合并消息/单条消息）
- ✅ 通过管理面板进行配置
- ✅ 友好的错误提示

## 🚀 安装方法

1. **将插件文件夹复制到AstrBot的插件目录**
2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```
3. **重启AstrBot**，插件会自动加载

## ⚙️ 插件配置

本插件支持通过AstrBot管理面板进行配置，配置项包括：

| 配置项 | 类型 | 默认值 | 说明 |
|-------|------|-------|------|
| default_format | string | png | 默认图片格式，可选值：png, webp |
| default_width | int | 1920 | 默认视窗宽度，范围100-3840 |
| default_height | int | 1080 | 默认视窗高度，范围100-2160 |
| default_send_method | string | single | 默认消息发送方式，可选值：chain（合并消息）, single（单条消息） |

配置文件路径：`_conf_schema.json`

## 📖 使用方法

### 1. 截图指令

#### 基础用法
```
/截图 <url>
```

#### 自定义格式和尺寸
```
/截图 <url> format=<format> width=<width> height=<height>
```

**参数说明**：
- `url`：要截图的网站URL（必需）
- `format`：图片格式，支持png（默认）和webp
- `width`：视窗宽度，范围100-3840（默认1920）
- `height`：视窗高度，范围100-2160（默认1080）

### 2. 发送方式切换

```
/发送 合并    # 切换为合并消息
/发送 单条    # 切换为单条消息
/发送         # 查看当前发送方式
```

## 🎯 示例

### 示例1：基础截图
```
/截图 baidu.com
```

### 示例2：带协议前缀的URL
```
/截图 https://www.baidu.com
```

### 示例3：自定义格式
```
/截图 baidu.com format=webp
```

### 示例4：自定义尺寸
```
/截图 baidu.com width=1280 height=720
```

## 🔧 技术实现

- **API调用**：使用 `https://screenshotsnap.com/api/screenshot` API 生成网页截图
- **消息发送**：支持两种发送方式
  - 合并消息：使用群合并转发消息发送结果
  - 单条消息：分别发送文字提示和图片
- **错误处理**：提供友好的错误提示信息

## 📝 注意事项

- 本插件使用第三方API进行截图，请确保机器人能够访问互联网
- 截图可能需要一定时间，取决于网站的加载速度
- 建议在配置中设置合适的默认值，以获得最佳体验

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个插件！

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👨‍💻 作者

**浅月tniay**

---

<div align="center">
  <p>如果这个插件对你有帮助，请给它一个 ⭐️ 吧！</p>
</div>

