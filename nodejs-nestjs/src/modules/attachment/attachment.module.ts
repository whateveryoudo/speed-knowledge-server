import { Module } from "@nestjs/common";
import { AttachmentService } from "./attachment.service";
import { MinioModule } from "../common/minio/minio.module";
import { TypeOrmModule } from "@nestjs/typeorm";
import { Attachment } from "./entities/attachment.entity";

@Module({
  imports: [MinioModule, TypeOrmModule.forFeature([Attachment])],
  providers: [AttachmentService],
  exports: [AttachmentService],
})
export class AttachmentModule {}
