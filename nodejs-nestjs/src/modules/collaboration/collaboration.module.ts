import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { DocumentContent } from "../document-content/entities/document-content.entity";
import { CollaborationService } from "./collaboration.service";
import { CollaborationGateway } from "./collaboration.gateway";
import { DocumentContentModule } from "../document-content/document-content.module";
import { AuthModule } from "../auth/auth.module";
import { DocumentModule } from "../document/document.module";
import { VectorSyncModule } from "../vector-sync/vector-sync.module";
import { NotificationModule } from "../notification/notification.module";
import { HttpModule } from "@nestjs/axios";
import { DocumentEditHistoryModule } from "../document-edit-history/document-edit-history.module";
@Module({
  imports: [
    TypeOrmModule.forFeature([DocumentContent]),
    DocumentContentModule,
    AuthModule,
    DocumentModule,
    DocumentEditHistoryModule,
    VectorSyncModule,
    NotificationModule,
    HttpModule.register({
      timeout: 5000,
      maxRedirects: 5,
    }),
  ],
  controllers: [],
  providers: [CollaborationService, CollaborationGateway],
  exports: [CollaborationService],
})
export class CollaborationModule {}
