import MarkdownIt from "markdown-it";
import mammoth from "mammoth";
import { BadRequestException, Injectable } from "@nestjs/common";
import { generateJSON } from "@tiptap/html/server";
import { knowledgeKit } from "@speed-tiptap-editor/schema";
export type ImportFormat = "word" | "markdown";

@Injectable()
export class DocumentIOConverter {
  private readonly md = new MarkdownIt({
    html: true,
    linkify: true,
    typographer: true,
    breaks: true,
  });
  private ensureTitle(json: any, titleHint: string): any {
    const text = titleHint.trim() || '无标题文档';
    // 加入文件名作为标题
    json.content = [
        {type: "title", content: [{ type: "text", text }]},
        ...(json.content || []),
    ]
    return json;
  }
  async convert(
    buffer: Buffer,
    format: ImportFormat,
    titleHint: string,
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
          convertImage: mammoth.images.imgElement((image) => {
            // TODO:走文件服务地址
            return image.read("base64").then((imageBuffer) => {
              return {
                src: `data:${image.contentType};base64,${imageBuffer}`,
              };
            });
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
    } else {
      throw new BadRequestException(`Unsupported format: ${format}`);
    }
    // 调用tiptap内置方法转化为json(这里走自定义的扩展包)
    return this.ensureTitle(
      generateJSON(html, knowledgeKit as any),
      titleHint,
    );
  }
}
