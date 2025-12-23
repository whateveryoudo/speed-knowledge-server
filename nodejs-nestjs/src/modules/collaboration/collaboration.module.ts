import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { DocumentContent } from "../document-content/entities/document-content.entity";
import { CollaborationService } from "./collaboration.service";
import { CollaborationGateway } from "./collaboration.gateway";
import { DocumentContentModule } from "../document-content/document-content.module";
@Module({
  imports: [TypeOrmModule.forFeature([DocumentContent]), DocumentContentModule],
  controllers: [],
  providers: [CollaborationService, CollaborationGateway],
  exports: [CollaborationService],
})
export class CollaborationModule {}
