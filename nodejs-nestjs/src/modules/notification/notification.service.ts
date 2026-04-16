import { Injectable } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Repository } from "typeorm";
import { Notification } from "./entities/notification.entity";
import { type MentionItem } from "../collaboration/collaboration.service";
import { UserService } from "../user/user.service";
import { randomUUID } from "crypto";
import { NotificationBizType } from "@/enums/notification";
@Injectable()
export class NotificationService {
  constructor(
    @InjectRepository(Notification)
    private notificationRepository: Repository<Notification>,
    private userService: UserService,
  ) {}
  // 创建mention通知
  private async createMentionNotifications({
    document_id,
    actorUserId,
    addedMentionRows,
  }: {
    document_id: string;
    actorUserId: number;
    addedMentionRows: MentionItem[];
  }) {
    for (const mentionRow of addedMentionRows) {
      try {
        const bizId = `${document_id}:${mentionRow.mention_id}:${randomUUID()}`;
        const actorUser = await this.userService.findOne(actorUserId);
        const notification = this.notificationRepository.create({
          mentioned_user_id: mentionRow.payload.user_id,
          biz_type: NotificationBizType.MENTION,
          biz_id: bizId,
          title: "你被提及了",
          content: `用户${actorUser.username}在文档中@了你`,
          //  这里我可能需要联表查询文档所属的团队，知识库，空间（或者给前端，python端给个接口？）
          payload: {
            document_id,
            mention_id: mentionRow.mention_id,
            ...mentionRow.payload,
          } as Record<string, any>,
        });
        await this.notificationRepository.insert(notification);
        // TODO:WS推送
      } catch (error) {
        throw error;
      }
    }
  }
}
