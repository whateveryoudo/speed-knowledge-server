import { Injectable, OnModuleInit } from "@nestjs/common";
import * as Minio from "minio";
import { ConfigService } from "@nestjs/config";

@Injectable()
export class MinioService implements OnModuleInit {
  private minioClient: Minio.Client;
  private bucketName: string;
  constructor(private readonly config: ConfigService) {
    this.bucketName = this.config.getOrThrow("MINIO_BUCKET_NAME");
    const endpoint = this.config.getOrThrow("MINIO_ENDPOINT");
    const [host, port] = endpoint.split(":");
    this.minioClient = new Minio.Client({
      endPoint: host,
      port: parseInt(port),
      useSSL: this.config.getOrThrow("MINIO_USE_SSL") === "true",
      accessKey: this.config.getOrThrow("MINIO_ACCESS_KEY"),
      secretKey: this.config.getOrThrow("MINIO_SECRET_KEY"),
    });
  }

  async onModuleInit() {
    const exists = await this.minioClient.bucketExists(this.bucketName);
    if (!exists) {
      await this.minioClient.makeBucket(this.bucketName);
    }
  }
  async putObject(params: {
    objectName: string;
    buffer: Buffer;
    contentType: string;
  }) {
    const { objectName, buffer, contentType } = params;
    await this.minioClient.putObject(
      this.bucketName,
      objectName,
      buffer,
      buffer.length,
      {
        "Content-Type": contentType,
      },
    );
    return {
      bucketName: this.bucketName,
      objectName,
    };
  }

  async getObject(params: {
    objectName: string;
    bucketName: string;
  }): Promise<Buffer> {
    const { objectName, bucketName } = params;
    const stream = await this.minioClient.getObject(bucketName, objectName);
    const chunks: Buffer[] = [];
    for await (const chunk of stream) {
      chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
    }

    return Buffer.concat(chunks);
  }
}
