import { Injectable, Logger } from "@nestjs/common";
import { VectorSync } from './entities/vector-sync.entity';
import { IsNull, LessThanOrEqual, Repository } from "typeorm";
import { randomUUID } from 'crypto'
import { InjectRepository } from "@nestjs/typeorm";
import { Cron, CronExpression } from "@nestjs/schedule";
import { RabbitMQPublisher } from "../common/messaging/rabbitmq.publisher";


@Injectable()
export class VectorSyncWorker {
    private readonly logger = new Logger(VectorSyncWorker.name);
    private isRunning = false;
    // private readonly POLL_WS = parseInt(process.env.VECTOR_SYNC_POLL_INTERVAL_MS || '1000', 10);
    constructor(
        @InjectRepository(VectorSync)
        private readonly repo: Repository<VectorSync>,
        private readonly rabbitMQPublisher: RabbitMQPublisher
    ) {
    }
    @Cron(CronExpression.EVERY_5_SECONDS)
    async handleCron() {
        if (this.isRunning) {
            return;
        }
        this.isRunning = true;
        try {
            await this.tick();
        } finally {
            this.isRunning = false;
        }
    }

    private async tick() {
        const now = new Date();
        const jobs = await this.repo.find({
            where: {
                next_run_at: LessThanOrEqual(now),
                locked_at: IsNull()
            },
            take: 50
        });
        if (jobs.length === 0) {
            return;
        }
        console.log('执行任务', jobs.length);
        for (const job of jobs) {
            const uuid = randomUUID();
            const locked = await this.repo.update({
                document_id: job.document_id,
                locked_at: IsNull()
            }, {
                locked_at: now,
                lock_token: uuid
            });
            if (!locked.affected) {
                continue
            }
            try {
                await this.rabbitMQPublisher.publishDocumentContentUpdated({
                    event_id: uuid,
                    knowledge_id: job.knowledge_id,
                    document_id: job.document_id,
                    content_updated_at: job.last_content_updated_at.toISOString()
                });
            } catch (error) {
                this.logger.error(`Failed to publish document content updated event, document_id: ${job.document_id}, error: ${error}`);
            } finally {
                await this.repo.delete({
                    document_id: job.document_id,
                })
            }
        }
    }
}