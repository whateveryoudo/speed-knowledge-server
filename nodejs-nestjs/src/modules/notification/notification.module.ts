import { TypeOrmModule } from "@nestjs/typeorm";
import { Notification } from "./entities/notification.entity";
import { NotificationService } from "./notification.service";
import { NotificationController } from "./notification.controller";
import { Module } from "@nestjs/common";

@Module({
    imports: [TypeOrmModule.forFeature([Notification])],
    controllers: [NotificationController],
    providers: [NotificationService],
    exports: [NotificationService],
})  
export class NotificationModule {}