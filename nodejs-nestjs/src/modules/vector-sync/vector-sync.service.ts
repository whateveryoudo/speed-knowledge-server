import { Injectable } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Repository } from "typeorm";
import { VectorSync } from "./entities/vector-sync.entity";

@Injectable()
export class VectorSyncService {
    private readonly DOBOUNCE_MS = parseInt(process.env.VECTOR_SYNC_DOBOUNCE_MS || '2000', 10);
    constructor(
        @InjectRepository(VectorSync)
        private readonly repo: Repository<VectorSync>,
    ) {

    }

    async touch(knowledge_id: string, document_id: string) {
        console.log('touch', knowledge_id, document_id);
        const now = new Date();
        const nextRunAt = new Date(now.getTime() + this.DOBOUNCE_MS);
        await this.repo.upsert({
            knowledge_id,
            document_id,
            last_content_updated_at: now,
            next_run_at: nextRunAt,
        }, ["document_id"]);
    }
}