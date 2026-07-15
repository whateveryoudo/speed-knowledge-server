import { DocumentIOController } from "./document-io.controller";
import { Module } from "@nestjs/common";
import { DocumentIOService } from "./document-io.service";
import { CommonModule } from "../common/common.module";
import { DocumentContentModule } from "../document-content/document-content.module";
import { DocumentIOConverter } from "./document-io.converter";
@Module({
  imports: [CommonModule, DocumentContentModule],
  controllers: [DocumentIOController],
  providers: [DocumentIOService, DocumentIOConverter],
  exports: [],
})
export class DocumentIOModule {}
