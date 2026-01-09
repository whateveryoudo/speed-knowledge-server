// speed-knowledge-server/nodejs-nestjs/src/tiptap-extends/kit.ts
import { Title } from "./title";
import { StarterKit } from "@tiptap/starter-kit";

/**
 * 后端专用的扩展集合
 * 只包含 schema 定义，不包含 view 逻辑
 */

export default [
  StarterKit.configure({
    // 可以根据需要禁用某些扩展
  }),
  Title,
];
