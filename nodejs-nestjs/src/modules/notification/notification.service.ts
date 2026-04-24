import { Injectable } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { IsNull, Repository } from "typeorm";
import { Notification } from "./entities/notification.entity";
import { type MentionItem } from "../collaboration/collaboration.service";
import { NotificationBizType } from "@/enums/notification";
import { NotificationGateway } from "./notification.getway";

import * as dayjs from "dayjs";
import { v7 as uuidv7 } from 'uuid';
@Injectable()
export class NotificationService {
  constructor(
    @InjectRepository(Notification)
    private notificationRepository: Repository<Notification>,
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
        // 这里查库， 在py端拿着id再去查
        // const actorUser = await this.userService.findOne(actorUserId);
        const notification = this.notificationRepository.create({
          id: uuidv7(),
          mentioned_user_id: mentionRow.payload.user_id,
          biz_type: NotificationBizType.MENTION,
          biz_id: bizId,
          actor_user_id: actorUserId,
          //  存入一些额外信息
          payload: {
            document_id: documentName,
            mention_id: mentionRow.mention_id,
            ...mentionRow.payload,
          } as Record<string, any>,
        });
        try {
          await this.notificationRepository.save(notification);
          const unreadCount = await this.notificationRepository.count({
            where: {
              mentioned_user_id: notification.mentioned_user_id,
              read_at: IsNull(),
            },
          });
          // 这里推送不要写带太多信息（仅返回unreadCount）
          this.notificationGateway.emitToUser(notification.mentioned_user_id, "notification", {
            unreadCount
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
