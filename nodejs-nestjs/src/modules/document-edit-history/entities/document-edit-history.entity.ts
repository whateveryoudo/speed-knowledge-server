import {
  PrimaryColumn,
  Column,
  Entity,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  JoinColumn,
} from "typeorm";
import { DocumentBase } from "../../document/entities/document.entity";
import { User } from "../../user/entities/user.entity";

@Entity("document_edit_history")
export class DocumentEditHistory {
  @PrimaryColumn("varchar", { length: 36 })
  id: string;

  @Column("varchar", { length: 36 })
  document_id: string;


  @Column("integer", { nullable: false })
  edited_user_id: number;

  @Column("datetime", { nullable: false })
  edited_datetime: Date;

  @CreateDateColumn({ type: "datetime" })
  created_at: Date;

  @UpdateDateColumn({ type: "datetime" })
  updated_at: Date;

  @ManyToOne(() => DocumentBase, (document) => document.edit_histories)
  @JoinColumn({ name: "document_id", referencedColumnName: "id" })
  document: DocumentBase;

  @ManyToOne(() => User, (user) => user.edit_histories)
  @JoinColumn({ name: "edited_user_id", referencedColumnName: "id" })
  user: User;
}
