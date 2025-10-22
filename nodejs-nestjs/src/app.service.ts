import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  getHello(): { message: string; timestamp: string } {
    return {
      message: 'Welcome to NestJS API Server!',
      timestamp: new Date().toISOString(),
    };
  }
}

