import {
  Injectable,
  OnModuleInit,
  Inject,
  UnauthorizedException,
} from "@nestjs/common";
import { Hocuspocus } from "@hocuspocus/server";
import { ConfigService } from "@nestjs/config";
import { type WebSocket } from "ws";
import { Database } from "@hocuspocus/extension-database";
import { TiptapTransformer } from "@hocuspocus/transformer";
import { DocumentContentService } from "../document-content/document-content.service";
import { DocumentEditHistoryService } from "../document-edit-history/document-edit-history.service";
import { AuthService } from "../auth/auth.service";
import { DocumentService } from "../document/document.service";
import { VectorSyncService } from "../vector-sync/vector-sync.service";
import { CACHE_MANAGER } from "@nestjs/cache-manager";
import { Cache } from "cache-manager";
import { firstValueFrom } from "rxjs";
import { debounce } from "lodash";
import * as Y from "yjs";
import { NotificationService } from "../notification/notification.service";
import { randomUUID } from "crypto";
import { HttpService } from "@nestjs/axios";
export type MentionItem = {
  mention_id: string;
  payload: Record<string, any>;
};
@Injectable()
export class CollaborationService implements OnModuleInit {
  private hocuspocusServer: Hocuspocus;
  private readonly VIEW_COUNT_TTL = 3600 * 24;
  private readonly SYNC_VECTOR_KNOWLEDGE_ID =
    process.env.SYNC_VECTOR_KNOWLEDGE_ID;

  private debounceHandleMention = debounce(this.handleMention, 1000);
  constructor(
    private documentContentService: DocumentContentService,
    private documentEditHistoryService: DocumentEditHistoryService,
    private notificationService: NotificationService,
    private authService: AuthService,
    private documentService: DocumentService,
    private vectorSyncService: VectorSyncService,
    private httpService: HttpService,
    @Inject(CACHE_MANAGER) private cacheManager: Cache,
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
  // 处理tiptap的mention节点，提取出所有attr内容（这里没有定死内容）
  private extractMentionIds(outNode: any, result: MentionItem[] = []) {
    // 注意这里从第一层开始取，
    const node = outNode.default || outNode;
    if (node.type === "mention" && node.attrs.id) {
      result.push({ mention_id: node.attrs.id, payload: node.attrs });
    }
    if (node.content && Array.isArray(node.content)) {
      for (const child of node.content) {
        this.extractMentionIds(child, result);
      }
    }
    return result;
  }
  // 处理mention节点，触发mention用户通知
  private async handleMention(
    documentName: string,
    oldContentJson: any,
    nodeJson: any,
    actorUserId: number,
    notificationEventId: string,
  ) {
    const oldMentionRows = this.extractMentionIds(oldContentJson);
    const newMentionRows = this.extractMentionIds(nodeJson);
    console.log(oldMentionRows, newMentionRows);
    const addedMentionRows = [...newMentionRows].filter(
      (row) =>
        !oldMentionRows.some((oldRow) => oldRow.mention_id === row.mention_id),
    );
    // test
    // const addedMentionRows = [
    //   {
    //     mention_id: 'ykxtest-mention-1',
    //     payload: {
    //       name: "ykxtest",
    //       user_id: 2
    //     },
    //   },
    // ];
    console.log(addedMentionRows);
    if (addedMentionRows.length > 0) {
      await this.notificationService.createMentionNotifications({
        documentName,
        actorUserId,
        addedMentionRows,
        notificationEventId,
      });
    }
  }
  private async verifyUserPermission(token: string, documentName: string) {
    // 调用python服务,校验用户是否有编辑权限
    const response = await firstValueFrom(
      this.httpService.get<boolean>(
        `${process.env.PYTHON_SERVER_URL}/api/v1/internal/document/${documentName}/valid`,
        {
          headers: {
            "X-Internal-Token": process.env.INTERNAL_SERVICE_TOKEN,
            Authorization: `Bearer ${token}`,
          },
        },
      ),
    );
    return response.data;
  }
  onModuleInit() {
    const documentContentService = this.documentContentService;
    const documentService = this.documentService;
    const documentEditHistoryService = this.documentEditHistoryService;
    const vectorSyncService = this.vectorSyncService;
    const yStateToPmJson = this.yStateToPmJson;
    const syncVectorKnowledgeId = this.SYNC_VECTOR_KNOWLEDGE_ID;
    const debounceHandleMention = this.debounceHandleMention.bind(this);
    const verifyUserPermission = this.verifyUserPermission.bind(this);
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
        // 这里调用python端接口获取当前用户权限（是否能够编辑当前文档）,TODO:感觉是不是前端调用传入进来好点？
        const canIEdit = await verifyUserPermission(
          token,
          context.documentName,
        );
        if (!canIEdit) {
          throw new UnauthorizedException(
            "Unauthorized: User does not have edit permission",
          );
        }

        // 存入访问次数，增加到document_base表中
        this.syncViewCount(context.documentName, decoded.id);
        return {
          user: decoded,
        };
      },
      extensions: [
        new Database({
          async fetch({ documentName, context }) {
            const content =
              await documentContentService.getContent(documentName);
            if (!content || content.length === 0) {
              return null;
            }
            return new Uint8Array(content);
          },
          async store({ documentName, state, context }) {
            const node = await yStateToPmJson(state);
            // 先那一遍旧的内容，用于对比
            const oldContentJson =
              await documentContentService.getDocumentContentJson(documentName);
            await documentContentService.updateContent(
              documentName,
              Buffer.from(state),
              JSON.stringify(node),
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

            // 增加向量同步任务(注意：这里需要传入知识库id)
            if (syncVectorKnowledgeId === context.knowledgeId) {
              await vectorSyncService.touch(context.knowledgeId, documentName);
            }
            const notificationEventId = randomUUID();
            // 查找提及用户，增加通知
            await debounceHandleMention(
              documentName,
              oldContentJson,
              node,
              context.user.id,
              notificationEventId,
            );
          },
        }),
      ],
    });
  }
  // 增加额外自定义参数
  handleConnection(
    ws: WebSocket,
    request: any,
    context: { knowledgeId: string },
  ) {
    this.hocuspocusServer.handleConnection(ws, request, context);
  }
}
