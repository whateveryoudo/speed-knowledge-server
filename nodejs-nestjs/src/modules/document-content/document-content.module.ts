import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { DocumentContent } from "./entities/document-content.entity";
import { DocumentContentService } from "./document-content.service";
import { DocumentContentController } from "./document-content.controller";
import { CommonModule } from "../common/common.module";
import { DocumentModule } from "../document/document.module";
@Module({   
    imports: [TypeOrmModule.forFeature([DocumentContent]), CommonModule, DocumentModule],
    controllers: [DocumentContentController],
    providers: [DocumentContentService],
    exports: [DocumentContentService],
})
export class DocumentContentModule {}