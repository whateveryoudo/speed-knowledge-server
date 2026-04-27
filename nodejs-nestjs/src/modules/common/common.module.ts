import { Module } from "@nestjs/common";
import { StrongPasswordValidator } from "../../utils/validators/strong-password.validator";
import { IdempotencyInterceptor } from "./interceptors/idempotency.interceptor";
import { InternalTokenGuard } from "./guards/internal-token.guard";
@Module({
  providers: [
    StrongPasswordValidator,
    IdempotencyInterceptor,
    InternalTokenGuard,
  ],
  exports: [
    StrongPasswordValidator,
    IdempotencyInterceptor,
    InternalTokenGuard,
  ],
})
export class CommonModule {}
