import { ApiProperty } from "@nestjs/swagger";
import {
  IsInt,
  IsEnum,
  IsNotEmpty,
  IsString,
  IsObject,
  IsOptional,
} from "class-validator";
import { NotificationBizType } from "@/enums/notification";
// 发送站内信通知的dto
export class SendNotificationDto {
  @ApiProperty({ example: 123 })
  @IsInt()
  @IsNotEmpty()
  mentionedUserId: number;

  @ApiProperty({ example: NotificationBizType.JOIN_COLLABORATOR })
  @IsEnum(NotificationBizType)
  @IsNotEmpty()
  bizType: NotificationBizType;

  @ApiProperty({ example: "1234567890" })
  @IsString()
  @IsNotEmpty()
  bizId: string;

  @ApiProperty({ example: 123 })
  @IsInt()
  @IsNotEmpty()
  actorUserId: number;

  @ApiProperty({ example: { key: "value" } })
  @IsObject()
  @IsOptional()
  payload?: Record<string, any>;
}
