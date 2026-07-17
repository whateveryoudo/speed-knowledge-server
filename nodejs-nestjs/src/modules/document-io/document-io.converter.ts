import MarkdownIt from "markdown-it";
import mammoth from "mammoth";
import { BadRequestException, Injectable } from "@nestjs/common";
import { generateHTML, generateJSON } from "@tiptap/html/server";
import { knowledgeKit } from "@speed-tiptap-editor/schema";
import sizeOf from "image-size";
import htmlToDocx from "html-to-docx";
import TurndownService from "turndown";
import { gfm, tables } from "turndown-plugin-gfm";
import { AttachmentService } from "../attachment/attachment.service";
export type ImportFormat = "word" | "markdown" | "speed";
export type ExportFormat = "word" | "markdown" | "speed";
@Injectable()
export class DocumentIOConverter {
  constructor(private readonly attachmentService: AttachmentService) {}

  private readonly IMG_WITH_PREVIEW_RE =
    /<img\b([^>]*?)\bsrc=(["'])([^"']*\/attachment\/(?:public\/)?preview\/([0-9a-f-]{36})[^"']*)\2([^>]*)>/gi;

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
  private getTitle(docJson: any) {
    const titleNode = this.UnwrapDocJson(docJson).content?.find(
      (node: any) => node.type === "title",
    );
    return titleNode?.content?.[0]?.text;
  }
  private parseSpeedDocument(content: string) {
    const text = content.replace(/^\uFEFF/, "");
    // 解析.speed文件内容
    const titleMatch = text.match(/<title>(.*?)<\/title>/i);
    const title = titleMatch ? titleMatch[1] : "未命名文档";
    const html = text
      .replace(/<!doctype\s+speed>\s*/i, "")
      .replace(/<title[^>]*>[\s\S]*?<\/title>\s*/gi, "")
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
  private UnwrapDocJson(docJson: any) {
    return docJson?.default ?? docJson;
  }
  private docJsonToHtml(docJson: any) {
    // 这里对json进行解除下（外面有层default）
    const unwrappedJson = this.UnwrapDocJson(docJson);
    return generateHTML(unwrappedJson, knowledgeKit as any);
  }
  private enhanceHtmlFormWord(html: string) {
    // 增加一些元素行内样式
    let out = html;
    // 表格撑满 + 边框
    out = out.replace(/<table\b([^>]*)>/gi, (_m, attrs) => {
      const cleaned = String(attrs).replace(/\sstyle="[^"]*"/i, "");
      return `<table${cleaned} style="width:100%; border-collapse:collapse;">`;
    });
    // 代码块框
    // out = out.replace(/<pre\b([^>]*)>/gi, (_m, attrs) => {
    //   const styleMatch = String(attrs).match(/\sstyle="([^"]*)"/i);
    //   const exist = styleMatch?.[1] ? `${styleMatch[1]}; ` : "";
    //   const cleaned = String(attrs).replace(/\sstyle="[^"]*"/i, "");
    //   return `<pre${cleaned} style="${exist}background:#f5f5f5; border:1px solid #e0e0e0; padding:12px; font-family:Consolas,monospace; white-space:pre-wrap;">`;
    // });
    return out;
  }
  private prepareHtmlForMarkdown(html: string) {
    return html
      .replace(/<colgroup[\s\S]*?<\/colgroup>/gi, "")
      .replace(
        /<(td|th)([^>]*)>\s*<p[^>]*>([\s\S]*?)<\/p>\s*<\/\1>/gi,
        "<$1$2>$3</$1>",
      );
  }
  /**
   * 重写部分预览路径为公网路径
   * @param html
   * @returns
   */
  private rewritePreviewToPublicUrl(html: string) {
    return html.replace(
      /(\/attachment\/)preview\/([0-9a-f-]{36})/gi,
      "$1public/preview/$2",
    );
  }
  /**
   * 将行内图片转换为 base64，用于word导出
   * @param html
   * @returns 转换后的html
   */
  inlineImageAsBase64 = async (html: string) => {
    const matches = [...html.matchAll(this.IMG_WITH_PREVIEW_RE)];
    if (!matches.length) {
      return html;
    }
    const ids = [...new Set(matches.map((match) => match[4]))];
    const cache = new Map<string, string>();
    await Promise.all(
      ids.map(async (id) => {
        const file = await this.attachmentService.getBufferById(id);
        cache.set(
          id,
          `data:${file.contentType};base64,${file.buffer.toString("base64")}`,
        );
      }),
    );

    return html.replace(
      this.IMG_WITH_PREVIEW_RE,
      (match, before, quote, _src, id, after) => {
        if (!cache.has(id)) {
          return match;
        }
        return `<img ${before} src=${quote}${cache.get(id)}${quote}${after}>`;
      },
    );
  };
  async exportFormDocJson(params: {
    docJson: any;
    format: ExportFormat;
    fileName?: string;
  }) {
    const { docJson, format, fileName } = params;
    // 解析成html格式
    const html = this.docJsonToHtml(docJson);
    console.log("html", html);
    const title = this.getTitle(docJson) || fileName;
    if (format === "word") {
      let transformedHtml =  this.enhanceHtmlFormWord(html);
      // 内部路径图片->base64
      transformedHtml = await this.inlineImageAsBase64(transformedHtml);
      const docx = await htmlToDocx(transformedHtml, null, {
        title,
      });
      return {
        buffer: Buffer.isBuffer(docx) ? docx : Buffer.from(docx as ArrayBuffer),
        fileName: `${title}.docx`,
        contentType:
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      };
    } else if (format === "markdown") {
      const td = new TurndownService({
        headingStyle: "atx",
        codeBlockStyle: "fenced",
        bulletListMarker: "-",
        emDelimiter: "*",
        strongDelimiter: "**",
      });
      td.use(gfm);
      td.addRule("strikethrough", {
        filter: ["del", "s"],
        replacement: (content: string) => `~~${content}~~`,
      });
      // 去掉表格的colgroup标签(不然无法变成管道)
      const transformedHtml = this.prepareHtmlForMarkdown(
        this.rewritePreviewToPublicUrl(html),
      );
      const mdText = td.turndown(transformedHtml);
      return {
        buffer: Buffer.from(mdText, "utf-8"),
        fileName: `${title}.md`,
        contentType: "text/markdown;charset=utf-8",
      };
    } else if (format === "speed") {
      const text = this.buildSpeedDocument(title, html);
      return {
        buffer: Buffer.from(text, "utf-8"),
        fileName: `${title}.speed`,
        contentType: "text/plain;charset=utf-8",
      };
    } else {
      throw new BadRequestException(`Unsupported format: ${format}`);
    }
  }
}
