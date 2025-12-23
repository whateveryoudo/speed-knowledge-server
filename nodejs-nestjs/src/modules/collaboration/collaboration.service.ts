import { Injectable, OnModuleInit } from "@nestjs/common";
import { Hocuspocus } from "@hocuspocus/server";
import { ConfigService } from "@nestjs/config";
import { type WebSocket } from "ws";
import { Database } from "@hocuspocus/extension-database";
import { DocumentContentService } from "../document-content/document-content.service";
@Injectable()
export class CollaborationService implements OnModuleInit {
  private hocuspocusServer: Hocuspocus;

  constructor(private documentContentService: DocumentContentService) {}

  onModuleInit() {
    const documentContentService = this.documentContentService;
    // 配置Hocuspocus服务器
    this.hocuspocusServer = new Hocuspocus({
      name: "Speed Editor Collaboration Server",
      // authentication: {
      //     async token(context) {
      //         return {
      //             documentName: context.documentName,
      //         };
      //     }
      // }
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
            console.log(documentName, state);
            await documentContentService.updateContent(
              documentName,
              Buffer.from(state)
            );
          },
        }),
      ],
    });
  }

  handleConnection(ws: WebSocket, request: any, context: any) {
    console.log(context);
    this.hocuspocusServer.handleConnection(ws, request, context);
  }
}
