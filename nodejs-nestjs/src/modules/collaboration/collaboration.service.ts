import { Injectable, OnModuleInit } from "@nestjs/common";
import { Hocuspocus } from "@hocuspocus/server";
import { ConfigService } from "@nestjs/config";
import { type WebSocket } from "ws";
import { Database } from "@hocuspocus/extension-database";
import { DocumentContentService } from "../document-content/document-content.service";
import { AuthService } from "../auth/auth.service";
@Injectable()
export class CollaborationService implements OnModuleInit {
  private hocuspocusServer: Hocuspocus;

  constructor(
    private documentContentService: DocumentContentService,
    private authService: AuthService
  ) {}

  onModuleInit() {
    const documentContentService = this.documentContentService;
    // 配置Hocuspocus服务器
    this.hocuspocusServer = new Hocuspocus({
      name: "Speed Editor Collaboration Server",
      onAuthenticate: async (context) => {
        console.log(context.token, 333);
        // token校验
        const token = context.token;
        if (!token) {
          throw new Error("Unauthorized: No token provided");
        }
        const decoded = await this.authService.verifyTokenAndGetUser(token);
        if (!decoded) {
          throw new Error("Unauthorized: Invalid token");
        }
        console.log(decoded);
        // 存入访问次数，增加到document_base表中
        return decoded;
      },
      extensions: [
        new Database({
          async fetch({ documentName }) {
            const content =
              await documentContentService.getContent(documentName);
            if (!content || content.length === 0) {
              return null;
            }
            return new Uint8Array(content);
          },
          async store({ documentName, state }) {
            await documentContentService.updateContent(
              documentName,
              Buffer.from(state)
            );
          },
        }),
      ],
    });
  }
  handleConnection(ws: WebSocket, request: any) {
    this.hocuspocusServer.handleConnection(ws, request);
  }
}
