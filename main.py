from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from astrbot.api import logger
import urllib.parse
from astrbot.api.message_components import Node, Plain, Image

class WebScreenshotPlugin(Star):
    # API常量
    SCREENSHOT_API_URL = "https://screenshotsnap.com/api/screenshot"
    
    def __init__(self, context: Context):
        super().__init__(context)
        # 消息发送方式配置：true为合并消息，false为单条消息
        self.use_chain_message = False
        
        # 配置项
        self.default_format = "png"
        self.default_width = 1920
        self.default_height = 1080
        
        # 白名单
        self.whitelist = set()
        
        # 非白名单是否回复
        self.reply_non_whitelist = True

    async def initialize(self):
        """插件初始化方法"""
        # 加载配置
        config = self.context.get_config()
        
        # 读取配置（使用字典get方法简化代码）
        self.default_format = config.get("default_format", self.default_format)
        self.default_width = config.get("default_width", self.default_width)
        self.default_height = config.get("default_height", self.default_height)
        self.use_chain_message = (config.get("default_send_method") == "chain")
        self.reply_non_whitelist = config.get("reply_non_whitelist", self.reply_non_whitelist)
        
        # 读取白名单
        whitelist_config = config.get("whitelist", [])
        if whitelist_config:
            self.whitelist = set(map(str, whitelist_config))
            logger.info(f"从配置加载白名单：{self.whitelist}")
        
        logger.info(f"插件初始化完成，默认配置：format={self.default_format}, width={self.default_width}, height={self.default_height}, send_method={'chain' if self.use_chain_message else 'single'}, reply_non_whitelist={self.reply_non_whitelist}")

    @filter.command("截图")
    async def screenshot(self, event: AstrMessageEvent, url: str, img_format: str = None, width: int = None, height: int = None):
        """截图功能，用法：/截图 <url> [format=png|webp] [width=1920] [height=1080]\n只有白名单用户可以使用"""
        # 获取发送者ID
        sender_id = str(event.get_sender_id())
        
        # 检查是否为管理员（管理员默认拥有权限）
        is_admin = False
        try:
            if hasattr(self.context, 'is_admin'):
                is_admin = await self.context.is_admin(event.get_sender_id())
        except Exception as e:
            logger.warning(f"管理员权限检查失败: {e}")
        
        # 检查是否在白名单中或是否为管理员
        if sender_id not in self.whitelist and not is_admin:
            # 根据配置决定是否回复
            if self.reply_non_whitelist:
                yield event.plain_result("权限不足，只有白名单用户可以使用此命令")
            return
        
        logger.info(f"接收到截图请求: url={url}, format={img_format}, width={width}, height={height}")
        
        # 使用默认值（如果参数未提供）
        img_format = img_format or self.default_format
        width = width or self.default_width
        height = height or self.default_height
        
        # 验证参数
        if img_format not in ["png", "webp"]:
            yield event.plain_result("图片格式错误，支持的格式：png, webp")
            return
        
        if width <= 0 or height <= 0:
            yield event.plain_result("宽度和高度必须大于0")
            return
        
        try:
            # 构建完整的URL
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            
            logger.info(f"解析到URL: {url}")
            
            # 构建截图API的完整URL（使用urlencode简化代码）
            params = {
                "url": url,
                "format": img_format,
                "width": width,
                "height": height
            }
            screenshot_url = f"{self.SCREENSHOT_API_URL}?{urllib.parse.urlencode(params)}"
            
            logger.info(f"使用图片URL: {screenshot_url}")
            
            # 根据配置选择发送方式
            if self.use_chain_message:
                # 使用群合并转发消息发送
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
    async def set_send_method(self, event: AstrMessageEvent, method: str = None):
        """设置消息发送方式，用法：/发送 <合并|单条>"""
        if method is None:
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

    @filter.command("jtwl")
    async def manage_whitelist(self, event: AstrMessageEvent, qq: str = None):
        """管理白名单，用法：/jtwl <qq号> 添加白名单"""
        # 检查是否为管理员
        try:
            if hasattr(self.context, 'is_admin'):
                if not await self.context.is_admin(event.get_sender_id()):
                    yield event.plain_result("权限不足，只有管理员可以管理白名单")
                    return
        except Exception as e:
            logger.warning(f"管理员权限检查失败: {e}")
            yield event.plain_result("权限检查失败，无法管理白名单")
            return
        
        if qq is None:
            # 显示当前白名单
            if self.whitelist:
                whitelist_str = "\n".join(self.whitelist)
                yield event.plain_result(f"当前白名单：\n{whitelist_str}")
            else:
                yield event.plain_result("当前白名单为空")
            return
        
        # 处理参数
        qq = qq.strip()
        
        # 验证QQ号格式
        if not qq.isdigit():
            yield event.plain_result("QQ号格式错误，请输入数字")
            return
        
        # 添加到白名单
        self.whitelist.add(qq)
        logger.info(f"管理员添加QQ {qq} 到白名单")
        yield event.plain_result(f"已添加QQ {qq} 到白名单")

    async def terminate(self):
        """插件销毁方法"""
        logger.info("插件已销毁")
