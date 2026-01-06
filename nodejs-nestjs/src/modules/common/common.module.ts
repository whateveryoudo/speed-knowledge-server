import { Module } from "@nestjs/common";
import { StrongPasswordValidator } from "../../utils/validators/strong-password.validator";

@Module({
  providers: [StrongPasswordValidator],
  exports: [StrongPasswordValidator],
})
export class CommonModule {}
