import { TypeOrmModule } from "@nestjs/typeorm";
import { Notification } from "./entities/notification.entity";
import { NotificationService } from "./notification.service";
import { NotificationController } from "./notification.controller";
import { Module } from "@nestjs/common";
import { AuthModule } from "../auth/auth.module";
import { UserModule } from "../user/user.module";
import { NotificationGateway } from "./notification.getway";
@Module({
    imports: [TypeOrmModule.forFeature([Notification]), AuthModule, UserModule],
    controllers: [NotificationController],
    providers: [NotificationService, NotificationGateway],
    exports: [NotificationService],
})  
export class NotificationModule {}