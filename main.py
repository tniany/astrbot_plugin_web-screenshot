import httpx
import tempfile
import os
from typing import AsyncGenerator, Any
from urllib.parse import urlparse
from astrbot.api.event import AstrMessageEvent
from astrbot.api.event import filter
from astrbot.api.star import Star, register

@register(
    "astrbot_plugin_web-screenshot",
    "浅月tniay",
    "基于外部API提供网页截图功能的AstrBot插件，适用于OneBot QQ机器人",
    "v1.3.1"
)
class WebScreenshotPlugin(Star):
    """API网页截图插件"""
    
    def __init__(self, context):
        """初始化插件
        
        Args:
            context: AstrBot上下文对象
        """
        super().__init__(context)
        self.api_url = "https://screenshotsnap.com/api/screenshot"
    
    @filter.command("截图", aliases=["网页截图", "截图网页"])
    async def handle_screenshot(self, event: AstrMessageEvent) -> AsyncGenerator[Any, None]:
        """基于外部API提供网页截图功能
        用法：/截图 <url> [format=<format>] [width=<width>] [height=<height>]
        参数说明：
        url：要截图的网站URL（必需）
        format：图片格式，支持png（默认）和webp
        width：视窗宽度，范围100-3840（默认1920）
        height：视窗高度，范围100-2160（默认1080）
        """
        # 获取消息内容并移除命令部分
        full_message = event.get_message_str().strip()
        
        # 移除命令部分，只保留参数
        # 支持的命令：截图、网页截图、截图网页
        commands = ["截图", "网页截图", "截图网页"]
        args = full_message
        
        # 处理 / 前缀
        if args.startswith("/"):
            args = args[1:].strip()
        
        for cmd in commands:
            if args.startswith(cmd):
                args = args[len(cmd):].strip()
                break
        
        if not args:
            yield event.plain_result("请提供要截图的网站URL")
            return
        
        # 解析参数
        params = self._parse_params(args)
        
        # 验证URL
        if not self._validate_url(params["url"]):
            yield event.plain_result("请提供有效的网站URL")
            return
        
        try:
            # 发送请求获取截图
            yield event.plain_result("正在获取网页截图，请稍候...")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.api_url, params=params)
                response.raise_for_status()
                
                # 检查响应是否为图片
                if response.headers.get("content-type", "").startswith("image/"):
                    # 保存图片到临时文件
                    file_ext = params["format"]
                    temp_file = None
                    
                    try:
                        with tempfile.NamedTemporaryFile(suffix=f".{file_ext}", delete=False) as f:
                            f.write(response.content)
                            temp_file = f.name
                    
                        # 验证文件存在且有内容
                        if not temp_file or not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
                            yield event.plain_result("获取截图失败：图片文件无效")
                            return
                    
                        # 发送图片
                        image_message = event.image_result(temp_file)
                        yield image_message
                        yield event.plain_result(
                            f"网页截图成功！\nURL: {params['url']}\n格式: {params['format']}\n尺寸: {params['width']}x{params['height']}\n\n"
                        )
                    except Exception as e:
                        yield event.plain_result("发送图片失败，请稍后重试")
                    finally:
                        # 清理临时文件
                        if temp_file and os.path.exists(temp_file):
                            try:
                                os.unlink(temp_file)
                            except:
                                pass
                else:
                    yield event.plain_result("获取截图失败：返回内容不是图片")
        except httpx.HTTPError as e:
            yield event.plain_result("获取截图失败：网络连接异常，请检查网络后重试")
        except Exception as e:
            yield event.plain_result("获取截图失败，请稍后重试")
    
    def _parse_params(self, args: str) -> dict:
        """解析命令参数
        
        Args:
            args: 命令参数字符串
            
        Returns:
            dict: 解析后的参数
        """
        params = {
            "url": None,
            "format": "png",
            "width": 1920,
            "height": 1080
        }
        
        parts = args.split()
        url_found = False
        
        for part in parts:
            if "=" in part:
                key, value = part.split("=", 1)
                if key == "format" and value in ["png", "webp"]:
                    params["format"] = value
                elif key == "width":
                    try:
                        width = int(value)
                        if 100 <= width <= 3840:
                            params["width"] = width
                    except ValueError:
                        pass
                elif key == "height":
                    try:
                        height = int(value)
                        if 100 <= height <= 2160:
                            params["height"] = height
                    except ValueError:
                        pass
            elif not url_found:
                # 处理URL，移除特殊字符但不添加协议前缀
                url_candidate = part
                # 移除常见的特殊字符，如反引号、引号等
                url_candidate = url_candidate.strip('`'"'"'<>'"'"'[](){}')
                # 直接使用用户输入的URL格式，不添加协议前缀
                params["url"] = url_candidate
                url_found = True
        
        return params
    
    def _validate_url(self, url: str) -> bool:
        """验证URL的有效性
        
        Args:
            url: 要验证的URL
            
        Returns:
            bool: URL是否有效
        """
        if not url:
            return False
        
        # 检查URL长度
        if len(url) > 2048:
            return False
        
        # 简化验证，只要URL不为空且长度合理即可
        # 这样可以接受没有协议前缀的URL，如 baidu.com
        return True

# 插件入口
def plugin_main(context):
    """插件入口函数
    
    Args:
        context: AstrBot上下文对象
        
    Returns:
        WebScreenshotPlugin: 插件实例
    """
    return WebScreenshotPlugin(context)