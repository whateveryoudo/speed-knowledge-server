import { Injectable, NotFoundException } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Repository } from "typeorm";
import { DocumentContent } from "./entities/document-content.entity";

@Injectable()
export class DocumentContentService {
  constructor(
    @InjectRepository(DocumentContent)
    private documentContentRepository: Repository<DocumentContent>
  ) {}
  // 获取文档内容
  async getDocumentContent(document_id: string) {
    const documentContent = await this.documentContentRepository.findOne({
      where: { document_id },
    });
    if (!documentContent) {
      throw new NotFoundException("Document content not found");
    }
    return documentContent;
  }
  // 新增文档内容
  async createContent(document_id: string, content: Buffer) {
    const documentContent = this.documentContentRepository.create({
      document_id,
      content,
    });
    await this.documentContentRepository.save(documentContent);
    return documentContent;
  }

  // 文档内容更新
  async updateContent(document_id: string, content: Buffer, node_json: string) {
    const documentContent = await this.documentContentRepository.findOne({
      where: { document_id },
    });
    if (!documentContent) {
      throw new NotFoundException("Document content not found");
    }

    // 这里先更新content_updated_at
    await this.documentContentRepository.update(
      {
        document_id,
      },
      { content_updated_at: new Date(), node_json,content }
    );
    console.log('更新成功');
  }

  async getContent(document_id: string) {
    const documentContent = await this.documentContentRepository.findOne({
      where: { document_id },
    });
    console.log(documentContent);
    if (!documentContent) {
      return null;
    }
    return documentContent.content;
  }
}
