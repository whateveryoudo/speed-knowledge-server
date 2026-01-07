import { Injectable, NotFoundException } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Repository } from "typeorm";
import { DocumentBase } from "./entities/document.entity";
import { CreateDocumentDto } from "./dto/create-document.dto";
import { UpdateDocumentDto } from "./dto/update-document.dto";
@Injectable()
export class DocumentService {
  constructor(
    @InjectRepository(DocumentBase)
    private DocumentBaseRepository: Repository<DocumentBase>
  ) {}
  // 新增文档内容
  async createDocument(documentIn: CreateDocumentDto) {
    const DocumentBase = this.DocumentBaseRepository.create(documentIn);
    await this.DocumentBaseRepository.save(DocumentBase);
    return DocumentBase;
  }

  // 文档内容更新
  async updateDocument(id: string, documentIn: UpdateDocumentDto) {
    const DocumentBase = await this.DocumentBaseRepository.findOne({
      where: { id },
    });
    if (!DocumentBase) {
      throw new NotFoundException("Document content not found");
    }
    console.log(documentIn, 333);
    this.DocumentBaseRepository.merge(DocumentBase, documentIn);
    await this.DocumentBaseRepository.save(DocumentBase);
    return DocumentBase;
  }

  async getDocument(id: string) {
    const DocumentBase = await this.DocumentBaseRepository.findOne({
      where: { id },
    });
    if (!DocumentBase) {
      throw new NotFoundException("Document not found");
    }
    return DocumentBase;
  }

  async incrementViewCount(id: string): Promise<void> {
    await this.DocumentBaseRepository.increment({ id }, "view_count", 1);
  }
}
