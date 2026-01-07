import { ApiProperty } from '@nestjs/swagger';
import { IsBoolean, IsEnum, IsNotEmpty, IsOptional, IsDate, IsString } from 'class-validator';
import { DocumentType } from '@/enums/document';
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

  
  @ApiProperty({ example: 'is_public' })
  @IsBoolean()
  @IsOptional()
  is_public: boolean;

  @ApiProperty({ example: 'content_updated_at' })
  @IsDate()
  @IsOptional()
  content_updated_at: Date;
}

