export enum NotificationListType {
  // 提及或评论
  MENTION_OR_COMMENT = "mention_or_comment",
  // 点赞
  LIKE = "like",
  // 关注
  FOLLOW = "follow",
  // 待处理
  TODO = "todo",
  // 系统
  SYSTEM = "system",
  // 其他
  OTHER = "other",
}

export enum NotificationBizType {
  MENTION = "mention",
  COMMENT = "comment",
  LIKE = "like",
  INVITE = "invite",
  FOLLOW = "follow",
}

// 列表类型到业务类型映射(可用于后续追加类型操作)
export const listType2BizTypeMap = {
  [NotificationListType.MENTION_OR_COMMENT]: [
    NotificationBizType.MENTION,
    NotificationBizType.COMMENT,
  ],
  [NotificationListType.LIKE]: [NotificationBizType.LIKE],
  [NotificationListType.FOLLOW]: [NotificationBizType.FOLLOW],
  [NotificationListType.TODO]: [],
  [NotificationListType.SYSTEM]: [NotificationBizType.INVITE],
};
// 业务类型到列表类型映射(用于实际使用时候取到listType)
export const bizType2ListTypeMap = Object.entries(listType2BizTypeMap).reduce(
  (acc, [listType, bizTypes]) => {
    bizTypes.forEach((bizType) => {
      acc[bizType] = listType as NotificationListType;
    });
    return acc;
  },
  {} as Record<NotificationBizType, NotificationListType>,
);
