import { ApiProperty } from '@nestjs/swagger';
import { IsEnum, IsNotEmpty, IsOptional, IsDate, IsString } from 'class-validator';
import { DocumentType, DocumentVisibility } from '@/enums/document';

export class CreateDocumentDto {
  @ApiProperty({ example: '1234567890' })
  @IsString()
  @IsNotEmpty()
  user_id: string;

  @ApiProperty({ example: '1234567890' })
  @IsString()
  @IsNotEmpty()
  knowledge_id: string;

  @ApiProperty({ example: 'Document Name' })
  @IsString()
  @IsNotEmpty()
  name: string;

  @ApiProperty({ example: 'document-slug' }) 
  @IsString()
  @IsOptional()
  slug: string;

  @ApiProperty({ example: 'document-type' })
  @IsEnum(DocumentType)
  @IsNotEmpty()
  type: DocumentType;

  @ApiProperty({
    example: DocumentVisibility.INHERIT,
    enum: DocumentVisibility,
    required: false,
    description: '文档可见范围: inherit(继承知识库), space(空间内部成员可见), private(私有), public(互联网公开)',
  })
  @IsEnum(DocumentVisibility)
  @IsOptional()
  visibility?: DocumentVisibility;

  @ApiProperty({ example: 'content_updated_at' })
  @IsDate()
  @IsOptional()
  content_updated_at: Date;
}
