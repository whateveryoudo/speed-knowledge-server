import {
  PrimaryColumn,
  Column,
  Entity,
  CreateDateColumn,
  UpdateDateColumn,
  OneToOne,
  JoinColumn,
} from "typeorm";
import { DocumentBase } from "../../document/entities/document.entity";

@Entity("document_content")
export class DocumentContent {
  @PrimaryColumn("varchar", { length: 36 })
  id: string;

  @Column("varchar", { length: 36 })
  document_id: string;

  @Column("longblob", { nullable: false })
  content: Buffer;

  @Column("text", { nullable: true })
  node_json: string;

  @Column({ type: "datetime", nullable: true })
  content_updated_at: Date;

  @CreateDateColumn({ type: "datetime" })
  created_at: Date;

  @UpdateDateColumn({ type: "datetime" })
  updated_at: Date;

  @OneToOne(() => DocumentBase, (document) => document.content)
  @JoinColumn({ name: "document_id", referencedColumnName: "id" })
  document: DocumentBase;
}
