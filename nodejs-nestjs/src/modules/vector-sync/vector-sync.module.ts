import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { VectorSync } from "./entities/vector-sync.entity";
import { VectorSyncService } from "./vector-sync.service";
import { VectorSyncWorker } from "./vector-sync.worker";
import { RabbitMQModule } from "../common/messaging/rabbitmq.module";

@Module({
    imports: [TypeOrmModule.forFeature([VectorSync]), RabbitMQModule],
    providers: [VectorSyncService, VectorSyncWorker],
    exports: [VectorSyncService],
})
export class VectorSyncModule { }