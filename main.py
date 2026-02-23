import httpx
import asyncio
from typing import Dict, Any, Optional
from astrbot.api.event import AstrMessageEvent, MessageEventResult
from astrbot.api.event.filter import command
import star

class WebScreenshotPlugin(star.Star):
    def __init__(self, context):
        super().__init__(context)
        self.api_url = "https://screenshotsnap.com/api/screenshot"
    
    @command("截图", aliases=["网页截图", "截图网页"])
    async def handle_screenshot(self, event: AstrMessageEvent) -> None:
        """基于外部API提供网页截图功能
        用法：/截图 <url> [format=<format>] [width=<width>] [height=<height>]
        参数说明：
        url：要截图的网站URL（必需）
        format：图片格式，支持png（默认）和webp
        width：视窗宽度，范围100-3840（默认1920）
        height：视窗高度，范围100-2160（默认1080）
        """
        args = event.get_message_str().strip()
        if not args:
            event.set_result(MessageEventResult().message("请提供要截图的网站URL"))
            return
        
        # 解析参数
        params = {
            "url": None,
            "format": "png",
            "width": 1920,
            "height": 1080
        }
        
        # 提取URL和其他参数
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
                params["url"] = part
                url_found = True
        
        if not params["url"]:
            event.set_result(MessageEventResult().message("请提供要截图的网站URL"))
            return
        
        # 构建API请求URL
        api_params = {
            "url": params["url"],
            "format": params["format"],
            "width": params["width"],
            "height": params["height"]
        }
        
        try:
            # 发送请求获取截图
            async with httpx.AsyncClient(timeout=30.0) as client:
                event.set_result(MessageEventResult().message("正在获取网页截图，请稍候..."))
                response = await client.get(self.api_url, params=api_params)
                response.raise_for_status()
                
                # 检查响应是否为图片
                if response.headers.get("content-type", "").startswith("image/"):
                    # 保存图片到临时文件
                    import tempfile
                    import os
                    
                    file_ext = params["format"]
                    with tempfile.NamedTemporaryFile(suffix=f".{file_ext}", delete=False) as f:
                        f.write(response.content)
                        temp_file = f.name
                    
                    try:
                        # 发送图片
                        event.set_result(MessageEventResult().message(
                            f"网页截图成功！\nURL: {params['url']}\n格式: {params['format']}\n尺寸: {params['width']}x{params['height']}\n\n"
                        ).file(temp_file))
                    finally:
                        # 清理临时文件
                        if os.path.exists(temp_file):
                            os.unlink(temp_file)
                else:
                    event.set_result(MessageEventResult().message("获取截图失败：返回内容不是图片"))
        
        except httpx.HTTPError as e:
            event.set_result(MessageEventResult().message(f"获取截图失败：网络错误 - {str(e)}"))
        except Exception as e:
            event.set_result(MessageEventResult().message(f"获取截图失败：{str(e)}"))

# 插件入口
def plugin_main(context):
    return WebScreenshotPlugin(context)