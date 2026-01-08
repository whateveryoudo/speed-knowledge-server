import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { DocumentContent } from "./entities/document-content.entity";
import { DocumentContentService } from "./document-content.service";
import { DocumentContentController } from "./document-content.controller";
@Module({   
    imports: [TypeOrmModule.forFeature([DocumentContent])],
    controllers: [DocumentContentController],
    providers: [DocumentContentService],
    exports: [DocumentContentService],
})
export class DocumentContentModule {}