import { HttpException, HttpStatus, Injectable } from "@nestjs/common";
import { DocumentIOConverter, ImportFormat } from "./document-io.converter";
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
  }) {
    const { documentId, buffer, format, titleHint } = params;
    const docJson = await this.converter.convert(buffer, format, titleHint);
    // 包一层default
    const ydoc = TiptapTransformer.toYdoc(docJson, 'default', knowledgeKit);
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
      documentId
    };
  }
}
