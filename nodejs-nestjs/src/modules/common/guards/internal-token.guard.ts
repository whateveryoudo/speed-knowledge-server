import { CanActivate, ExecutionContext,  Injectable,  UnauthorizedException} from "@nestjs/common";

@Injectable()
export class InternalTokenGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const req = context.switchToHttp().getRequest();
    const token = req.headers['x-internal-token'];
    const expected = process.env.INTERNAL_SERVICE_TOKEN;
    if (!expected) {
      throw new UnauthorizedException('Internal token need  config');
    }
    if (!token ||token !== expected) {
      throw new UnauthorizedException('Internal token is invalid');
    }
    return true;
  }
}