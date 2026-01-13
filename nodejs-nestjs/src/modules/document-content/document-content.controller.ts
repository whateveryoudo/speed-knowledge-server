import { DocumentContentService } from "./document-content.service";
import {
  Controller,
  Body,
  Post,
  HttpException,
  HttpStatus,
} from "@nestjs/common";
import { TiptapTransformer } from "@hocuspocus/transformer";
import * as Y from "yjs";
import extensions from "../../tiptap-extends/kit";

@Controller("document-content")
export class DocumentContentController {
  constructor(
    private readonly documentContentService: DocumentContentService
  ) {}

  private getDefaultContent(title: string = "无标题文档"): {
    content: Buffer;
    node_json: string;
  } {
    const defaultJson: any = {
      type: "doc",
      content: [
        {
          type: "title",
          content: [
            {
              type: "text",
              text: title,
            },
          ],
        },
      ],
    };
    const ydoc = TiptapTransformer.toYdoc(defaultJson, "default", extensions);

    return {
      content: Buffer.from(Y.encodeStateAsUpdate(ydoc)),
      node_json: JSON.stringify({ default : defaultJson }), // 多包一层
    };
  }

  @Post("sync-title")
  async syncTitle(@Body() body: { documentId: string; newTitle: string }) {
    const { documentId, newTitle } = body;
    const documentContent =
      await this.documentContentService.getDocumentContent(documentId);
    if (!documentContent) {
      throw new HttpException(
        "Document content not found",
        HttpStatus.NOT_FOUND
      );
    }
    const nodeData = JSON.parse(documentContent.node_json);
    // 查找标题节点
    if (nodeData?.default?.content?.[0]?.type === "title") {
      const titleNode = nodeData.default.content[0];

      if (titleNode.content && titleNode.content.length > 0) {
        titleNode.content[0].text = newTitle;
      } else {
        titleNode.content = [{ text: newTitle }];
      }
    }
    // 更新json
    const updatedJson = JSON.stringify(nodeData);

    // 更新二进制

    const ydoc = new Y.Doc();
    Y.applyUpdate(ydoc, new Uint8Array(documentContent.content));
    // 2. 直接通过 Yjs API 修改 ydoc 中的标题
    // TipTap 使用 y-prosemirror，根节点是 'default'
    const root = ydoc.get("default", Y.XmlFragment);
    if (!root || root.length === 0) {
      throw new HttpException(
        "Document root not found",
        HttpStatus.BAD_REQUEST
      );
    }

    const firstChild = root.get(0) as Y.XmlElement;
    if (!firstChild || firstChild.nodeName !== "title") {
      throw new HttpException(
        "Title node not found in document content",
        HttpStatus.BAD_REQUEST
      );
    }

    // 删除所有现有内容
    const length = firstChild.length;
    if (length > 0) {
      firstChild.delete(0, length);
    }
    // 创建新的文本节点并插入
    const textNode = new Y.XmlText();
    textNode.insert(0, newTitle);
    firstChild.insert(0, [textNode]);

    const updatedBinary = Buffer.from(Y.encodeStateAsUpdate(ydoc));

    await this.documentContentService.updateContent(
      documentId,
      updatedBinary,
      updatedJson
    );
    // 保持和py一致
    return {
      success: true,
      errCode: 0,
      data: null,
      errMessage: "Title synced successfully",
    };
  }

  @Post("create-default")
  async createDefault(@Body() body: { documentId: string }) {
    const { documentId } = body;
    const documentContent = this.getDefaultContent();
    console.log(documentContent);
    await this.documentContentService.createContent(
      documentId,
      documentContent.content,
      documentContent.node_json
    );
    return {
      success: true,
      errCode: 0,
      data: null,
      errMessage: "Create default content successfully",
    };
  }
}
