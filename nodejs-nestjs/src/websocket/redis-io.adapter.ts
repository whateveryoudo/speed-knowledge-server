import { IoAdapter} from '@nestjs/platform-socket.io'
import { INestApplication } from '@nestjs/common'
import { createAdapter} from '@socket.io/redis-adapter'
import Redis from 'ioredis'
import { ServerOptions } from 'socket.io'

export class RedisIoAdapter extends IoAdapter {
  private adapterConstructor: ReturnType<typeof createAdapter>;
  constructor(app: INestApplication) {
    super(app);
  }

  async connectToRedis(): Promise<void> {
    const host = (process.env.REDIS_HOST || 'localhost').replace(/"/g, '');
    const port = process.env.REDIS_PORT || '6379';
    const redisUrl = `redis://${host}:${port}`;
    if (!redisUrl) {
      throw new Error('Redis URL is not set');
    }
    const pubClient = new Redis(redisUrl);
    const subClient = pubClient.duplicate();

    await Promise.all([
      new Promise((resolve, reject) => {
        pubClient.on('connect', resolve);
        pubClient.on('error', reject);
      }),
      new Promise((resolve, reject) => {
        subClient.on('connect', resolve);
        subClient.on('error', reject);
      }),
    ]);

    this.adapterConstructor = createAdapter(pubClient, subClient);
  }

  createIOServer(port: number, options?: ServerOptions) {
    const origin = process.env.CORS_ORIGIN || 'http://localhost:5173';
    const allowCredentials = origin !== '*';
    const server = super.createIOServer(port, {
      ...options,
      cors: {
        origin,
        credentials: allowCredentials,
      },
    });
    if (!this.adapterConstructor) {
      throw new Error('Redis adapter not initialized');
    }
    server.adapter(this.adapterConstructor);
    return server;
  }
}