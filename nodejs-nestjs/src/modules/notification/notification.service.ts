import { Injectable } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Repository } from "typeorm";
import { Notification } from "./entities/notification.entity";
import { type MentionItem } from "../collaboration/collaboration.service";
import { UserService } from "../user/user.service";
import { NotificationBizType } from "@/enums/notification";
import { NotificationGateway } from "./notification.getway";
import * as dayjs from "dayjs";
import { v7 as uuidv7 } from 'uuid';
@Injectable()
export class NotificationService {
  constructor(
    @InjectRepository(Notification)
    private notificationRepository: Repository<Notification>,
    private userService: UserService,
    private notificationGateway: NotificationGateway,
  ) {}
  // 创建mention通知
  async createMentionNotifications({
    documentName,
    actorUserId,
    addedMentionRows,
    notificationEventId,
  }: {
    documentName: string;
    actorUserId: number;
    addedMentionRows: MentionItem[];
    notificationEventId: string;
  }) {
    for (const mentionRow of addedMentionRows) {
      try {
        // 这里直接用传入的事件id,不要每次都生成新的，TODO:mq接入
        const bizId = `${documentName}:${mentionRow.mention_id}:${notificationEventId}`;
        const actorUser = await this.userService.findOne(actorUserId);
        const notification = this.notificationRepository.create({
          id: uuidv7(),
          mentioned_user_id: mentionRow.payload.user_id,
          biz_type: NotificationBizType.MENTION,
          biz_id: bizId,
          title: "你被提及了",
          content: `用户${actorUser.username}在文档中@了你`,
          //  这里仅给出通知id,后端进行逻辑判断跳转
          payload: {
            mention_id: mentionRow.mention_id,
            ...mentionRow.payload,
          } as Record<string, any>,
        });
        try {
          await this.notificationRepository.insert(notification);
          console.log('notification', notification);
          this.notificationGateway.emitToUser(notification.mentioned_user_id, "notification", {
            id: notification.id,
            title: notification.title,
            content: notification.content,
            payload: notification.payload,
            created_at: dayjs().format('YYYY-MM-DD HH:mm:ss'),
          });
        } catch (error) {
          if (error?.code === 'ER_DUP_ENTRY') {
            return;
          }
          throw error;
        }
      } catch (error) {
        throw error;
      }
    }
  }
}
