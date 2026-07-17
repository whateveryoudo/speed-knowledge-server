declare module "html-to-docx" {
  export default function htmlToDocx(
    html: string,
    headerHTML?: string | null,
    documentOptions?: Record<string, unknown>,
    footerHTML?: string | null,
  ): Promise<Buffer | ArrayBuffer | Uint8Array>;
}
