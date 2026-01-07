import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { DocumentContent } from "../document-content/entities/document-content.entity";
import { CollaborationService } from "./collaboration.service";
import { CollaborationGateway } from "./collaboration.gateway";
import { DocumentContentModule } from "../document-content/document-content.module";
import { AuthModule } from "../auth/auth.module";
import { DocumentModule } from "../document/document.module";
@Module({
  imports: [
    TypeOrmModule.forFeature([DocumentContent]),
    DocumentContentModule,
    AuthModule,
    DocumentModule,
  ],
  controllers: [],
  providers: [CollaborationService,  CollaborationGateway],
  exports: [CollaborationService],
})
export class CollaborationModule {}
