import { HttpException, HttpStatus, Injectable } from "@nestjs/common";
import {
  DocumentIOConverter,
  type ImportFormat,
  type ExportFormat,
} from "./document-io.converter";
import { DocumentContentService } from "../document-content/document-content.service";
import * as Y from "yjs";
import { knowledgeKit } from "@speed-tiptap-editor/schema";
import { TiptapTransformer } from "@hocuspocus/transformer";
@Injectable()
export class DocumentIOService {
  constructor(
    private readonly converter: DocumentIOConverter,
    private readonly documentContentService: DocumentContentService,
  ) {}

  async importToDocument(params: {
    documentId: string;
    buffer: Buffer;
    format: ImportFormat;
    titleHint: string;
    userId: number;
  }) {
    const { documentId, buffer, format, titleHint, userId } = params;
    const docJson = await this.converter.convert(
      buffer,
      format,
      titleHint,
      userId,
    );
    // 包一层default
    const ydoc = TiptapTransformer.toYdoc(docJson, "default", knowledgeKit);
    const nodeJson = JSON.stringify({ default: docJson });
    // 转换为二进制
    const binary = Buffer.from(Y.encodeStateAsUpdate(ydoc));

    // 调用文档内容创建服务
    await this.documentContentService.createContent(
      documentId,
      binary,
      nodeJson,
    );
    return {
      documentId,
    };
  }

  async exportDocument(params: {
    documentId: string;
    format: ExportFormat;
    fileName?: string;
  }) {
    const { documentId, format, fileName } = params;
    const contentRow =
      await this.documentContentService.getDocumentContent(documentId);
    if (!contentRow || !contentRow.node_json) {
      throw new HttpException(
        "Document content not found",
        HttpStatus.NOT_FOUND,
      );
    }
    return this.converter.exportFormDocJson({
      docJson: JSON.parse(contentRow.node_json),
      format,
      fileName,
    });
  }
}
