import {
  PrimaryColumn,
  Column,
  Entity,
  CreateDateColumn,
  UpdateDateColumn,
} from "typeorm";

@Entity("document_content")
export class DocumentContent {
  @PrimaryColumn("varchar", { length: 36 })
  id: string;

  //   先定义为普通字段，优先完善协同的逻辑
  @Column("varchar", { length: 36 })
  document_id: string;

  @Column("longblob", { nullable: false })
  content: Buffer;

  @Column({ type: "datetime", nullable: true })
  content_updated_at: Date;

  @CreateDateColumn({ type: "datetime" })
  created_at: Date;

  @UpdateDateColumn({ type: "datetime" })
  updated_at: Date;
}
