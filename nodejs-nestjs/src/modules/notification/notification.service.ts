import { Injectable } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { IsNull, Repository } from "typeorm";
import { Notification } from "./entities/notification.entity";
import { type MentionItem } from "../collaboration/collaboration.service";
import { NotificationBizType } from "@/enums/notification";
import { NotificationGateway } from "./notification.getway";
import { SendNotificationDto } from "./dto/send-notification.dto";
import { v7 as uuidv7 } from "uuid";
import { bizType2ListTypeMap } from "@/enums/notification";
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
        const bizId = `${documentName}:${mentionRow.mention_id}:${notificationEventId}`;
        await this.sendNotificationSingle({
          mentionedUserId: mentionRow.payload.userId,
          bizType: NotificationBizType.MENTION,
          bizId,
          actorUserId,
          payload: {
            document_id: documentName,
            mention_id: mentionRow.mention_id,
            ...mentionRow.payload,
          },
        });
      } catch (error) {
        throw error;
      }
    }
  }
  // 单条站内信发送（包含落库 & 站内信推送）
  async sendNotificationSingle({
    mentionedUserId,
    bizType,
    bizId,
    actorUserId,
    payload,
  }: SendNotificationDto) {
    // 这里直接用传入的事件id,不要每次都生成新的，TODO:mq接入
    // 这里查库， 在py端拿着id再去查
    // const actorUser = await this.userService.findOne(actorUserId);
    const listType = bizType2ListTypeMap[bizType];
    if (!listType) {
      throw new Error(`Invalid bizType: ${bizType}`);
    }
    const notification = this.notificationRepository.create({
      id: uuidv7(),
      mentioned_user_id: mentionedUserId,
      biz_type: bizType,
      list_type: listType,
      biz_id: bizId,
      actor_user_id: actorUserId,
      //  存入一些额外信息
      payload: (payload || {}) as Record<string, any>,
      // 这里需要显示传入日期，是走的 python初始化 表，数据库层面没兜底
      created_at: new Date(),
      updated_at: new Date(),
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
      this.notificationGateway.emitToUser(
        notification.mentioned_user_id,
        "notification",
        {
          unreadCount,
        },
      );
    } catch (error) {
      if (error?.code === "ER_DUP_ENTRY") {
        return;
      }
      throw error;
    }
  }
}
