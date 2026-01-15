import { Injectable, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcrypt';
import { UserService } from '../user/user.service';
import { User } from '../user/entities/user.entity';

@Injectable()
export class AuthService {
  constructor(
    private UserService: UserService,
    private jwtService: JwtService,
  ) {}

  async validateUser(email: string, password: string): Promise<any> {
    const user = await this.UserService.findByEmail(email);
    if (user && (await bcrypt.compare(password, user.password))) {
      const { password, ...result } = user;
      return result;
    }
    return null;
  }

  async login(user: User) {
    const payload = { email: user.email, sub: user.id };
    return {
      access_token: this.jwtService.sign(payload),
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
      },
    };
  }

  async verifyTokenAndGetUser(token: string) {
    const decoded = this.jwtService.verify(token.replace('Bearer ', ''));
    if (!decoded) {
      throw new UnauthorizedException('Invalid token');
    }
    const user = await this.UserService.findOne(decoded.sub);
    if (!user) {
      throw new UnauthorizedException('User not found');
    }
    return user;
  }
}
