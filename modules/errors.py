"""
自定义异常类
"""


class ThreeDPornDudeException(Exception):
    """基础异常类"""
    pass


class InvalidURL(ThreeDPornDudeException):
    """无效的URL"""
    pass


class VideoNotFound(ThreeDPornDudeException):
    """视频未找到"""
    pass


class VideoUnavailable(ThreeDPornDudeException):
    """视频不可用（已删除或版权问题）"""
    pass


class NetworkError(ThreeDPornDudeException):
    """网络请求错误"""
    pass


class ParseError(ThreeDPornDudeException):
    """解析HTML内容时发生错误"""
    pass


class RateLimitError(ThreeDPornDudeException):
    """请求频率限制"""
    pass


class CategoryNotFound(ThreeDPornDudeException):
    """分类未找到"""
    pass


class TagNotFound(ThreeDPornDudeException):
    """标签未找到"""
    pass


class NoResultsFound(ThreeDPornDudeException):
    """没有找到结果"""
    pass