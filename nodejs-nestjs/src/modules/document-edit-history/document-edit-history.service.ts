import { Injectable } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Repository } from "typeorm";
import { DocumentEditHistory } from "./entities/document-edit-history.entity";
import { CreateDocumentEditHistoryDto } from "./dto/document-edit-history.dto";
import { v4 as uuidv4 } from "uuid";
@Injectable()
export class DocumentEditHistoryService {
  constructor(
    @InjectRepository(DocumentEditHistory)
    private DocumentEditHistoryRepository: Repository<DocumentEditHistory>
  ) {}
  // 新增文档编辑历史（这里不写查询：查询逻辑在python端，这里只是为了不node调用python）
  async create(document_edit_history_in: CreateDocumentEditHistoryDto) {
    // 判断当前记录是不是有了
    const existingRecord = await this.DocumentEditHistoryRepository.findOne({
      where: {
        document_id: document_edit_history_in.document_id,
        edited_user_id: document_edit_history_in.edited_user_id,
      },
    });
    if (existingRecord) { // 存在则不新增
      return existingRecord;
    }
    const DocumentEditHistory = this.DocumentEditHistoryRepository.create({
      id: uuidv4(),
      document_id: document_edit_history_in.document_id,
      edited_user_id: document_edit_history_in.edited_user_id,
      edited_datetime: document_edit_history_in.edited_datetime,
    });
    await this.DocumentEditHistoryRepository.save(DocumentEditHistory);
    return DocumentEditHistory;
  }
}
