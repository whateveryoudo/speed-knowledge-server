import { Injectable, OnModuleInit, Inject } from "@nestjs/common";
import { Hocuspocus } from "@hocuspocus/server";
import { ConfigService } from "@nestjs/config";
import { type WebSocket } from "ws";
import { Database } from "@hocuspocus/extension-database";
import { TiptapTransformer } from "@hocuspocus/transformer";
import { DocumentContentService } from "../document-content/document-content.service";
import { DocumentEditHistoryService } from "../document-edit-history/document-edit-history.service";
import { AuthService } from "../auth/auth.service";
import { DocumentService } from "../document/document.service";
import { CACHE_MANAGER } from "@nestjs/cache-manager";
import { Cache } from "cache-manager";
import * as Y from "yjs";
@Injectable()
export class CollaborationService implements OnModuleInit {
  private hocuspocusServer: Hocuspocus;
  private readonly VIEW_COUNT_TTL = 3600 * 24;

  constructor(
    private documentContentService: DocumentContentService,
    private documentEditHistoryService: DocumentEditHistoryService,
    private authService: AuthService,
    private documentService: DocumentService,
    @Inject(CACHE_MANAGER) private cacheManager: Cache
  ) {}
  private async syncViewCount(documentId: string, userId: number) {
    const cacheKey = `document_view_count:${documentId}:${userId}`;
    const cacheValue = await this.cacheManager.get(cacheKey);
    if (cacheValue) {
      return cacheValue;
    }

    await this.cacheManager.set(cacheKey, "1", this.VIEW_COUNT_TTL * 1000);

    try {
      await this.documentService.incrementViewCount(documentId);
    } catch (error) {
      await this.cacheManager.del(cacheKey);
      console.error("Failed to increment view count");
    }
  }
  private async yStateToPmJson(state: Uint8Array) {
    const ydoc = new Y.Doc();
    // 把二进制更新应用到 ydoc
    Y.applyUpdate(ydoc, state);
    // TiptapTransformer.extensions(extensions as any);
    // 从 ydoc 提取 ProseMirror JSON（默认根类型名是 'content'，保持与你写入时一致）
    const pmJson = TiptapTransformer.fromYdoc(ydoc as any);
    return pmJson;
  }

  onModuleInit() {
    const documentContentService = this.documentContentService;
    const documentService = this.documentService;
    const documentEditHistoryService = this.documentEditHistoryService;
    const yStateToPmJson = this.yStateToPmJson;
    // 配置Hocuspocus服务器
    this.hocuspocusServer = new Hocuspocus({
      name: "Speed Editor Collaboration Server",
      onAuthenticate: async (context) => {
        // token校验
        const token = context.token;
        if (!token) {
          throw new Error("Unauthorized: No token provided");
        }
        const decoded = await this.authService.verifyTokenAndGetUser(token);
        if (!decoded) {
          throw new Error("Unauthorized: Invalid token");
        }
        // 存入访问次数，增加到document_base表中
        this.syncViewCount(context.documentName, decoded.id);
        return {
          user: decoded,
        };
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
          async store({ documentName, state, context }) {
            const node = await yStateToPmJson(state);
            await documentContentService.updateContent(
              documentName,
              Buffer.from(state),
              JSON.stringify(node)
            );
            // 更新文档最后更新时间
            await documentService.updateDocument(documentName, {
              content_updated_at: new Date(),
            });
            // 编辑历史记录增加
            await documentEditHistoryService.create({
              edited_user_id: context.user.id,
              document_id: documentName,
              edited_datetime: new Date(),
            });
            
          },
        }),
      ],
    });
  }
  handleConnection(ws: WebSocket, request: any) {
    this.hocuspocusServer.handleConnection(ws, request);
  }
}
