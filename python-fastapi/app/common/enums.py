"""枚举类"""
from enum import Enum


class AIAction(str, Enum):
    """AI 动作"""
    REFACOTR = "refactor"  # 重构
    CHECK = "check"  # 检查
    SIMPLE = "simple"  # 简洁
    RICH = "rich"  # 丰富
    TRANSLATE = "translate"  # 翻译
    SUMMARY = "summary"  # 总结
    CUSTOM = "custom"  # 自定义
# ==================== 知识库分组相关枚举 ====================

AIActionPromptDict = {
    AIAction.REFACOTR: "你是一位专业的写作助手。请改进以下文本，使其更加流畅、专业和易读。保持原意，只输出改进后的文本内容，不要添加任何解释。",
    AIAction.CHECK: "你是一位语法检查专家。请检查以下文本的拼写和语法错误，并直接输出修正后的文本。如果没有错误，输出原文。",
    AIAction.SIMPLE: "你是一位内容编辑。请将以下文本简化，使其更加简洁明了，保留核心意思。只输出简化后的文本。",
    AIAction.RICH: "你是一位内容创作者。请丰富以下文本内容，添加更多细节和描述，使其更加生动具体。只输出丰富后的文本。",
    AIAction.TRANSLATE: "你是一位翻译专家。如果文本是中文，翻译成英文；如果是英文，翻译成中文。只输出翻译结果。",
    AIAction.SUMMARY: "你是一位总结专家。请总结以下文本的核心要点，用简洁的语言概括主要内容。只输出总结内容。",
    AIAction.CUSTOM: "请处理以下文本：",
}

class KnowledgeIndexPageLayout(str, Enum):
    """知识库文档树首页视图"""
    CATALOG = "catalog"  # 目录视图
    CARD = "card"  # 卡片视图
    COLUMN = "column"  # 专栏视图

class KnowledgeIndexPageSort(str, Enum):
    """知识库文档树首页排序"""
    CATALOG = "catalog"  # 目录排序
    CREATE_TIME = "create_time"  # 创建时间
    UPDATE_TIME = "update_time"  # 更新时间
    LIKE_COUNT = "like_count"  # 点赞次数

class KnowledgeGroupType(str, Enum):
    """知识库布局模式"""
    CARD = "card"  # 卡片布局
    LIST = "list"  # 列表布局


class KnowledgeGroupStyle(str, Enum):
    """知识库卡片样式"""
    SIMPLE = "simple"  # 简洁
    BASIC = "basic"  # 基础
    DETAIL = "detail"  # 详情
    IMAGE = "image"  # 图片

class DocumentHistoryType(str, Enum):
    """文档历史类型"""
    VIEW = "view"  # 浏览
    EDIT = "edit"  # 编辑
    LIKE = "like"  # 点赞
    COLLECT = "collect"  # 收藏

class DocumentType(str, Enum):
    """文档类型:目前仅支持word"""
    WORD = "word"  # Word

class DocumentNodeDragAction(str, Enum):
    """文档节点拖拽动作"""
    MOVE_AFTER = "moveAfter"  # 移动到目标节点后
    MOVE_BEFORE = "moveBefore"  # 移动到目标节点前
    PREPEND_CHILD = "prependChild"  # 插入到目标节点前

class DocumentNodeType(str, Enum):
    """文档节点类型"""
    TITLE = "TITLE"  # 目录
    DOC = "DOC"  # 文档节点


# ==================== 知识库协同相关 ====================

class KnowledgeCollaboratorRole(int, Enum):
    """知识库协同权限"""
    READ = 1  # 只读(浏览文档 & 评论文档)
    EDIT = 2  # 编辑
    ADMIN = 3  # 管理员

class KnowledgeCollaboratorStatus(int, Enum):
    """知识库协作者状态"""
    PENDING = 1  # 申请加入中
    ACCEPTED = 2  # 已加入    

class KnowledgeCollaboratorSource(int, Enum):
    """知识库协作者来源"""
    CREATOR = 0  # 创建者
    INVITATION = 1  # 邀请链接加入
    SEARCH_JOIN = 2  # 搜索加入

class KnowledgeInvitationStatus(int, Enum):
    """知识库邀请链接状态"""
    ACTIVE = 1  # 正常
    REVOKED = 2  # 已撤销

class CollectResourceType(str, Enum):
    """收藏资源类型"""
    KNOWLEDGE = "knowledge"  # 知识库
    DOCUMENT = "document"  # 文档