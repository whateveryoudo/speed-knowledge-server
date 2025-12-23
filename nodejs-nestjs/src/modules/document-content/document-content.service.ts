import { Injectable, NotFoundException } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Repository } from "typeorm";
import { DocumentContent } from "./entities/document-content.entity";

@Injectable()
export class DocumentContentService {
    constructor(
        @InjectRepository(DocumentContent)
        private documentContentRepository: Repository<DocumentContent>,
    ) {}
    // 新增文档内容
    async createContent(document_id: string, content: Buffer) {
        const documentContent = this.documentContentRepository.create({ document_id, content });
        await this.documentContentRepository.save(documentContent);
        return documentContent;
    }

    // 文档内容更新
    async updateContent(document_id: string, content: Buffer) {
        const documentContent = await this.documentContentRepository.findOne({ where: { document_id } });
        if (!documentContent) {
            throw new NotFoundException('Document content not found');
        }
        documentContent.content = content;
        documentContent.content_updated_at = new Date();
        await this.documentContentRepository.save(documentContent);
        return documentContent;
    }

    async getContent(document_id: string) {
        const documentContent = await this.documentContentRepository.findOne({ where: { document_id } });
        console.log(documentContent)
        if (!documentContent) {
            return null;
        }
        return documentContent.content;
    }

}