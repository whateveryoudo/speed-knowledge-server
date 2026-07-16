import MarkdownIt from "markdown-it";
import mammoth from "mammoth";
import { BadRequestException, Injectable } from "@nestjs/common";
import { generateJSON } from "@tiptap/html/server";
import { knowledgeKit } from "@speed-tiptap-editor/schema";
import sizeOf from "image-size";
import { AttachmentService } from "../attachment/attachment.service";
export type ImportFormat = "word" | "markdown" | "speed";

@Injectable()
export class DocumentIOConverter {
  constructor(private readonly attachmentService: AttachmentService) {}

  private readonly md = new MarkdownIt({
    html: true,
    linkify: true,
    typographer: true,
    breaks: true,
  });
  private ensureTitle(json: any, titleHint: string): any {
    const text = titleHint.trim() || "无标题文档";
    // 加入文件名作为标题
    json.content = [
      { type: "title", content: [{ type: "text", text }] },
      ...(json.content || []),
    ];
    return json;
  }

  private parseSpeedDocument(content: string) {
    const text = content.replace(/^\uFEFF/, "");
    // 解析.speed文件内容
    const titleMatch = content.match(/<title>(.*?)<\/title>/i);
    const title = titleMatch ? titleMatch[1] : "未命名文档";
    const html = text
      .replace(/<!doctype\s+speed>\s*/i, "")
      .replace(/<title[\s\S]*?<\/title>\s*/g, "")
      .replace(/(?:<meta\b[^>]*\/?>\s*)+/gi, "")
      .trim();
    return { title, html };
  }
  private buildSpeedDocument(title: string, html: string) {
    const safeTitle = String(title || "未命名文档")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&apos;");
    return `<!doctype speed>
    <title>${safeTitle}</title>
    ${html}
    `;
  }
  async convert(
    buffer: Buffer,
    format: ImportFormat,
    titleHint: string,
    userId: number,
  ): Promise<any> {
    let html = "";
    if (format === "word") {
      // 使用 mammoth 转换 Word 文档
      const result = await mammoth.convertToHtml(
        { buffer },
        {
          // 样式映射配置
          styleMap: [
            // 标题样式映射
            "p[style-name='Heading 1'] => h1:fresh",
            "p[style-name='Heading 2'] => h2:fresh",
            "p[style-name='Heading 3'] => h3:fresh",
            "p[style-name='Heading 4'] => h4:fresh",
            "p[style-name='Heading 5'] => h5:fresh",
            "p[style-name='Heading 6'] => h6:fresh",

            // 列表样式映射
            "p[style-name='List Paragraph'] => ul > li:fresh",

            // 引用样式映射
            "p[style-name='Quote'] => blockquote:fresh",

            // 代码样式映射
            "p[style-name='Code'] => pre > code:fresh",
            // 动态样式映射 - 通过 transformDocument 更新的样式名称（这些是我自定义的）
            "p[style-name='Centered Text'] => p[style='text-align: center']:fresh",
            "p[style-name='Right Aligned'] => p[style='text-align: right']:fresh",
            "p[style-name='Justified Text'] => p[style='text-align: justify']:fresh",
            // 先不加背景高亮
          ],
          // 使用 transformDocument 动态更新样式名称
          transformDocument: (document: any) => {
            console.log("原始文档结构:", document);

            // 递归处理文档中的所有元素
            const processElement = (element: any) => {
              // 创建元素的副本，避免直接修改原对象
              const processedElement = { ...element };

              if (element.type === "paragraph") {
                // 根据对齐方式动态更新样式名称
                if (element.alignment === "center") {
                  processedElement.styleName = "Centered Text";
                } else if (element.alignment === "right") {
                  processedElement.styleName = "Right Aligned";
                } else if (element.alignment === "justify") {
                  processedElement.styleName = "Justified Text";
                }
              }

              // 递归处理子元素
              if (element.children && Array.isArray(element.children)) {
                processedElement.children =
                  element.children.map(processElement);
              }

              return processedElement;
            };

            const result = processElement(document);
            console.log("处理后的文档结构:", result);
            return result;
          },

          // 转换选项
          convertImage: mammoth.images.imgElement(async (image) => {
            const imageBuffer = await image.read();
            const contentType = image.contentType || "image/png";
            const ext = contentType.split("/")[1] || "png";
            const { width = 0, height = 0 } = sizeOf(imageBuffer);

            try {
              console.log("upload start", imageBuffer.length);
              const attachment = await this.attachmentService.uploadBuffer({
                buffer: imageBuffer,
                fileName: `image-${Date.now()}.${ext}`,
                contentType,
                userId,
              });
              console.log("upload done", attachment.id);

              return {
                src: `${process.env.PYTHON_SERVER_URL}/api/v1/attachment/preview/${attachment.id}`,
                width: String(width),
                height: String(height),
                "data-original-width": String(width),
                "data-original-height": String(height),
              };
            } catch (error) {
              console.error("上传图片失败:", error);
              return {
                src: `data:${contentType};base64,${imageBuffer.toString("base64")}`,
                width,
                height,
              };
            }
          }),

          // 忽略空段落
          ignoreEmptyParagraphs: true,

          // 保留样式
          includeEmbeddedStyleMap: true,
          includeDefaultStyleMap: true,
        },
      );
      html = result.value;
    } else if (format === "markdown") {
      html = this.md.render(buffer.toString("utf-8"));
    } else if (format === "speed") {
      // 平台内部的html(其实是tiptap本身的html)
      html = buffer.toString("utf-8");
      const parsed = this.parseSpeedDocument(html);
      html = parsed.html;
      titleHint = parsed.title; // 这里用解析的title标签覆盖掉titleHint
    } else {
      throw new BadRequestException(`Unsupported format: ${format}`);
    }
    // 调用tiptap内置方法转化为json(这里走自定义的扩展包)
    return this.ensureTitle(generateJSON(html, knowledgeKit as any), titleHint);
  }
}
