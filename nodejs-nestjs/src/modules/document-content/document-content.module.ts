import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { DocumentContent } from "./entities/document-content.entity";
import { DocumentContentService } from "./document-content.service";
import { DocumentContentController } from "./document-content.controller";
import { CommonModule } from "../common/common.module";
@Module({   
    imports: [TypeOrmModule.forFeature([DocumentContent]), CommonModule],
    controllers: [DocumentContentController],
    providers: [DocumentContentService],
    exports: [DocumentContentService],
})
export class DocumentContentModule {}