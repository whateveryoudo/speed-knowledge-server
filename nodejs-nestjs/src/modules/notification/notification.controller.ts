import { NotificationService } from "./notification.service";
import { Controller } from "@nestjs/common";

@Controller("notification")
export class NotificationController {
    constructor(
        private notificationService: NotificationService,
    ) { }
}