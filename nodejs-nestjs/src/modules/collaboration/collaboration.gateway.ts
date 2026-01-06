import { Injectable, Logger, OnModuleInit } from "@nestjs/common";
import { WebSocketServer, type WebSocket  } from "ws";
import { CollaborationService } from "./collaboration.service";

@Injectable()
export class CollaborationGateway implements OnModuleInit {
    private wss: WebSocketServer;
    private logger:Logger = new Logger(CollaborationGateway.name);
    constructor(private collaborationService: CollaborationService) {}
    onModuleInit() { 
        this.logger.log('CollaborationGateway initialized');
    }

    initialize(server: any) {
        this.wss = new WebSocketServer({ server, path: '/collaboration' });
        this.wss.on('connection', (ws: WebSocket, request: any) => {
            // 获取一些参数
            const url = new URL(request.url, `http://${request.headers.host}`);
            const documentId = url.searchParams.get('documentId');
            const userId = url.searchParams.get('userId');
            const userName = url.searchParams.get('userName');
            // const user = {
            //     id: userId,
            //     name: userName,
            // }
            // const  context = {
            //     documentName: documentId,
            //     user,
            //     requestParameters: {
            //         documentName: documentId  // 传递给 Hocuspocus
            //     }
            // }
            this.collaborationService.handleConnection(ws,request);
             // 处理连接关闭
             ws.on('close', () => {
                this.logger.log(
                    `WebSocket 连接关闭: ${userName} - 文档: ${documentId}`
                );
            });

            // 处理错误
            ws.on('error', (error) => {
                this.logger.error(
                    `WebSocket 错误: ${error.message}`,
                    error.stack
                );
            });
        });
    }
}