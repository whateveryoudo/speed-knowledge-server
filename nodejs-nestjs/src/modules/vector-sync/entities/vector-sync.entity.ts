import { Entity, PrimaryColumn, Column, Index, UpdateDateColumn } from "typeorm";

@Entity("vector_sync")
export class VectorSync {
    @PrimaryColumn({type: "varchar", length: 36 })
    document_id: string;

    @Column({type: "varchar", length: 36 })
    knowledge_id: string;

    @Column({type: "datetime", precision: 3 })
    last_content_updated_at: Date;

    @Index()
    @Column({type: "datetime", precision: 3 })
    next_run_at: Date;

    @Index()
    @Column({type: "datetime", precision: 3, nullable: true, default: null })
    locked_at: Date | null;

    @Column({type: "varchar", length: 36, nullable: true,default: null })
    lock_token: string | null;

    @UpdateDateColumn({ type: "datetime", precision: 3 })
    updated_at: Date;
}