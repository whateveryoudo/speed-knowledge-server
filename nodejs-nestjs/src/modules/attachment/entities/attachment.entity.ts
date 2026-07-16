import {
  Entity,
  PrimaryColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
} from "typeorm";
import { v4 as uuidv4 } from "uuid";

@Entity("attachment")
export class Attachment {
  @PrimaryColumn({ type: "varchar", length: 36 })
  id: string = uuidv4();

  @Column({ name: "file_name", length: 255 })
  fileName: string;

  @Column({ name: "file_type", length: 255 })
  fileType: string;

  @Column({ name: "object_name", length: 255 })
  objectName: string;

  @Column({ name: "file_size", type: "bigint" })
  fileSize: number;

  @Column({ name: "bucket_name", length: 255 })
  bucketName: string;

  @Column({ name: "user_id", type: "int" })
  userId: number;

  @CreateDateColumn({ name: "created_at" })
  createdAt: Date;

  @UpdateDateColumn({ name: "updated_at" })
  updatedAt: Date;
}
