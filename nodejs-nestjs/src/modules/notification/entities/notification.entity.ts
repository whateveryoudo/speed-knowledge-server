import { Entity, PrimaryColumn, Column, CreateDateColumn, UpdateDateColumn } from "typeorm";
import { NotificationBizType } from "@/enums/notification";

@Entity("notification")
export class Notification {
    @PrimaryColumn("varchar", { length: 36 })
    id: string;

    @Column("int")
    user_id: number;

    @Column("varchar", { length: 20 })
    biz_type: NotificationBizType;

    @Column("varchar", { length: 64 })
    biz_id: string;

    @Column("varchar", { length: 255 })
    title: string;

    @Column("text", { nullable: true })
    content: string | null;

    @Column("datetime", { nullable: true })
    read_at: Date | null;

    @Column("json", { nullable: true })
    payload: Record<string, any> | null;

    @CreateDateColumn({ type: "datetime" })
    created_at: Date;

    @UpdateDateColumn({ type: "datetime" })
    updated_at: Date;
}