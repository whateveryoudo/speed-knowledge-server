from app.db.session import SessionLocal
from app.services.document_service import DocumentService
from app.ai.chains.index_chain import index_document_form_json
from typing import TypedDict

class DocumentContentUpdatedDict(TypedDict):
    document_id: str
    event_id: str
    knowledge_id: str
    content_updated_at: str


async def handle_document__content_updated(evt: DocumentContentUpdatedDict):
    """处理文档内容更新事件(接收到mq消息)"""
    print("开始执行其他操作,收到的消息是：", evt)
    with SessionLocal() as db:
        document_service = DocumentService(db)
        node_json = document_service.get_content(evt.get("document_id"))

        if node_json is None:
            raise ValueError(f"文档内容不存在")
        try:
            index_document_form_json(
                event_id=evt.get("event_id"),
                knowledge_id=evt.get("knowledge_id"),
                node_json=node_json,
                document_id=evt.get("document_id"),
                content_updated_at=evt.get("content_updated_at"),
            )
        except Exception as e:
            print(f"索引文档失败: {e}")
            raise e


ROUTES = {
    "document.content.updated": handle_document__content_updated,
}
