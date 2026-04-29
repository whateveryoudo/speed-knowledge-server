import { NotificationService } from "./notification.service";
import { Controller, Post, UseGuards, UseInterceptors } from "@nestjs/common";
import { Body } from "@nestjs/common";
import { SendNotificationDto } from "./dto/send-notification.dto";
import { InternalTokenGuard } from "../common/guards/internal-token.guard";
import { IdempotencyInterceptor } from "../common/interceptors/idempotency.interceptor";

@Controller("notification")
export class NotificationController {
  constructor(private notificationService: NotificationService) {}

  // 发送站内信通知，提供给python端调用
  @UseGuards(InternalTokenGuard)
  @UseInterceptors(IdempotencyInterceptor)
  @Post("send")
  async sendNotification(@Body() body: SendNotificationDto) {
    return await this.notificationService.sendNotificationSingle(body);
  }
}
