import httpx
import tempfile
import os
import asyncio
from typing import AsyncGenerator, Any
from urllib.parse import urlparse
from astrbot.api.event import AstrMessageEvent
from astrbot.api.event import filter
from astrbot.api.star import Star, register
from astrbot.api import logger
from astrbot.api import AstrBotConfig

@register(
    "astrbot_plugin_web-screenshot",
    "浅月tniay",
    "基于外部API提供网页截图功能的AstrBot插件，适用于OneBot QQ机器人",
    "v1.3.2"
)
class WebScreenshotPlugin(Star):
    """API网页截图插件
    
    基于外部API提供网页截图功能的AstrBot插件，适用于OneBot QQ机器人
    支持指定URL、图片格式、视窗宽度和高度
    """
    
    # 常量定义
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 最大文件大小限制（10MB）
    CHUNK_SIZE = 8192  # 下载分块大小（8KB）
    RETRY_COUNT = 2  # 网络请求重试次数
    RETRY_DELAY = 1  # 重试延迟（秒）
    
    def __init__(self, context, config: AstrBotConfig):
        """初始化插件
        
        Args:
            context: AstrBot上下文对象
            config: 插件配置
        """
        super().__init__(context)
        self.api_url = "https://screenshotsnap.com/api/screenshot"
        self.config = config
        self.pure_mode = config.get("pure_mode", False)
        command_alias = config.get("command_alias", "")
        if command_alias:
            self.command_alias = [command_alias]
        else:
            self.command_alias = []
    
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
        raw_message = event.get_message_str().strip()
        
        if self.command_alias and any(raw_message.startswith(f"/{alias}") for alias in self.command_alias):
            for alias in self.command_alias:
                if raw_message.startswith(f"/{alias}"):
                    args = raw_message[len(f"/{alias}"):].strip()
                    break
        else:
            args = self._parse_command(raw_message)
        
        if not args:
            yield event.plain_result("请提供要截图的网站URL")
            return
        
        params, errors = self._parse_params(args)
        if errors:
            for error in errors:
                yield event.plain_result(f"参数错误：{error}")
            return
        
        # 验证URL
        if not self._validate_url(params["url"]):
            yield event.plain_result("请提供有效的网站URL或添加http(s)前缀")
            return
        
        try:
            if not self.pure_mode:
                yield event.plain_result("正在获取网页截图，请稍候...")
            
            response = await self._fetch_screenshot(params)
            
            # 处理截图响应
            async for message in self._process_screenshot_response(event, response, params):
                yield message
        except httpx.HTTPStatusError as e:
            # 处理HTTP状态码错误（4xx/5xx）
            async for message in self._handle_http_status_error(event, e):
                yield message
        except httpx.RequestError as e:
            # 处理网络连接错误
            logger.error(f"网络连接异常: {str(e)}")
            yield event.plain_result("获取截图失败：网络连接异常，请检查网络后重试")
        except Exception as e:
            logger.error(f"获取截图失败: {str(e)}")
            yield event.plain_result("获取截图失败，请稍后重试")
    
    def _parse_command(self, full_message: str) -> str:
        """解析命令，移除命令前缀，返回参数部分
        
        处理消息中的命令前缀，支持带/前缀的命令格式
        例如："/截图 https://www.example.com" 或 "截图 https://www.example.com"
        
        Args:
            full_message: 完整的消息内容
            
        Returns:
            str: 移除命令前缀后的参数部分
        """
        # 处理 / 前缀
        args = full_message
        if args.startswith("/"):
            args = args[1:].strip()
        
        # 移除命令部分，只保留参数
        # 支持的命令：截图、网页截图、截图网页
        command_prefixes = ["截图网页", "网页截图", "截图"]
        for prefix in command_prefixes:
            if args.startswith(prefix):
                args = args[len(prefix):].strip()
                break
        
        return args
    
    async def _fetch_screenshot(self, params: dict) -> httpx.Response:
        """发送请求获取截图
        
        Args:
            params: 请求参数
            
        Returns:
            httpx.Response: 响应对象
            
        Raises:
            httpx.HTTPError: HTTP请求错误
        """
        logger.info(f"开始获取网页截图: URL={params['url']}, 格式={params['format']}, 尺寸={params['width']}x{params['height']}")
        
        retry_count = 0
        while retry_count <= self.RETRY_COUNT:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(self.api_url, params=params)
                    logger.debug(f"获取截图响应状态码: {response.status_code}")
                    response.raise_for_status()
                    logger.info(f"获取网页截图成功: {params['url']}")
                    return response
            except httpx.RequestError as e:
                # 只对网络请求错误进行重试
                retry_count += 1
                if retry_count <= self.RETRY_COUNT:
                    logger.warning(f"获取网页截图失败，正在重试 ({retry_count}/{self.RETRY_COUNT}): {str(e)}")
                    await asyncio.sleep(self.RETRY_DELAY)
                else:
                    logger.error(f"获取网页截图失败，已达到最大重试次数: {str(e)}")
                    raise
            except httpx.HTTPStatusError as e:
                # HTTP状态码错误不重试
                logger.error(f"获取网页截图失败: {str(e)}")
                raise
    
    async def _process_screenshot_response(self, event: AstrMessageEvent, response: httpx.Response, params: dict) -> AsyncGenerator[Any, None]:
        """处理截图响应
        
        Args:
            event: 消息事件
            response: 响应对象
            params: 请求参数
        """
        # 检查响应是否为图片
        if response.headers.get("content-type", "").startswith("image/"):
            # 保存图片到临时文件
            temp_file = await self._save_screenshot_to_temp_file(response, params["format"])
            
            if not temp_file:
                yield event.plain_result("获取截图失败：图片文件无效")
                return
            
            try:
                # 发送图片
                async for message in self._send_screenshot(event, temp_file, params):
                    yield message
            finally:
                # 清理临时文件
                self._cleanup_temp_file(temp_file)
        else:
            yield event.plain_result("获取截图失败：返回内容不是图片")
    
    async def _save_screenshot_to_temp_file(self, response: httpx.Response, file_ext: str) -> str:
        """保存截图到临时文件
        
        Args:
            response: 响应对象
            file_ext: 文件扩展名
            
        Returns:
            str: 临时文件路径，失败返回None
        """
        temp_file = None
        try:
            logger.debug(f"开始保存截图到临时文件，格式: {file_ext}")
            total_size = 0
            
            # 创建临时文件，设置更安全的权限
            with tempfile.NamedTemporaryFile(
                suffix=f".{file_ext}", 
                delete=False,
                mode='wb'
            ) as f:
                # 使用流式下载
                async for chunk in response.aiter_bytes(chunk_size=self.CHUNK_SIZE):
                    total_size += len(chunk)
                    if total_size > self.MAX_FILE_SIZE:
                        logger.warning(f"截图文件过大: {total_size} bytes, 超过限制: {self.MAX_FILE_SIZE} bytes")
                        return None
                    f.write(chunk)
                temp_file = f.name
            
            # 验证文件存在且有内容
            if not temp_file:
                logger.error("临时文件路径为空")
                return None
            
            if not os.path.exists(temp_file):
                logger.error(f"临时文件不存在: {temp_file}")
                return None
            
            file_size = os.path.getsize(temp_file)
            if file_size == 0:
                logger.error(f"临时文件为空: {temp_file}")
                self._cleanup_temp_file(temp_file)
                return None
            
            logger.info(f"截图保存成功，文件大小: {file_size} bytes, 路径: {temp_file}")
            return temp_file
        except Exception as e:
            logger.error(f"保存截图到临时文件失败: {str(e)}")
            if temp_file and os.path.exists(temp_file):
                self._cleanup_temp_file(temp_file)
            return None
    
    async def _send_screenshot(self, event: AstrMessageEvent, temp_file: str, params: dict) -> AsyncGenerator[Any, None]:
        """发送截图
        
        Args:
            event: 消息事件
            temp_file: 临时文件路径
            params: 请求参数
        """
        try:
            logger.debug(f"开始发送截图: {temp_file}")
            image_message = event.image_result(temp_file)
            yield image_message
            
            if not self.pure_mode:
                success_message = (
                    f"网页截图成功！\n" 
                    f"URL: {params['url']}\n" 
                    f"格式: {params['format']}\n" 
                    f"尺寸: {params['width']}x{params['height']}\n"
                )
                yield event.plain_result(success_message)
            logger.info(f"截图发送成功: {params['url']}")
        except Exception as e:
            logger.error(f"发送图片失败: {str(e)}")
            yield event.plain_result("发送图片失败，请稍后重试")
    
    def _cleanup_temp_file(self, temp_file: str):
        """清理临时文件
        
        Args:
            temp_file: 临时文件路径
        """
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"清理临时文件失败: {str(e)}")
    
    async def _handle_http_status_error(self, event: AstrMessageEvent, e: httpx.HTTPStatusError) -> AsyncGenerator[Any, None]:
        """处理HTTP状态码错误
        
        Args:
            event: 消息事件
            e: HTTP状态码错误
        """
        status_code = e.response.status_code
        logger.error(f"HTTP状态码错误: {status_code}, 详情: {str(e)}")
        if 400 <= status_code < 500:
            yield event.plain_result(f"获取截图失败：请求参数错误 ({status_code})，请检查URL是否正确")
        else:
            yield event.plain_result(f"获取截图失败：服务器错误 ({status_code})，请稍后重试")
    
    def _parse_params(self, args: str) -> tuple[dict, list]:
        """解析命令参数并进行安全性验证
        
        Args:
            args: 命令参数字符串
            
        Returns:
            tuple[dict, list]: 解析后的参数和错误信息列表
        """
        params = {
            "url": None,
            "format": "png",
            "width": 1920,
            "height": 1080
        }
        errors = []
        
        # 检查参数长度
        if len(args) > 4096:
            errors.append("参数长度过长")
            return params, errors
        
        parts = args.split()
        url_found = False
        
        for part in parts:
            if "=" in part:
                # 检查键值对格式
                if part.count("=") > 1:
                    errors.append(f"参数格式错误: {part}")
                    continue
                
                key, value = part.split("=", 1)
                
                # 检查键名是否合法
                if not key.isalnum():
                    errors.append(f"参数名无效: {key}")
                    continue
                
                # 检查值是否包含恶意字符
                dangerous_chars = [';', '|', '&', '`', '\\', '\'', '"', '<', '>']
                for char in dangerous_chars:
                    if char in value:
                        errors.append(f"参数值包含无效字符: {key}")
                        continue
                
                if key == "format":
                    if value in ["png", "webp"]:
                        params["format"] = value
                    else:
                        errors.append(f"format 参数无效，只支持 png 和 webp")
                elif key == "width":
                    try:
                        width = int(value)
                        if 100 <= width <= 3840:
                            params["width"] = width
                        else:
                            errors.append(f"width 必须在 100~3840 之间")
                    except ValueError:
                        errors.append(f"width 必须是数字")
                elif key == "height":
                    try:
                        height = int(value)
                        if 100 <= height <= 2160:
                            params["height"] = height
                        else:
                            errors.append(f"height 必须在 100~2160 之间")
                    except ValueError:
                        errors.append(f"height 必须是数字")
                else:
                    errors.append(f"未知参数: {key}")
            elif not url_found:
                # 处理URL，移除特殊字符但不添加协议前缀
                url_candidate = part
                # 移除常见的特殊字符，如反引号、引号等
                url_candidate = url_candidate.strip('`'"'"'<>'"'"'[](){}')
                # 直接使用用户输入的URL格式，不添加协议前缀
                params["url"] = url_candidate
                url_found = True
        
        # 确保URL参数存在
        if not url_found:
            errors.append("缺少URL参数")
        
        return params, errors
    
    def _validate_url(self, url: str | None) -> bool:
        """验证URL的有效性和安全性
        
        Args:
            url: 要验证的URL
            
        Returns:
            bool: URL是否有效且安全
        """
        if not url:
            return False
        
        # 检查URL长度
        if len(url) > 2048:
            return False
        
        # 检查URL是否包含恶意字符
        dangerous_chars = [';', '|', '&', '`', '\\', '\'', '"', '<', '>']
        for char in dangerous_chars:
            if char in url:
                return False
        
        # 使用urlparse验证URL结构
        parsed = urlparse(url)
        
        # 检查scheme是否为http或https
        if parsed.scheme not in {"http", "https"}:
            return False
        
        # 检查netloc是否非空（确保有主机名）
        if not parsed.netloc:
            return False
        
        # 安全检查：阻止localhost和内部网络地址
        host = parsed.netloc.split(':')[0]  # 移除端口号
        
        # 阻止localhost
        if host in {"localhost", "127.0.0.1", "::1"}:
            return False
        
        # 阻止内部网络地址
        import ipaddress
        try:
            ip = ipaddress.ip_address(host)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False
        except ValueError:
            # 不是IP地址，继续检查
            pass
        
        # 阻止.local域名（通常用于本地网络）
        if host.endswith('.local'):
            return False
        
        # 阻止其他可能的本地网络域名
        local_domains = ['.localhost', '.localdomain', '.test', '.example']
        for domain in local_domains:
            if host.endswith(domain):
                return False
        
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