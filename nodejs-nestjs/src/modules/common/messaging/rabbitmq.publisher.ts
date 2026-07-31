import { Injectable, OnModuleDestroy, OnModuleInit, Logger } from "@nestjs/common";
import * as amqplib from 'amqplib';

export type DocumentContentUpdatedEvent = {
    event_id: string;
    knowledge_id: string;
    document_id: string;
    content_updated_at: string;
}

function isRabbitMqEnabled(): boolean {
    const raw = (process.env.ENABLE_RABBITMQ || 'true').trim().toLowerCase();
    return raw === 'true' || raw === '1' || raw === 'yes';
}

@Injectable()
export class RabbitMQPublisher implements OnModuleInit, OnModuleDestroy {
    private readonly logger = new Logger(RabbitMQPublisher.name);
    private readonly enabled = isRabbitMqEnabled();

    private conn: amqplib.ChannelModel | null = null;
    private ch: amqplib.Channel | null = null;
    private readonly routingKey: string = process.env.RABBITMQ_ROUTING_KEY || 'document.content.updated';
    private readonly exchange: string = process.env.RABBITMQ_EXCHANGE || 'speed_knowledge.events';

    isEnabled(): boolean {
        return this.enabled;
    }

    private async connect() {
        const url = process.env.RABBITMQ_URL;
        if (!url) {
            throw new Error('RABBITMQ_URL is not set');
        }
        this.conn = await amqplib.connect(url);
        if (!this.conn) {
            throw new Error('Failed to connect to RabbitMQ');
        }
        this.conn.on('error', (err: any) => {
            console.error('RabbitMQ connection error:', err);
        });
        this.conn.on('close', () => {
            console.error('RabbitMQ connection closed');
        });

        this.ch = await this.conn.createChannel();
        await this.ch.assertExchange(this.exchange, 'topic', { durable: true });

        this.logger.log(`RabbitMQ connected, exchange: ${this.exchange}`);
    }
    async onModuleInit() {
        if (!this.enabled) {
            this.logger.warn('RabbitMQ disabled (ENABLE_RABBITMQ=false), skip connect');
            return;
        }
        await this.connect();
    }
    async onModuleDestroy() {
        await this.ch?.close();
        await this.conn?.close();
    }

    // 对外提供方法
    async publishDocumentContentUpdated(evt: DocumentContentUpdatedEvent) {
        if (!this.enabled) {
            this.logger.debug(`RabbitMQ disabled, skip publish: ${evt.document_id}`);
            return;
        }
        if (!this.ch) {
            await this.connect();
        }
        const body = Buffer.from(JSON.stringify(evt));
        const ok = this.ch!.publish(this.exchange, this.routingKey, body, {
            contentType: 'application/json',
            contentEncoding: 'utf-8',
            persistent: true,
            mandatory: true,
        });

        if (!ok) {
            this.logger.error(`Failed to publish document content updated event, exchange: ${this.exchange}, routingKey: ${this.routingKey}, event: ${JSON.stringify(evt)}`);
        }
    }

}
