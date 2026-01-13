from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.attachment import Attachment
from typing import Dict, Any, Tuple
import os
from datetime import datetime
from jose import jwt


class OnlyofficeService:
    """onlyoffice服务"""

    def __init__(self, db: Session):
        self.db = db
        self.onlyoffice_secret_key = settings.ONLYOFFICE_JWT_SECRET
        # MIME 类型到文档类型的映射（优先使用）
        self.mime_to_document_type = {
            # Word 文档类型
            "application/msword": "word",  # .doc
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "word",  # .docx
            "application/vnd.openxmlformats-officedocument.wordprocessingml.template": "word",  # .dotx
            "application/vnd.ms-word.document.macroEnabled.12": "word",  # .docm
            "application/vnd.ms-word.template.macroEnabled.12": "word",  # .dotm
            "application/vnd.openxmlformats-officedocument.wordprocessingml.template": "word",  # .dot
            "application/vnd.oasis.opendocument.text": "word",  # .odt
            "application/vnd.oasis.opendocument.text-template": "word",  # .ott
            "application/rtf": "word",  # .rtf
            "text/plain": "word",  # .txt
            "text/html": "word",  # .html, .htm
            "application/xhtml+xml": "word",  # .html
            "application/epub+zip": "word",  # .epub
            "application/x-fictionbook+xml": "word",  # .fb2
            "application/vnd.oasis.opendocument.text-flat-xml": "word",  # .fodt
            "application/vnd.ms-htmlhelp": "word",  # .mht
            "message/rfc822": "word",  # .mhtml
            "application/vnd.apple.pages": "word",  # .pages
            "application/vnd.sun.xml.writer": "word",  # .sxw
            "application/vnd.sun.xml.writer.template": "word",  # .stw
            "application/vnd.kingsoft.wps": "word",  # .wps
            "application/vnd.kingsoft.wpt": "word",  # .wpt
            "application/xml": "word",  # .xml
            "text/xml": "word",  # .xml
            # Excel 表格类型
            "application/vnd.ms-excel": "cell",  # .xls
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "cell",  # .xlsx
            "application/vnd.openxmlformats-officedocument.spreadsheetml.template": "cell",  # .xltx
            "application/vnd.ms-excel.sheet.macroEnabled.12": "cell",  # .xlsm
            "application/vnd.ms-excel.template.macroEnabled.12": "cell",  # .xltm
            "application/vnd.ms-excel.sheet.binary.macroEnabled.12": "cell",  # .xlsb
            "application/vnd.oasis.opendocument.spreadsheet": "cell",  # .ods
            "application/vnd.oasis.opendocument.spreadsheet-template": "cell",  # .ots
            "application/vnd.oasis.opendocument.spreadsheet-flat-xml": "cell",  # .fods
            "text/csv": "cell",  # .csv
            "application/vnd.apple.numbers": "cell",  # .numbers
            "application/vnd.kingsoft.et": "cell",  # .et
            "application/vnd.kingsoft.ett": "cell",  # .ett
            "application/vnd.sun.xml.calc": "cell",  # .sxc
            # PowerPoint 演示文稿类型
            "application/vnd.ms-powerpoint": "slide",  # .ppt
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": "slide",  # .pptx
            "application/vnd.openxmlformats-officedocument.presentationml.template": "slide",  # .potx
            "application/vnd.openxmlformats-officedocument.presentationml.slideshow": "slide",  # .ppsx
            "application/vnd.ms-powerpoint.presentation.macroEnabled.12": "slide",  # .pptm
            "application/vnd.ms-powerpoint.template.macroEnabled.12": "slide",  # .potm
            "application/vnd.ms-powerpoint.slideshow.macroEnabled.12": "slide",  # .ppsm
            "application/vnd.oasis.opendocument.presentation": "slide",  # .odp
            "application/vnd.oasis.opendocument.presentation-template": "slide",  # .otp
            "application/vnd.oasis.opendocument.presentation-flat-xml": "slide",  # .fodp
            "application/vnd.apple.keynote": "slide",  # .key
            "application/vnd.kingsoft.dps": "slide",  # .dps
            "application/vnd.kingsoft.dpt": "slide",  # .dpt
            "application/vnd.sun.xml.impress": "slide",  # .sxi
            # PDF 类型（独立类型）
            "application/pdf": "pdf",  # .pdf
            "image/vnd.djvu": "pdf",  # .djvu
            "image/x-djvu": "pdf",  # .djvu
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml": "pdf",  # .docxf (近似)
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main": "pdf",  # .docxf
            "application/vnd.openxmlformats-officedocument.wordprocessingml.form": "pdf",  # .oform
            "application/oxps": "pdf",  # .oxps
            "application/vnd.ms-xpsdocument": "pdf",  # .xps
            # Diagram 图表类型
            "application/vnd.ms-visio.drawing.macroEnabled.main+xml": "diagram",  # .vsdm
            "application/vnd.ms-visio.drawing.main+xml": "diagram",  # .vsdx
            "application/vnd.ms-visio.stencil.macroEnabled.main+xml": "diagram",  # .vssm
            "application/vnd.ms-visio.stencil.main+xml": "diagram",  # .vssx
            "application/vnd.ms-visio.template.macroEnabled.main+xml": "diagram",  # .vstm
            "application/vnd.ms-visio.template.main+xml": "diagram",  # .vstx
            # 图片类型（模板中处理）
            "image/jpeg": "image",
            "image/png": "image",
            "image/gif": "image",
            "image/bmp": "image",
            "image/webp": "image",
            # 视频类型（模板中处理）
            "video/mp4": "video",
            "video/avi": "video",
            "video/quicktime": "video",
            "video/x-ms-wmv": "video",
            "video/x-flv": "video",
            "video/x-matroska": "video",
        }

        # MIME 类型到文件扩展名的映射
        self.mime_to_extension = {
            "application/msword": "doc",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.template": "dotx",
            "application/vnd.ms-word.document.macroEnabled.12": "docm",
            "application/vnd.ms-word.template.macroEnabled.12": "dotm",
            "application/vnd.oasis.opendocument.text": "odt",
            "application/vnd.oasis.opendocument.text-template": "ott",
            "application/rtf": "rtf",
            "text/plain": "txt",
            "text/html": "html",
            "application/xhtml+xml": "html",
            "application/epub+zip": "epub",
            "application/x-fictionbook+xml": "fb2",
            "application/vnd.oasis.opendocument.text-flat-xml": "fodt",
            "application/vnd.ms-htmlhelp": "mht",
            "message/rfc822": "mhtml",
            "application/vnd.apple.pages": "pages",
            "application/vnd.sun.xml.writer": "sxw",
            "application/vnd.sun.xml.writer.template": "stw",
            "application/vnd.kingsoft.wps": "wps",
            "application/vnd.kingsoft.wpt": "wpt",
            "application/xml": "xml",
            "text/xml": "xml",
            "application/vnd.ms-excel": "xls",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.template": "xltx",
            "application/vnd.ms-excel.sheet.macroEnabled.12": "xlsm",
            "application/vnd.ms-excel.template.macroEnabled.12": "xltm",
            "application/vnd.ms-excel.sheet.binary.macroEnabled.12": "xlsb",
            "application/vnd.oasis.opendocument.spreadsheet": "ods",
            "application/vnd.oasis.opendocument.spreadsheet-template": "ots",
            "application/vnd.oasis.opendocument.spreadsheet-flat-xml": "fods",
            "text/csv": "csv",
            "application/vnd.apple.numbers": "numbers",
            "application/vnd.kingsoft.et": "et",
            "application/vnd.kingsoft.ett": "ett",
            "application/vnd.sun.xml.calc": "sxc",
            "application/vnd.ms-powerpoint": "ppt",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
            "application/vnd.openxmlformats-officedocument.presentationml.template": "potx",
            "application/vnd.openxmlformats-officedocument.presentationml.slideshow": "ppsx",
            "application/vnd.ms-powerpoint.presentation.macroEnabled.12": "pptm",
            "application/vnd.ms-powerpoint.template.macroEnabled.12": "potm",
            "application/vnd.ms-powerpoint.slideshow.macroEnabled.12": "ppsm",
            "application/vnd.oasis.opendocument.presentation": "odp",
            "application/vnd.oasis.opendocument.presentation-template": "otp",
            "application/vnd.oasis.opendocument.presentation-flat-xml": "fodp",
            "application/vnd.apple.keynote": "key",
            "application/vnd.kingsoft.dps": "dps",
            "application/vnd.kingsoft.dpt": "dpt",
            "application/vnd.sun.xml.impress": "sxi",
            "application/pdf": "pdf",
            "image/vnd.djvu": "djvu",
            "image/x-djvu": "djvu",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main": "docxf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.form": "oform",
            "application/oxps": "oxps",
            "application/vnd.ms-xpsdocument": "xps",
            "application/vnd.ms-visio.drawing.macroEnabled.main+xml": "vsdm",
            "application/vnd.ms-visio.drawing.main+xml": "vsdx",
            "application/vnd.ms-visio.stencil.macroEnabled.main+xml": "vssm",
            "application/vnd.ms-visio.stencil.main+xml": "vssx",
            "application/vnd.ms-visio.template.macroEnabled.main+xml": "vstm",
            "application/vnd.ms-visio.template.main+xml": "vstx",
            # 以下是自己定义的一些扩展名（onlyoffice不支持,为了确保方法统一）
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/gif": "gif",
            "image/bmp": "bmp",
            "image/webp": "webp",
            "video/mp4": "mp4",
            "video/avi": "avi",
            "video/quicktime": "quicktime",
            "video/x-ms-wmv": "wmv",
            "video/x-flv": "flv",
            "video/x-matroska": "mkv",
        }
        # 文件扩展名到文档类型的映射（作为回退方案）
        self.extension_to_document_type = {
            # Word 类型
            "doc": "word",
            "docm": "word",
            "docx": "word",
            "dot": "word",
            "dotm": "word",
            "dotx": "word",
            "epub": "word",
            "fb2": "word",
            "fodt": "word",
            "htm": "word",
            "html": "word",
            "mht": "word",
            "mhtml": "word",
            "odt": "word",
            "ott": "word",
            "pages": "word",
            "rtf": "word",
            "stw": "word",
            "sxw": "word",
            "txt": "word",
            "wps": "word",
            "wpt": "word",
            "xml": "word",
            # Cell 类型
            "csv": "cell",
            "et": "cell",
            "ett": "cell",
            "fods": "cell",
            "numbers": "cell",
            "ods": "cell",
            "ots": "cell",
            "sxc": "cell",
            "xls": "cell",
            "xlsb": "cell",
            "xlsm": "cell",
            "xlsx": "cell",
            "xlt": "cell",
            "xltm": "cell",
            "xltx": "cell",
            # Slide 类型
            "dps": "slide",
            "dpt": "slide",
            "fodp": "slide",
            "key": "slide",
            "odp": "slide",
            "otp": "slide",
            "pot": "slide",
            "potm": "slide",
            "potx": "slide",
            "pps": "slide",
            "ppsm": "slide",
            "ppsx": "slide",
            "ppt": "slide",
            "pptm": "slide",
            "pptx": "slide",
            "sxi": "slide",
            # PDF 类型
            "djvu": "pdf",
            "docxf": "pdf",
            "oform": "pdf",
            "oxps": "pdf",
            "pdf": "pdf",
            "xps": "pdf",
            # Diagram 类型
            "vsdm": "diagram",
            "vsdx": "diagram",
            "vssm": "diagram",
            "vssx": "diagram",
            "vstm": "diagram",
            "vstx": "diagram",
        }

    def _get_file_info_from_mime(self, mime_type: str) -> Tuple[str, str]:
        """从 MIME 类型获取文件信息"""
        if not mime_type:
            return None
        document_type = self.mime_to_document_type.get(mime_type)
        file_extension = self.mime_to_extension.get(mime_type)

        if document_type and file_extension:
            return document_type, file_extension
        return None

    def _get_file_info_from_extension(self, file_extension: str) -> Tuple[str, str]:
        """从文件扩展名获取文件信息"""
        if not file_extension:
            return None
        document_type = self.extension_to_document_type.get(file_extension)

        if document_type:
            return (document_type, file_extension)

        return None

    def generate_config(
        self, attachment: Attachment, mode: str = "view", access_token: str = ""
    ) -> Dict[str, Any]:
        """生成onlyoffice配置"""
        # 优先从 MIME 类型判断
        mime_type = attachment.file_type
        document_type = None
        file_extension = None
        print(f"mime_type: {mime_type}")
        if mime_type:
            result = self._get_file_info_from_mime(mime_type)
            if result:
                document_type, file_extension = result

        # 如果无法从 MIME 类型判断，则从文件扩展名判断
        if not document_type or not file_extension:
            file_ext = (
                os.path.splitext(attachment.file_name)[1].replace(".", "").lower()
            )
            result = self._get_file_info_from_extension(file_ext)
            if result:
                document_type, file_extension = result
            else:
                # 无法识别则统一设置为word
                document_type = "word"
                file_extension = file_ext or "docx"
        print(f"document_type: {document_type}")
        is_image = document_type and document_type == "image"
        is_video = document_type and document_type == "video"
        document_key = f"{attachment.id}-{datetime.now().timestamp()}"
        # 构造文件访问URL
        baseUrl = (
            f"http://localhost:{settings.PORT}"
            if is_image or is_video
            else f"http://host.docker.internal:{settings.PORT}"
        )
        document_url = f"{baseUrl}{settings.API_V1_STR}/attachment/preview/{attachment.id}?access_token={access_token}"
        download_url = f"{baseUrl}{settings.API_V1_STR}/attachment/download/{attachment.id}?access_token={access_token}"
        if is_image or is_video:
            """如果是图片或视频，简化配置"""
            config = {
                "document": {
                    "url": document_url,
                },
                "fileTypeInfo": {
                    "isImage": is_image,
                    "isVideo": is_video,
                },
            }
        else:
            config = {
                "document": {
                    "fileType": file_extension,
                    "key": document_key,
                    "title": attachment.file_name,
                    "url": document_url,
                    "permissions": {
                        "edit": mode == "edit" and not is_image and not is_video,
                        "download": True,
                        "print": not is_video,
                    },
                },
                "documentType": document_type,
                "editorConfig": {
                    "edit": mode == "edit" and not is_image and not is_video,
                    "print": not is_video,
                    "lang": "zh-CN",
                    "customization": {
                        "autosace": mode == "edit" and not is_image and not is_video,
                        "forcesave": False,
                    },
                    "user": {"id": "preview_user", "name": "预览用户"},
                },
                "downloadUrl": download_url,
                # 额外的一些属性，用于在模板中判断文件
                "fileTypeInfo": {
                    "isImage": is_image,
                    "isVideo": is_video,
                },
            }
            if self.onlyoffice_secret_key:
                config["token"] = jwt.encode(
                    config, self.onlyoffice_secret_key, algorithm="HS256"
                )
            else:
                config["token"] = None

        print(f"config: {config}")
        return config
