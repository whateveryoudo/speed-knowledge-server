/*
 * @Author: ykx
 * @Date: 2022-11-11 15:30:15
 * @LastEditTime: 2023-01-06 11:33:21
 * @LastEditors: your name
 * @Description: 用于后端解析标题节点（TODO:提取为公共扩展库，前后端都可以使用）
 * @FilePath: \we-knowledge-base\src\tiptap\core\extensions\title\index.ts
 */
import { mergeAttributes, Node } from "@tiptap/core";
export interface TitleOptions {
  HTMLAttributes: Record<string, any>;
}

export const TitleExtensionName = "title";

export const Title = Node.create<TitleOptions>({
  name: TitleExtensionName,
  content: "inline*",
  defining: true,
  isolating: true,
  marks: "", // 禁用样式修改
  addOptions() {
    return {
      HTMLAttributes: {
        class: "node-title",
      },
    };
  },

  // addAttributes() {
  //   return {
  //     cover: {
  //       default: '',
  //       parseHTML: getDatasetAttribute('cover'),
  //     },
  //   };
  // },

  parseHTML() {
    return [
      {
        tag: "h1[class=node-title]",
      },
    ];
  },

  renderHTML({ HTMLAttributes }: { HTMLAttributes: Record<string, any> }) {
    return [
      "h1",
      mergeAttributes(this.options.HTMLAttributes, HTMLAttributes),
      0, // 直接渲染内联内容，避免在 h1 内包裹 div（防止导出的时候出现无法识别的问题）
    ];
  },
});
