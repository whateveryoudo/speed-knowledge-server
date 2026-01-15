import { ApiProperty } from '@nestjs/swagger';
import { IsNumber, IsNotEmpty, IsOptional, IsDate, IsString } from 'class-validator';

export class CreateDocumentEditHistoryDto {
  @ApiProperty({ example: '1234567890', description: '文档ID' })
  @IsString()
  @IsNotEmpty()
  document_id: string;

  @ApiProperty({ example: '1234567890', description: '编辑用户ID' })
  @IsNumber()
  @IsNotEmpty()
  edited_user_id: number;

  @ApiProperty({ example: '2026-01-01 12:00:00', description: '编辑时间' })
  @IsDate()
  @IsOptional()
  edited_datetime: Date;
}

