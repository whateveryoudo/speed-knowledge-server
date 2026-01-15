import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { DocumentEditHistory } from "./entities/document-edit-history.entity";
import { DocumentEditHistoryService } from "./document-edit-history.service";
@Module({   
    imports: [TypeOrmModule.forFeature([DocumentEditHistory])],
    controllers: [],
    providers: [DocumentEditHistoryService],
    exports: [DocumentEditHistoryService],
})
export class DocumentEditHistoryModule {}