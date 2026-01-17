"""
3DPornDude AstrBot 插件
用于解析和查询 https://3dporndude.com/ 网站视频信息
"""

import aiohttp
import random
from io import BytesIO
from PIL import Image
from pathlib import Path
from typing import Optional, List

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import astrbot.api.message_components as Comp

from .modules.core import Client, VideoInfo
from .modules.errors import (
    VideoNotFound, NetworkError, TagNotFound, NoResultsFound
)
from .modules.consts import POPULAR_TAGS


# 缓存目录
CACHE_DIR = Path(__file__).parent / "cache"


def ensure_cache_dir():
    """确保缓存目录存在"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def clean_cache():
    """清理缓存文件"""
    if CACHE_DIR.exists():
        for file in CACHE_DIR.iterdir():
            try:
                file.unlink()
            except Exception:
                pass


def apply_mosaic(image: Image.Image, block_size: int = 10) -> Image.Image:
    """
    对图片应用马赛克效果
    
    Args:
        image: PIL Image对象
        block_size: 马赛克块大小，越大越模糊
        
    Returns:
        处理后的图片
    """
    if block_size <= 1:
        return image
    
    # 缩小然后放大实现马赛克效果
    small = image.resize(
        (max(1, image.width // block_size), max(1, image.height // block_size)),
        Image.Resampling.BILINEAR
    )
    return small.resize(image.size, Image.Resampling.NEAREST)


async def download_and_process_image(
    url: str, 
    mosaic_level: int = 0,
    proxy: Optional[str] = None
) -> Optional[str]:
    """
    下载并处理图片
    
    Args:
        url: 图片URL
        mosaic_level: 马赛克级别 (0=无, 1=轻度, 2=中度, 3=重度)
        proxy: 代理地址
        
    Returns:
        处理后图片的本地路径
    """
    if not url:
        return None
    
    ensure_cache_dir()
    
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
            async with session.get(url, proxy=proxy) as response:
                if response.status != 200:
                    return None
                
                image_data = await response.read()
        
        # 打开图片
        image = Image.open(BytesIO(image_data))
        
        # 转换为RGB模式（处理RGBA等情况）
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 应用马赛克
        if mosaic_level > 0:
            block_sizes = {1: 8, 2: 15, 3: 25}
            block_size = block_sizes.get(mosaic_level, 15)
            image = apply_mosaic(image, block_size)
        
        # 保存到缓存
        filename = f"thumb_{random.randint(100000, 999999)}.jpg"
        filepath = CACHE_DIR / filename
        image.save(filepath, "JPEG", quality=85)
        
        return str(filepath)
        
    except Exception as e:
        logger.error(f"下载处理图片失败: {e}")
        return None


def format_video_info(info: VideoInfo, show_url: bool = True) -> str:
    """
    格式化视频信息为文本
    
    Args:
        info: VideoInfo对象
        show_url: 是否显示URL
        
    Returns:
        格式化的文本
    """
    lines = []
    lines.append(f"🎬 {info.title or '无标题'}")
    
    if info.duration:
        lines.append(f"⏱️ 时长: {info.duration}")
    
    if info.views:
        lines.append(f"👁️ 播放: {info.views}")
    
    # 过滤无效评分值（-1 通常表示无评分数据）
    if info.rating and info.rating not in ["-1", "-1%", "N/A", "0"]:
        lines.append(f"👍 评分: {info.rating}")
    elif info.likes > 0 or info.dislikes > 0:
        # 如果有点赞/踩数据，显示点赞数
        lines.append(f"👍 点赞: {info.likes}")
    
    if info.uploader:
        lines.append(f"👤 作者: {info.uploader}")
    
    if info.upload_date:
        lines.append(f"📅 日期: {info.upload_date}")
    
    if info.tags:
        tags_str = ", ".join(info.tags[:5])
        if len(info.tags) > 5:
            tags_str += f" (+{len(info.tags) - 5})"
        lines.append(f"🏷️ 标签: {tags_str}")
    
    if show_url:
        lines.append(f"🔗 {info.url}")
    
    # 添加零宽字符防止strip
    return "\n".join(lines) + "\u200E"


def format_video_list(videos: List[VideoInfo], title: str = "视频列表") -> str:
    """
    格式化视频列表
    
    Args:
        videos: VideoInfo列表
        title: 列表标题
        
    Returns:
        格式化的文本
    """
    if not videos:
        return f"📭 {title}: 没有找到视频\u200E"
    
    lines = [f"📋 {title} ({len(videos)}个结果):", ""]
    
    for i, video in enumerate(videos[:10], 1):
        duration_str = f" [{video.duration}]" if video.duration else ""
        views_str = f" 👁️{video.views}" if video.views else ""
        lines.append(f"{i}. {video.title or video.video_id}{duration_str}{views_str}")
        lines.append(f"   ID: {video.video_id}")
    
    if len(videos) > 10:
        lines.append(f"\n... 还有 {len(videos) - 10} 个视频")
    
    return "\n".join(lines) + "\u200E"


@register("3dporndude", "vmoranv", "3DPornDude视频解析插件", "1.0.1")
class Main(Star):
    """3DPornDude 视频解析插件"""
    
    def __init__(self, context: Context):
        super().__init__(context)
        self.context = context
        self._plugin_config = {}
        # 初始时创建默认客户端
        self.client = Client(proxy=None, timeout=30)
    
    async def initialize(self):
        """插件初始化"""
        # 从context获取配置
        try:
            config = getattr(self.context, 'config', {})
            if isinstance(config, dict):
                plugin_config = config.get("3dporndude", {})
            else:
                plugin_config = {}
        except Exception:
            plugin_config = {}
        
        self._plugin_config = plugin_config
        
        # 获取配置
        proxy = plugin_config.get("proxy", "")
        timeout = plugin_config.get("timeout", 30)
        
        # 关闭旧客户端
        if self.client:
            try:
                await self.client.close()
            except Exception:
                pass
        
        # 创建新客户端
        self.client = Client(proxy=proxy if proxy else None, timeout=timeout)
        
        # 确保缓存目录存在
        ensure_cache_dir()
        
        logger.info("3DPornDude 插件已初始化")
    
    async def terminate(self):
        """插件销毁"""
        # 关闭客户端
        if self.client:
            await self.client.close()
        
        # 清理缓存
        clean_cache()
        
        logger.info("3DPornDude 插件已销毁")
    
    def _get_mosaic_level(self) -> int:
        """获取马赛克级别配置"""
        if hasattr(self, '_plugin_config'):
            return self._plugin_config.get("mosaic_level", 2)
        return 2
    
    def _get_proxy(self) -> Optional[str]:
        """获取代理配置"""
        if hasattr(self, '_plugin_config'):
            proxy = self._plugin_config.get("proxy", "")
            return proxy if proxy else None
        return None
    
    @filter.command("3DPornDude")
    async def cmd_video_info(self, event: AstrMessageEvent, video_id: str = ""):
        """
        获取视频详细信息
        用法: /3DPornDude <视频ID>
        """
        # 清理上次缓存
        clean_cache()
        
        if not video_id:
            yield event.plain_result(
                "❌ 请提供视频ID\n"
                "用法: /3DPornDude <视频ID>\n"
                "示例: /3DPornDude huntrix-game-kpop-demon-hunters-futa-intersex-porn-animation\u200E"
            )
            return
        
        try:
            video = self.client.get_video(video_id)
            info = await video.get_info()
            
            # 格式化信息
            text = format_video_info(info)
            
            # 下载并处理缩略图
            mosaic_level = self._get_mosaic_level()
            thumb_path = await download_and_process_image(
                info.thumbnail, 
                mosaic_level,
                self._get_proxy()
            )
            
            if thumb_path:
                chain = [
                    Comp.Plain(text),
                    Comp.Image.fromFileSystem(thumb_path)
                ]
                yield event.chain_result(chain)
            else:
                yield event.plain_result(text)
                
        except VideoNotFound:
            yield event.plain_result(f"❌ 视频不存在: {video_id}\u200E")
        except NetworkError as e:
            yield event.plain_result(f"❌ 网络错误: {e}\u200E")
        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            yield event.plain_result(f"❌ 获取失败: {e}\u200E")
    
    @filter.command("3DPornDude_tag")
    async def cmd_videos_by_tag(self, event: AstrMessageEvent, tag: str = "", page: str = "1"):
        """
        按标签获取视频列表
        用法: /3DPornDude_tag <标签> [页码]
        """
        clean_cache()
        
        if not tag:
            tags_list = ", ".join(POPULAR_TAGS[:10])
            yield event.plain_result(
                "❌ 请提供标签名称\n"
                "用法: /3DPornDude_tag <标签> [页码]\n"
                f"常用标签: {tags_list}\u200E"
            )
            return
        
        try:
            page_num = int(page)
        except ValueError:
            page_num = 1
        
        try:
            videos = await self.client.get_videos_by_tag(tag, page=page_num)
            text = format_video_list(videos, f"标签: {tag} (第{page_num}页)")
            yield event.plain_result(text)
            
        except TagNotFound:
            yield event.plain_result(f"❌ 标签不存在: {tag}\u200E")
        except Exception as e:
            logger.error(f"获取标签视频失败: {e}")
            yield event.plain_result(f"❌ 获取失败: {e}\u200E")
    
    @filter.command("3DPornDude_search")
    async def cmd_search(self, event: AstrMessageEvent, query: str = "", page: str = "1"):
        """
        搜索视频
        用法: /3DPornDude_search <关键词> [页码]
        """
        clean_cache()
        
        if not query:
            yield event.plain_result(
                "❌ 请提供搜索关键词\n"
                "用法: /3DPornDude_search <关键词> [页码]\n"
                "示例: /3DPornDude_search futanari\u200E"
            )
            return
        
        # 解析页码
        try:
            page_num = int(page)
        except ValueError:
            page_num = 1
        
        try:
            videos = await self.client.search(query, page=page_num)
            text = format_video_list(videos, f"搜索: {query} (第{page_num}页)")
            yield event.plain_result(text)
            
        except Exception as e:
            logger.error(f"搜索视频失败: {e}")
            yield event.plain_result(f"❌ 搜索失败: {e}\u200E")
    
    @filter.command("3DPornDude_latest")
    async def cmd_latest(self, event: AstrMessageEvent, page: str = "1"):
        """
        获取最新视频
        用法: /3DPornDude_latest [页码]
        """
        clean_cache()
        
        try:
            page_num = int(page)
        except ValueError:
            page_num = 1
        
        try:
            videos = await self.client.get_latest_videos(page=page_num)
            text = format_video_list(videos, f"最新视频 (第{page_num}页)")
            yield event.plain_result(text)
            
        except Exception as e:
            logger.error(f"获取最新视频失败: {e}")
            yield event.plain_result(f"❌ 获取失败: {e}\u200E")
    
    @filter.command("3DPornDude_popular")
    async def cmd_popular(self, event: AstrMessageEvent, page: str = "1"):
        """
        获取热门视频
        用法: /3DPornDude_popular [页码]
        """
        clean_cache()
        
        try:
            page_num = int(page)
        except ValueError:
            page_num = 1
        
        try:
            videos = await self.client.get_popular_videos(page=page_num)
            text = format_video_list(videos, f"热门视频 (第{page_num}页)")
            yield event.plain_result(text)
            
        except Exception as e:
            logger.error(f"获取热门视频失败: {e}")
            yield event.plain_result(f"❌ 获取失败: {e}\u200E")
    
    @filter.command("3DPornDude_random")
    async def cmd_random(self, event: AstrMessageEvent):
        """
        获取随机视频
        用法: /3DPornDude_random
        """
        clean_cache()
        
        try:
            info = await self.client.get_random_video()
            
            # 格式化信息
            text = format_video_info(info)
            
            # 下载并处理缩略图
            mosaic_level = self._get_mosaic_level()
            thumb_path = await download_and_process_image(
                info.thumbnail, 
                mosaic_level,
                self._get_proxy()
            )
            
            if thumb_path:
                chain = [
                    Comp.Plain("🎲 随机视频:\n\n" + text),
                    Comp.Image.fromFileSystem(thumb_path)
                ]
                yield event.chain_result(chain)
            else:
                yield event.plain_result("🎲 随机视频:\n\n" + text)
                
        except NoResultsFound:
            yield event.plain_result("❌ 无法获取随机视频\u200E")
        except Exception as e:
            logger.error(f"获取随机视频失败: {e}")
            yield event.plain_result(f"❌ 获取失败: {e}\u200E")
    
    @filter.command("3DPornDude_tags")
    async def cmd_tags(self, event: AstrMessageEvent):
        """
        列出常用标签
        用法: /3DPornDude_tags
        """
        tags_list = "\n".join([f"• {tag}" for tag in POPULAR_TAGS])
        yield event.plain_result(
            f"🏷️ 常用标签:\n\n{tags_list}\n\n"
            f"使用 /3DPornDude_tag <标签> 查看该标签下的视频\u200E"
        )
