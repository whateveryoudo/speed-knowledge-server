import {
  Entity,
  PrimaryColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from "typeorm";
import { IsEnum } from "class-validator";
import {
  NotificationBizType,
  NotificationListType,
} from "@/enums/notification";

@Entity("notification")
export class Notification {
  @PrimaryColumn("varchar", { length: 36 })
  id: string;

  @Column("int", { nullable: false, comment: "被提及用户id" })
  mentioned_user_id: number;

  @Column("int", { nullable: false, comment: "发起者用户id" })
  actor_user_id: number;

  @Column("varchar", { length: 20 })
  @IsEnum(NotificationBizType)
  biz_type: NotificationBizType;

  @Column("varchar", { length: 128 })
  biz_id: string;

  @Column("varchar", {
    length: 20,
    nullable: false,
    comment: "列表类型(用于分组展示)",
  })
  @IsEnum(NotificationListType)
  list_type: NotificationListType;

  @Column("datetime", { nullable: true })
  read_at: Date | null;

  @Column("json", { nullable: true })
  payload: Record<string, any> | null;

  @CreateDateColumn({ type: "datetime" })
  created_at: Date;

  @UpdateDateColumn({ type: "datetime" })
  updated_at: Date;
}
