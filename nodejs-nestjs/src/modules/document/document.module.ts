import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { DocumentBase } from "./entities/document.entity";
import { DocumentService } from "./document.service";
@Module({   
    imports: [TypeOrmModule.forFeature([DocumentBase])],
    controllers: [],
    providers: [DocumentService],
    exports: [DocumentService],
})
export class DocumentModule {}