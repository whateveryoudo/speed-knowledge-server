import {
  PrimaryColumn,
  Column,
  Entity,
  CreateDateColumn,
  UpdateDateColumn,
  OneToOne,
  JoinColumn,
} from "typeorm";
import { DocumentContent } from "../../document-content/entities/document-content.entity";

@Entity("document_base")
export class DocumentBase {
  @PrimaryColumn("varchar", { length: 36 })
  id: string;

  @Column("varchar", { length: 36 })
  user_id: string;

  @Column("varchar", { length: 36 })
  knowledge_id: string;

  @Column("varchar", { length: 128 })
  name: string;
  
  @Column("varchar", { length: 64 })
  slug: string;

  @Column("varchar", { length: 10 })
  type: string;

  @Column("boolean", { default: false })
  is_public: boolean;

  @Column("int", { default: 0 })
  view_count: number;

  @Column("datetime", { nullable: true })
  content_updated_at: Date;

  @CreateDateColumn({ type: "datetime" })
  created_at: Date;

  @UpdateDateColumn({ type: "datetime" })
  updated_at: Date;

  @OneToOne(() => DocumentContent, (content) => content.document, { cascade: true })
  content: DocumentContent;
}
