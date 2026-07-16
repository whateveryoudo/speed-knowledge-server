import {
  BadRequestException,
  Body,
  Controller,
  Post,
  UploadedFile,
  UseGuards,
  UseInterceptors,
} from "@nestjs/common";
import { InternalTokenGuard } from "../common/guards/internal-token.guard";
import { FileInterceptor } from "@nestjs/platform-express";
import type { ImportFormat } from "./document-io.converter";
import { DocumentIOService } from "./document-io.service";

@Controller("document-io")
@UseGuards(InternalTokenGuard)
export class DocumentIOController {
  constructor(private readonly documentIOService: DocumentIOService) {}
  @Post("import")
  @UseInterceptors(FileInterceptor("file"))
  async import(
    @UploadedFile() file: Express.Multer.File,
    @Body()
    body: {
      documentId: string;
      format: ImportFormat;
      titleHint: string;
      userId: number;
    },
  ) {
    if (!file?.buffer) {
      throw new BadRequestException("File is required");
    }
    if (!body.documentId) {
      throw new BadRequestException("documentId is required");
    }
    if (!body.format) {
      throw new BadRequestException("format is required");
    }
    if (!body.titleHint) {
      throw new BadRequestException("titleHint is required");
    }
    if (!body.userId) {
      throw new BadRequestException("userId is required");
    }
    const result = await this.documentIOService.importToDocument({
      documentId: body.documentId,
      buffer: file.buffer,
      format: body.format,
      titleHint: body.titleHint,
      userId: body.userId,
    });
    return {
      success: true,
      errCode: 0,
      data: result,
      errMessage: "ok"
    };
  }
}
