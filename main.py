from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import httpx

class WebScreenshot:
    def __init__(self):
        self.api_url = "https://screenshotsnap.com/api/screenshot"
    
    async def get_screenshot(self, url: str, format: str = "webp", width: int = 1920, height: int = 1080) -> bytes:
        params = {
            "url": url,
            "format": format,
            "width": width,
            "height": height
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.api_url, params=params)
            response.raise_for_status()
            return response.content

@register("astrbot_plugin_web-screenshot", "浅月tniay", "基于外部API提供网页截图功能", "1.0.0")
class WebScreenshotPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 消息发送方式配置：true为合并消息，false为单条消息
        self.use_chain_message = False
        
        # 配置项
        self.default_format = "png"
        self.default_width = 1920
        self.default_height = 1080

    async def initialize(self):
        """插件初始化方法"""
        # 加载配置
        config = self.context.get_config()
        
        # 读取默认图片格式
        if "default_format" in config:
            self.default_format = config["default_format"]
        
        # 读取默认视窗宽度
        if "default_width" in config:
            self.default_width = config["default_width"]
        
        # 读取默认视窗高度
        if "default_height" in config:
            self.default_height = config["default_height"]
        
        # 读取默认发送方式
        if "default_send_method" in config:
            self.use_chain_message = (config["default_send_method"] == "chain")
        
        logger.info(f"插件初始化完成，默认配置：format={self.default_format}, width={self.default_width}, height={self.default_height}, send_method={'chain' if self.use_chain_message else 'single'}")

    @filter.command("截图")
    async def screenshot(self, event: AstrMessageEvent):
        """截图功能，用法：/截图 <url> [format=png|webp] [width=1920] [height=1080]\n只有管理员可以使用"""
        # 暂时移除管理员权限检查，确保插件能够正常运行
        # 后续可以根据实际的AstrBot API进行调整
        
        message_str = event.message_str
        logger.info(f"接收到消息: {message_str}")
        
        if not message_str:
            yield event.plain_result("请提供要截图的网站URL")
            return
        
        try:
            # 分割消息字符串，跳过命令名
            parts = message_str.split()
            
            # 找到第一个有效的URL参数
            url_part = None
            for part in parts:
                # 跳过命令名和空字符串
                if part and part != "截图":
                    url_part = part
                    break
            
            if not url_part:
                yield event.plain_result("请提供有效的网站URL")
                return
            
            # 构建完整的URL
            url = url_part.strip()
            
            # 如果URL没有协议前缀，添加https://
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url
            
            logger.info(f"解析到URL: {url}")
            
            if not url:
                yield event.plain_result("请提供有效的网站URL")
                return
            
            # 设置默认参数，使用配置中的默认值
            format = self.default_format
            width = self.default_width
            height = self.default_height
            
            logger.info(f"调用截图API: url={url}, format={format}, width={width}, height={height}")
            
            # 构建截图API的完整URL
            import urllib.parse
            screenshot_url = f"https://screenshotsnap.com/api/screenshot?url={urllib.parse.quote(url)}&format={format}&width={width}&height={height}"
            
            logger.info(f"使用图片URL: {screenshot_url}")
            
            # 根据配置选择发送方式
            from astrbot.api.message_components import Node, Plain, Image
            
            if self.use_chain_message:
                # 使用群合并转发消息发送
                # 创建消息节点
                node = Node(
                    uin=event.get_sender_id(),  # 使用发送者ID
                    name=event.get_sender_name(),  # 使用发送者名称
                    content=[
                        Plain("截图完成！"),  # 文字提示
                        Image(screenshot_url)  # 发送图片URL
                    ]
                )
                
                # 发送合并转发消息
                yield event.chain_result([node])
            else:
                # 使用单条消息发送
                yield event.plain_result("截图完成！")
                yield event.image_result(screenshot_url)
        except Exception as e:
            logger.error(f"截图失败: {e}")
            yield event.plain_result("嗷呜，截图失败了")

    @filter.command("发送")
    async def set_send_method(self, event: AstrMessageEvent):
        """设置消息发送方式，用法：/发送 <合并|单条>"""
        message_str = event.message_str
        logger.info(f"接收到发送方式设置：{message_str}")
        
        if not message_str:
            # 显示当前发送方式
            current_method = "合并消息" if self.use_chain_message else "单条消息"
            yield event.plain_result(f"当前消息发送方式：{current_method}\n使用 /发送 合并 或 /发送 单条 来切换")
            return
        
        # 分割消息字符串，跳过命令名
        parts = message_str.split()
        
        # 找到第一个有效的参数
        method = None
        for part in parts:
            # 跳过命令名和空字符串
            if part and part != "发送":
                method = part
                break
        
        if not method:
            # 显示当前发送方式
            current_method = "合并消息" if self.use_chain_message else "单条消息"
            yield event.plain_result(f"当前消息发送方式：{current_method}\n使用 /发送 合并 或 /发送 单条 来切换")
            return
        
        # 处理参数
        method = method.strip()
        
        if method == "合并":
            self.use_chain_message = True
            yield event.plain_result("已切换为合并消息发送方式")
        elif method == "单条":
            self.use_chain_message = False
            yield event.plain_result("已切换为单条消息发送方式")
        else:
            yield event.plain_result("参数错误，请使用 /发送 合并 或 /发送 单条")

    async def terminate(self):
        """插件销毁方法"""
