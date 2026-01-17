"""
常量和正则表达式定义
"""

import re

# 基础 URL
ROOT_URL = "https://3dporndude.com"

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

# 视频列表页正则
REGEX_VIDEO_ITEM = re.compile(
    r'<div class="video-item[^"]*"[^>]*>.*?</div>\s*</div>\s*</div>',
    re.DOTALL
)

# 视频链接和ID
REGEX_VIDEO_LINK = re.compile(r'href="(/video/[^"]+)"')
REGEX_VIDEO_ID = re.compile(r'/video/([^/]+)/?')

# 视频标题
REGEX_VIDEO_TITLE = re.compile(r'<h1[^>]*class="[^"]*video-title[^"]*"[^>]*>([^<]+)</h1>', re.IGNORECASE)
REGEX_VIDEO_TITLE_ALT = re.compile(r'<title>([^<]+)</title>', re.IGNORECASE)

# 视频时长
REGEX_VIDEO_DURATION = re.compile(r'<span[^>]*class="[^"]*duration[^"]*"[^>]*>([^<]+)</span>', re.IGNORECASE)
REGEX_DURATION_TEXT = re.compile(r'(\d+:\d+(?::\d+)?)')

# 视频缩略图
REGEX_VIDEO_THUMBNAIL = re.compile(r'<img[^>]*src="([^"]+)"[^>]*class="[^"]*thumb[^"]*"', re.IGNORECASE)
REGEX_VIDEO_THUMBNAIL_ALT = re.compile(r'data-src="([^"]+)"[^>]*class="[^"]*thumb', re.IGNORECASE)
REGEX_VIDEO_THUMBNAIL_OG = re.compile(r'<meta[^>]*property="og:image"[^>]*content="([^"]+)"', re.IGNORECASE)

# 视频预览图
REGEX_VIDEO_PREVIEW = re.compile(r'data-preview="([^"]+)"', re.IGNORECASE)

# 视频观看数
REGEX_VIDEO_VIEWS = re.compile(r'<span[^>]*class="[^"]*views[^"]*"[^>]*>([^<]+)</span>', re.IGNORECASE)
REGEX_VIEWS_NUMBER = re.compile(r'([\d,\.]+[KMB]?)')

# 视频评分
REGEX_VIDEO_RATING = re.compile(r'<span[^>]*class="[^"]*(?:rating|like)[^"]*"[^>]*>([^<]+)</span>', re.IGNORECASE)
REGEX_RATING_PERCENT = re.compile(r'(\d+)%')

# 视频标签
REGEX_VIDEO_TAGS = re.compile(r'<a[^>]*href="/tag/([^"]+)"[^>]*>([^<]+)</a>', re.IGNORECASE)

# 视频上传者/制作者
REGEX_VIDEO_UPLOADER = re.compile(r'<a[^>]*href="/(?:creator|channel|uploader)/([^"]+)"[^>]*>([^<]+)</a>', re.IGNORECASE)
REGEX_VIDEO_UPLOADER_ALT = re.compile(r'class="[^"]*(?:creator|uploader|channel)[^"]*"[^>]*>([^<]+)<', re.IGNORECASE)

# 视频发布日期
REGEX_VIDEO_DATE = re.compile(r'<span[^>]*class="[^"]*(?:date|time|ago)[^"]*"[^>]*>([^<]+)</span>', re.IGNORECASE)

# 分类页面
REGEX_CATEGORY_TITLE = re.compile(r'<h1[^>]*>([^<]+)</h1>', re.IGNORECASE)

# 分页
REGEX_PAGINATION = re.compile(r'<a[^>]*href="([^"]*\?page=\d+[^"]*)"[^>]*>', re.IGNORECASE)
REGEX_PAGE_NUMBER = re.compile(r'page=(\d+)')
REGEX_TOTAL_PAGES = re.compile(r'<a[^>]*href="[^"]*\?page=(\d+)[^"]*"[^>]*class="[^"]*last[^"]*"', re.IGNORECASE)

# 视频源链接（HTML5播放器）
REGEX_VIDEO_SOURCE = re.compile(r'<source[^>]*src="([^"]+)"[^>]*type="video/mp4"', re.IGNORECASE)
REGEX_VIDEO_SOURCE_ALT = re.compile(r'"(?:file|src|url)"\s*:\s*"([^"]+\.mp4[^"]*)"', re.IGNORECASE)

# iframe嵌入视频
REGEX_IFRAME_SRC = re.compile(r'<iframe[^>]*src="([^"]+)"', re.IGNORECASE)

# 视频质量选项
REGEX_QUALITY_OPTIONS = re.compile(r'"(\d+p?)"\s*:\s*"([^"]+)"', re.IGNORECASE)

# 列表页视频信息
REGEX_LIST_VIDEO = re.compile(
    r'<a[^>]*href="(/video/[^"]+)"[^>]*>.*?'
    r'<img[^>]*(?:src|data-src)="([^"]+)".*?'
    r'(?:<span[^>]*class="[^"]*duration[^"]*"[^>]*>([^<]*)</span>)?.*?'
    r'</a>',
    re.DOTALL | re.IGNORECASE
)

# 获取视频卡片信息的正则
REGEX_VIDEO_CARD = re.compile(
    r'<div[^>]*class="[^"]*(?:video-item|thumb-block|video-block)[^"]*"[^>]*>(.*?)</div>\s*(?:</div>)*',
    re.DOTALL | re.IGNORECASE
)

# JSON-LD 结构化数据
REGEX_JSON_LD = re.compile(
    r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE
)

# 点赞数
REGEX_LIKES = re.compile(r'<span[^>]*class="[^"]*likes?[^"]*"[^>]*>(\d+)</span>', re.IGNORECASE)

# 不喜欢数
REGEX_DISLIKES = re.compile(r'<span[^>]*class="[^"]*dislikes?[^"]*"[^>]*>(\d+)</span>', re.IGNORECASE)

# 视频描述
REGEX_VIDEO_DESCRIPTION = re.compile(
    r'<div[^>]*class="[^"]*(?:description|video-desc)[^"]*"[^>]*>(.*?)</div>',
    re.DOTALL | re.IGNORECASE
)

# 相关视频
REGEX_RELATED_VIDEOS = re.compile(
    r'<div[^>]*class="[^"]*related[^"]*"[^>]*>(.*?)</div>\s*</div>',
    re.DOTALL | re.IGNORECASE
)

# 标签/分类常量
POPULAR_TAGS = [
    "futanari-hentai",
    "tentacles", 
    "hardcore",
    "rough",
    "pov",
    "big-tits",
    "blowjob",
    "anal",
    "creampie",
    "milf",
    "teen",
    "lesbian",
    "threesome",
    "gangbang",
    "bbc",
    "deepthroat",
]