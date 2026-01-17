"""
3DPornDude 网站解析核心模块
"""

import re
import aiohttp
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin, quote_plus
from bs4 import BeautifulSoup

from .consts import ROOT_URL, HEADERS, POPULAR_TAGS
from .errors import (
    InvalidURL, VideoNotFound, NetworkError, TagNotFound, NoResultsFound
)


class VideoInfo:
    """视频信息数据类"""
    
    def __init__(
        self,
        video_id: str,
        url: str,
        title: str = "",
        duration: str = "",
        thumbnail: str = "",
        preview: str = "",
        views: str = "",
        rating: str = "",
        likes: int = 0,
        dislikes: int = 0,
        uploader: str = "",
        upload_date: str = "",
        tags: Optional[List[str]] = None,
        description: str = ""
    ):
        self.video_id = video_id
        self.url = url
        self.title = title
        self.duration = duration
        self.thumbnail = thumbnail
        self.preview = preview
        self.views = views
        self.rating = rating
        self.likes = likes
        self.dislikes = dislikes
        self.uploader = uploader
        self.upload_date = upload_date
        self.tags = tags if tags is not None else []
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "video_id": self.video_id,
            "url": self.url,
            "title": self.title,
            "duration": self.duration,
            "thumbnail": self.thumbnail,
            "preview": self.preview,
            "views": self.views,
            "rating": self.rating,
            "likes": self.likes,
            "dislikes": self.dislikes,
            "uploader": self.uploader,
            "upload_date": self.upload_date,
            "tags": self.tags,
            "description": self.description,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "video_id": self.video_id,
            "url": self.url,
            "title": self.title,
            "duration": self.duration,
            "thumbnail": self.thumbnail,
            "preview": self.preview,
            "views": self.views,
            "rating": self.rating,
            "likes": self.likes,
            "dislikes": self.dislikes,
            "uploader": self.uploader,
            "upload_date": self.upload_date,
            "tags": self.tags,
            "description": self.description,
        }


class Video:
    """视频对象类，用于获取和解析视频详情"""
    
    def __init__(self, video_id: str, client: "Client"):
        """
        初始化视频对象
        
        Args:
            video_id: 视频ID（URL路径的最后一部分）
            client: Client实例
        """
        self.video_id = video_id
        self.client = client
        self.url = f"{ROOT_URL}/video/{video_id}"
        self._html_content: Optional[str] = None
        self._soup: Optional[BeautifulSoup] = None
        self._info: Optional[VideoInfo] = None
    
    async def _fetch_page(self) -> str:
        """获取视频页面HTML"""
        if self._html_content is None:
            self._html_content = await self.client.fetch(self.url)
            if "404" in self._html_content and "not found" in self._html_content.lower():
                raise VideoNotFound(f"视频不存在: {self.video_id}")
        return self._html_content
    
    async def _get_soup(self) -> BeautifulSoup:
        """获取BeautifulSoup对象"""
        if self._soup is None:
            html_content = await self._fetch_page()
            self._soup = BeautifulSoup(html_content, 'html.parser')
        return self._soup
    
    async def get_info(self) -> VideoInfo:
        """获取视频完整信息"""
        if self._info is not None:
            return self._info
        
        soup = await self._get_soup()
        html_content = await self._fetch_page()
        
        # 解析标题
        title = ""
        title_elem = soup.find('h1', class_=lambda x: x and 'title' in x.lower() if x else False)
        if title_elem:
            title = title_elem.get_text(strip=True)
        else:
            # 尝试从 og:title 获取
            og_title = soup.find('meta', property='og:title')
            if og_title:
                title = og_title.get('content', '')
            else:
                # 尝试从 <title> 获取
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    # 移除网站名称后缀
                    if ' - ' in title:
                        title = title.rsplit(' - ', 1)[0]
        
        # 解析时长
        duration = ""
        duration_elem = soup.find('span', class_=lambda x: x and 'duration' in x.lower() if x else False)
        if duration_elem:
            duration = duration_elem.get_text(strip=True)
        else:
            # 从页面文本中查找时长模式
            duration_match = re.search(r'(\d+:\d+(?::\d+)?)', html_content)
            if duration_match:
                duration = duration_match.group(1)
        
        # 解析缩略图
        thumbnail = ""
        og_image = soup.find('meta', property='og:image')
        if og_image:
            thumbnail = og_image.get('content', '')
        else:
            # 查找视频播放器附近的图片
            video_container = soup.find('div', class_=lambda x: x and 'player' in x.lower() if x else False)
            if video_container:
                img = video_container.find('img')
                if img:
                    thumbnail = img.get('src') or img.get('data-src', '')
        
        # 解析预览图
        preview = ""
        preview_elem = soup.find(attrs={'data-preview': True})
        if preview_elem:
            preview = preview_elem.get('data-preview', '')
        
        # 解析观看数
        views = ""
        views_elem = soup.find('span', class_=lambda x: x and 'views' in x.lower() if x else False)
        if views_elem:
            views = views_elem.get_text(strip=True)
        else:
            # 查找包含视图数的文本
            views_match = re.search(r'([\d,\.]+[KMB]?)\s*(?:views?|播放)', html_content, re.IGNORECASE)
            if views_match:
                views = views_match.group(1)
        
        # 解析评分
        rating = ""
        rating_elem = soup.find('span', class_=lambda x: x and ('rating' in x.lower() or 'like' in x.lower()) if x else False)
        if rating_elem:
            rating = rating_elem.get_text(strip=True)
        
        # 解析点赞/不喜欢
        likes = 0
        dislikes = 0
        likes_elem = soup.find('span', class_=lambda x: x and 'like' in x.lower() and 'dis' not in x.lower() if x else False)
        if likes_elem:
            likes_text = likes_elem.get_text(strip=True)
            likes_match = re.search(r'(\d+)', likes_text)
            if likes_match:
                likes = int(likes_match.group(1))
        
        dislikes_elem = soup.find('span', class_=lambda x: x and 'dislike' in x.lower() if x else False)
        if dislikes_elem:
            dislikes_text = dislikes_elem.get_text(strip=True)
            dislikes_match = re.search(r'(\d+)', dislikes_text)
            if dislikes_match:
                dislikes = int(dislikes_match.group(1))
        
        # 解析上传者
        uploader = ""
        uploader_link = soup.find('a', href=lambda x: x and ('/creator/' in x or '/channel/' in x or '/uploader/' in x) if x else False)
        if uploader_link:
            uploader = uploader_link.get_text(strip=True)
        else:
            # 查找上传者相关的元素
            uploader_elem = soup.find(class_=lambda x: x and ('creator' in x.lower() or 'uploader' in x.lower() or 'channel' in x.lower()) if x else False)
            if uploader_elem:
                uploader = uploader_elem.get_text(strip=True)
        
        # 解析上传日期
        upload_date = ""
        date_elem = soup.find('span', class_=lambda x: x and ('date' in x.lower() or 'time' in x.lower() or 'ago' in x.lower()) if x else False)
        if date_elem:
            upload_date = date_elem.get_text(strip=True)
        
        # 解析标签
        tags = []
        tag_links = soup.find_all('a', href=lambda x: x and '/tag/' in x if x else False)
        for tag_link in tag_links:
            tag_text = tag_link.get_text(strip=True)
            if tag_text and tag_text not in tags:
                tags.append(tag_text)
        
        # 解析描述
        description = ""
        desc_elem = soup.find('div', class_=lambda x: x and ('description' in x.lower() or 'desc' in x.lower()) if x else False)
        if desc_elem:
            description = desc_elem.get_text(strip=True)
        
        self._info = VideoInfo(
            video_id=self.video_id,
            url=self.url,
            title=title,
            duration=duration,
            thumbnail=thumbnail,
            preview=preview,
            views=views,
            rating=rating,
            likes=likes,
            dislikes=dislikes,
            uploader=uploader,
            upload_date=upload_date,
            tags=tags,
            description=description,
        )
        
        return self._info
    
    @property
    async def title(self) -> str:
        """获取视频标题"""
        info = await self.get_info()
        return info.title
    
    @property
    async def thumbnail(self) -> str:
        """获取视频缩略图"""
        info = await self.get_info()
        return info.thumbnail
    
    @property
    async def duration(self) -> str:
        """获取视频时长"""
        info = await self.get_info()
        return info.duration
    
    @property
    async def views(self) -> str:
        """获取观看数"""
        info = await self.get_info()
        return info.views
    
    @property
    async def tags(self) -> List[str]:
        """获取标签列表"""
        info = await self.get_info()
        return info.tags


class Client:
    """3DPornDude API客户端"""
    
    def __init__(self, proxy: Optional[str] = None, timeout: int = 30):
        """
        初始化客户端
        
        Args:
            proxy: 代理服务器地址，如 "http://127.0.0.1:7890"
            timeout: 请求超时时间（秒）
        """
        self.proxy = proxy
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建aiohttp会话"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                headers=HEADERS,
                timeout=timeout,
                trust_env=True
            )
        return self._session
    
    async def close(self):
        """关闭会话"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def fetch(self, url: str) -> str:
        """
        获取页面HTML内容
        
        Args:
            url: 页面URL
            
        Returns:
            HTML内容字符串
        """
        session = await self._get_session()
        try:
            async with session.get(url, proxy=self.proxy) as response:
                if response.status == 404:
                    raise VideoNotFound(f"页面不存在: {url}")
                if response.status != 200:
                    raise NetworkError(f"HTTP错误 {response.status}: {url}")
                return await response.text()
        except aiohttp.ClientError as e:
            raise NetworkError(f"网络请求失败: {e}")
    
    def get_video(self, video_id: str) -> Video:
        """
        获取视频对象
        
        Args:
            video_id: 视频ID
            
        Returns:
            Video对象
        """
        # 处理完整URL的情况
        if video_id.startswith("http"):
            match = re.search(r'/video/([^/\?]+)', video_id)
            if match:
                video_id = match.group(1)
            else:
                raise InvalidURL(f"无效的视频URL: {video_id}")
        
        return Video(video_id, self)
    
    async def get_videos_by_tag(
        self, 
        tag: str, 
        page: int = 1, 
        sort: str = "most-viewed"
    ) -> List[VideoInfo]:
        """
        按标签获取视频列表
        
        Args:
            tag: 标签名称
            page: 页码
            sort: 排序方式 (most-viewed, newest, top-rated)
            
        Returns:
            VideoInfo列表
        """
        url = f"{ROOT_URL}/tag/{tag}"
        if page > 1:
            url += f"?page={page}"
        
        html_content = await self.fetch(url)
        
        if "404" in html_content and "not found" in html_content.lower():
            raise TagNotFound(f"标签不存在: {tag}")
        
        return self._parse_video_list(html_content)
    
    async def search(
        self, 
        query: str, 
        page: int = 1
    ) -> List[VideoInfo]:
        """
        搜索视频
        
        Args:
            query: 搜索关键词
            page: 页码
            
        Returns:
            VideoInfo列表
        """
        encoded_query = quote_plus(query)
        url = f"{ROOT_URL}/search?q={encoded_query}"
        if page > 1:
            url += f"&page={page}"
        
        html_content = await self.fetch(url)
        return self._parse_video_list(html_content)
    
    async def get_latest_videos(self, page: int = 1) -> List[VideoInfo]:
        """
        获取最新视频
        
        Args:
            page: 页码
            
        Returns:
            VideoInfo列表
        """
        url = ROOT_URL
        if page > 1:
            url += f"?page={page}"
        
        html_content = await self.fetch(url)
        return self._parse_video_list(html_content)
    
    async def get_popular_videos(self, page: int = 1) -> List[VideoInfo]:
        """
        获取热门视频
        
        Args:
            page: 页码
            
        Returns:
            VideoInfo列表
        """
        url = f"{ROOT_URL}/most-viewed"
        if page > 1:
            url += f"?page={page}"
        
        html_content = await self.fetch(url)
        return self._parse_video_list(html_content)
    
    async def get_random_video(self) -> VideoInfo:
        """
        获取随机视频
        
        Returns:
            随机VideoInfo
        """
        import random
        
        # 从首页获取视频列表
        videos = await self.get_latest_videos(page=random.randint(1, 10))
        if not videos:
            videos = await self.get_latest_videos(page=1)
        
        if not videos:
            raise NoResultsFound("无法获取随机视频")
        
        return random.choice(videos)
    
    def _parse_video_list(self, html_content: str) -> List[VideoInfo]:
        """
        解析视频列表页面
        
        Args:
            html_content: HTML内容
            
        Returns:
            VideoInfo列表
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        videos = []
        
        # 查找所有视频卡片
        video_cards = soup.find_all('div', class_=lambda x: x and ('video' in x.lower() or 'thumb' in x.lower()) if x else False)
        
        for card in video_cards:
            try:
                # 查找视频链接
                link = card.find('a', href=lambda x: x and '/video/' in x if x else False)
                if not link:
                    continue
                
                href = link.get('href', '')
                video_id_match = re.search(r'/video/([^/\?]+)', href)
                if not video_id_match:
                    continue
                
                video_id = video_id_match.group(1)
                url = urljoin(ROOT_URL, href)
                
                # 解析标题
                title = ""
                title_elem = card.find(['h2', 'h3', 'h4', 'span', 'a'], class_=lambda x: x and 'title' in x.lower() if x else False)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                else:
                    # 尝试从链接的title属性或文本获取
                    title = link.get('title', '') or link.get_text(strip=True)
                
                # 解析缩略图
                thumbnail = ""
                img = card.find('img')
                if img:
                    thumbnail = img.get('src') or img.get('data-src') or img.get('data-lazy-src', '')
                
                # 解析预览图
                preview = ""
                preview_elem = card.find(attrs={'data-preview': True})
                if preview_elem:
                    preview = preview_elem.get('data-preview', '')
                
                # 解析时长
                duration = ""
                duration_elem = card.find('span', class_=lambda x: x and 'duration' in x.lower() if x else False)
                if duration_elem:
                    duration = duration_elem.get_text(strip=True)
                
                # 解析观看数
                views = ""
                views_elem = card.find('span', class_=lambda x: x and 'views' in x.lower() if x else False)
                if views_elem:
                    views = views_elem.get_text(strip=True)
                
                # 解析评分
                rating = ""
                rating_elem = card.find('span', class_=lambda x: x and ('rating' in x.lower() or 'percent' in x.lower()) if x else False)
                if rating_elem:
                    rating = rating_elem.get_text(strip=True)
                
                # 解析上传者
                uploader = ""
                uploader_elem = card.find('a', href=lambda x: x and ('/creator/' in x or '/channel/' in x) if x else False)
                if uploader_elem:
                    uploader = uploader_elem.get_text(strip=True)
                
                # 解析日期
                upload_date = ""
                date_elem = card.find('span', class_=lambda x: x and ('date' in x.lower() or 'ago' in x.lower()) if x else False)
                if date_elem:
                    upload_date = date_elem.get_text(strip=True)
                
                video_info = VideoInfo(
                    video_id=video_id,
                    url=url,
                    title=title,
                    duration=duration,
                    thumbnail=thumbnail,
                    preview=preview,
                    views=views,
                    rating=rating,
                    uploader=uploader,
                    upload_date=upload_date,
                )
                
                videos.append(video_info)
                
            except Exception:
                # 跳过解析失败的卡片
                continue
        
        return videos
    
    async def get_available_tags(self) -> List[str]:
        """
        获取可用的标签列表
        
        Returns:
            标签列表
        """
        return POPULAR_TAGS.copy()


# 便捷函数
async def get_video_info(video_id: str, proxy: Optional[str] = None) -> VideoInfo:
    """
    获取视频信息的便捷函数
    
    Args:
        video_id: 视频ID
        proxy: 代理地址
        
    Returns:
        VideoInfo对象
    """
    client = Client(proxy=proxy)
    try:
        video = client.get_video(video_id)
        return await video.get_info()
    finally:
        await client.close()


async def search_videos(query: str, page: int = 1, proxy: Optional[str] = None) -> List[VideoInfo]:
    """
    搜索视频的便捷函数
    
    Args:
        query: 搜索关键词
        page: 页码
        proxy: 代理地址
        
    Returns:
        VideoInfo列表
    """
    client = Client(proxy=proxy)
    try:
        return await client.search(query, page)
    finally:
        await client.close()