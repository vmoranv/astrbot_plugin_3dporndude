# 3DPornDude AstrBot 插件

一个用于解析 [3DPornDude](https://3dporndude.com/) 网站视频信息的 AstrBot 插件。

## 功能特性

- 🎬 获取视频详细信息（标题、时长、观看数、评分等）
- 🏷️ 按标签浏览视频
- 🔍 搜索视频
- 📋 获取最新/热门视频列表
- 🎲 随机获取视频
- 🖼️ 缩略图马赛克处理（可配置级别）
- 🌐 代理支持

## 安装

将插件目录放置到 AstrBot 的插件目录中，插件会自动安装依赖。

## 配置

在 AstrBot 管理面板中配置以下选项：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| proxy | string | "" | 代理服务器地址，如 `http://127.0.0.1:7890` |
| mosaic_level | int | 2 | 缩略图马赛克级别 (0=无, 1=轻度, 2=中度, 3=重度) |
| timeout | int | 30 | 网络请求超时时间（秒） |

## 命令列表

### 获取视频信息
```
/3DPornDude <视频ID>
```
获取指定视频的详细信息和缩略图。

示例：
```
/3DPornDude huntrix-game-kpop-demon-hunters-futa-intersex-porn-animation
```

### 按标签浏览
```
/3DPornDude_tag <标签> [页码]
```
获取指定标签下的视频列表。

示例：
```
/3DPornDude_tag futanari-hentai
/3DPornDude_tag hardcore 2
```

### 搜索视频
```
/3DPornDude_search <关键词> [页码]
```
搜索视频。

示例：
```
/3DPornDude_search futanari
/3DPornDude_search anime girl 2
```

### 最新视频
```
/3DPornDude_latest [页码]
```
获取最新上传的视频列表。

### 热门视频
```
/3DPornDude_popular [页码]
```
获取热门视频列表。

### 随机视频
```
/3DPornDude_random
```
随机获取一个视频。

### 查看常用标签
```
/3DPornDude_tags
```
列出常用标签。

## API 使用（独立使用）

本插件的核心模块也可以独立使用：

```python
import asyncio
from modules.core import Client, get_video_info, search_videos

async def main():
    # 创建客户端
    client = Client(proxy="http://127.0.0.1:7890")
    
    try:
        # 获取视频信息
        video = client.get_video("video-id-here")
        info = await video.get_info()
        print(f"标题: {info.title}")
        print(f"时长: {info.duration}")
        print(f"观看数: {info.views}")
        
        # 搜索视频
        results = await client.search("keyword", page=1)
        for v in results:
            print(f"- {v.title}")
        
        # 按标签获取
        tag_videos = await client.get_videos_by_tag("futanari-hentai")
        for v in tag_videos:
            print(f"- {v.title}")
            
    finally:
        await client.close()

asyncio.run(main())
```

## 文件结构

```
astrbot_plugin_3dporndude/
├── main.py              # AstrBot 插件主文件
├── metadata.yaml        # 插件元数据
├── requirements.txt     # Python 依赖
├── _conf_schema.json    # 配置模式
├── README.md            # 说明文档
└── modules/
    ├── __init__.py      # 模块初始化
    ├── core.py          # 核心解析功能
    ├── consts.py        # 常量定义
    └── errors.py        # 异常类定义
```

## 注意事项

1. 本插件仅供学习和研究目的使用
2. 请遵守当地法律法规
3. 请勿滥用 API，避免对目标网站造成过大压力
4. 缩略图会自动进行马赛克处理，可在配置中调整级别

## 许可证

MIT License
