import { Injectable, NotFoundException } from "@nestjs/common";
import { MinioService } from "../common/minio/minio.service";
import { Attachment } from "./entities/attachment.entity";
import { Repository } from "typeorm";
import { InjectRepository } from "@nestjs/typeorm";
import { v4 as uuidv4 } from "uuid";

@Injectable()
export class AttachmentService {
  constructor(
    @InjectRepository(Attachment)
    private readonly attachmentRepo: Repository<Attachment>,
    private readonly minioService: MinioService,
  ) {}

  async uploadBuffer(params: {
    buffer: Buffer;
    fileName: string;
    contentType: string;
    userId: number;
  }): Promise<Attachment> {
    const { buffer, fileName, contentType, userId } = params;
    const objectName = `${userId}/${uuidv4()}_${fileName}`;
    // 存入minio
    const { bucketName } = await this.minioService.putObject({
      objectName,
      buffer,
      contentType,
    });
    const attachment = this.attachmentRepo.create({
      id: uuidv4(),
      fileName,
      fileType: contentType,
      objectName,
      fileSize: buffer.length,
      bucketName,
      userId,
    });

    return this.attachmentRepo.save(attachment);
  }

  async getBufferById(id: string): Promise<{
    buffer: Buffer;
    contentType: string;
  }> {
    const attachment = await this.attachmentRepo.findOne({ where: { id } });
    if (!attachment) {
      throw new NotFoundException("Attachment not found");
    }
    return {
      buffer: await this.minioService.getObject({ 
        objectName: attachment.objectName,
        bucketName: attachment.bucketName,
      }),
      contentType: attachment.fileType || "image/png",
    } 
  }
}
