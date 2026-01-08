from datetime import date
import json
from sqlalchemy.orm.session import Session
from app.models.document import Document, DocumentContent
from app.models.knowledge import Knowledge
from app.models.knowledge_daily_stats import KnowledgeDailyStats
from app.db.session import SessionLocal


def _count_words_from_node_json(node_json: str) -> int:
    """从node_json中统计字数(单个文档内容)"""
    try:
        data = json.loads(node_json)

    except Exception as e:
        print(f"统计字数失败: {e}")
        return 0

    def walk(node) -> int:
        if not isinstance(node, dict):
            return 0
        total = 0
        if node.get("type") == "text" and isinstance(node.get("text"), str):
            total += len(node.get("text"))
        for child in node.get("content", []) or []:
            total += walk(child)
        return total

    root = data.get("default") or data
    return walk(root)


def rebuild_daily_knowledge_stats():
    """重建每日知识统计:字数"""

    today = date.today()
    db: Session = SessionLocal()
    try:
        knowledge_ids = [k for (k,) in db.query(Knowledge.id).all()]
        for kid in knowledge_ids:
            word_total = 0
            document_with_json = (
                db.query(Document, DocumentContent)
                .join(DocumentContent, Document.id == DocumentContent.document_id)
                .all()
            )
            for _, content in document_with_json:
                if content.node_json:
                    word_count = _count_words_from_node_json(content.node_json)
                    word_total += word_count
            stat = (
                db.query(KnowledgeDailyStats)
                .filter(
                    KnowledgeDailyStats.knowledge_id == kid,
                    KnowledgeDailyStats.stats_date == today,
                )
                .first()
            )
            if not stat:
                new_stat = KnowledgeDailyStats(
                    knowledge_id=kid,
                    stats_date=today,
                    word_count=word_total,
                )
                db.add(new_stat)
        db.commit()
        print(f"知识统计任务成功: 字数总计{word_total}")
    except Exception as e:
        db.rollback()
        print(f"知识统计任务失败: {e}")
        raise e
    finally:
        db.close()
