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


class CollectResourceType(str, Enum):
    """收藏资源类型"""

    KNOWLEDGE = "knowledge"  # 知识库
    DOCUMENT = "document"  # 文档
