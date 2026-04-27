import {
  NestInterceptor,
  ExecutionContext,
  BadRequestException,
  CallHandler,
  Injectable,
  Inject,
  ConflictException,
} from "@nestjs/common";
import { Observable, of, tap } from "rxjs";
import { CACHE_MANAGER } from "@nestjs/cache-manager";
import { Cache } from "cache-manager";

@Injectable()
export class IdempotencyInterceptor implements NestInterceptor {
  constructor(@Inject(CACHE_MANAGER) private cacheManager: Cache) {}
  async intercept(
    context: ExecutionContext,
    next: CallHandler,
  ): Promise<Observable<any>> {
    const request = context.switchToHttp().getRequest();
    const idemKey = request.headers["idempotency-key"];
    if (!idemKey) {
      throw new BadRequestException("Missing Idempotency-Key");
    }
    // TODO:换成redis的setnx操作

    const routerKey = `idem:${request.method}:${request.path}:${idemKey}`;

    const exists = await this.cacheManager.get(routerKey);
    if (exists) {
      throw new ConflictException("Idempotency-Key already processed");
    }

    await this.cacheManager.set(routerKey, "processing", 60 * 1000);

    return next.handle().pipe(
      tap(async () => {
        await this.cacheManager.set(routerKey, "success", 5 * 60 * 1000);
      }),
    );
  }
}
