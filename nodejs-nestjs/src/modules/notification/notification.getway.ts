import {
  OnGatewayConnection,
  WebSocketGateway,
  OnGatewayDisconnect,
  WebSocketServer,
} from "@nestjs/websockets";
import { AuthService } from "../auth/auth.service";
import { Socket } from "socket.io";
import { Logger } from "@nestjs/common";
import { Server } from "socket.io";

@WebSocketGateway({
  namespace: "/notification",
  cors: {
    origin: process.env.CORS_ORIGIN,
    credentials: true,
  },
})
export class NotificationGateway
  implements OnGatewayConnection, OnGatewayDisconnect
{
  @WebSocketServer()
  server: Server;

  private logger = new Logger(NotificationGateway.name);
  constructor(private readonly authService: AuthService) {}

  async handleConnection(client: Socket) {
    try {
      const token =
        (client.handshake.auth.token as string) ||
        client.handshake.headers.authorization;
      if (!token) {
        throw new Error("Token is required");
      }
      const user = await this.authService.verifyTokenAndGetUser(token);
      if (!user?.id) {
        throw new Error("Invalid token");
      }
      client.data.userId = user.id;
      await client.join(this.userRoom(user.id));
      this.logger.log(
        `joined room=${this.userRoom(user.id)} sid=${client.id} user=${user.id}`,
      );
    } catch (error) {
      client.disconnect();
      return;
    }
  }

  private userRoom(userId: number) {
    return `user:${userId}`;
  }

  handleDisconnect(client: Socket) {
    this.logger.log(`客户端断开: ${client.id}`);
  }
  emitToUser(userId: number, event: string, payload: any) {
    this.server.to(this.userRoom(userId)).emit(event, payload);
  }
}
