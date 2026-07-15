from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_credentials.client import Client as CredentialsClient
from alibabacloud_credentials.models import Config as CredentialsConfig
from app.core.config import settings
from alibabacloud_dm20151123.client import Client
from fastapi import HTTPException, status
from alibabacloud_dm20151123 import models as dm_models
from app.common.enums.auth import EmailScene
import logging

logger = logging.getLogger(__name__)


class EmailService:
    # 内置模板列表
    SCENE_TEMPLATE_MAP = {
        EmailScene.REGISTER: settings.ALIYUN_DM_TEMPLATE_ID,
    }

    def __init__(self):
        if settings.ALIYUN_DM_USE_ECS_RAM_ROLE:
            # 生产从实例元数据获取sts
            credentials_client = CredentialsClient()
            config = open_api_models.Config(
                credential=credentials_client,
                region_id=settings.ALIYUN_DM_REGION,
            )
        else:
            if (
                not settings.ALIYUN_DM_ACCESS_KEY_ID
                or not settings.ALIYUN_DM_ACCESS_KEY_SECRET
                or not settings.ALIYUN_DM_REGION
            ):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="邮箱服务未配置",
                )
            credentials_client = CredentialsClient(
                CredentialsConfig(
                    type="access_key",
                    access_key_id=settings.ALIYUN_DM_ACCESS_KEY_ID,
                    access_key_secret=settings.ALIYUN_DM_ACCESS_KEY_SECRET
                )
            )
            config = open_api_models.Config(
                credential=credentials_client,
                region_id=settings.ALIYUN_DM_REGION,
            )
        self.client = Client(config)

    def send_verification_code(self, scene: EmailScene, to_email: str, code: str):
        # 通用邮箱验证码发送
        target_template_id = self.SCENE_TEMPLATE_MAP.get(scene)
        if not target_template_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的邮箱场景"
            )

        if (
            not settings.ALIYUN_DM_USE_ECS_RAM_ROLE
            or not settings.ALIYUN_DM_ACCESS_KEY_ID
            or not settings.ALIYUN_DM_ACCESS_KEY_SECRET
            or not settings.ALIYUN_DM_REGION
        ):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="邮箱服务未配置"
            )
        template = dm_models.SingleSendMailRequestTemplate(
            template_id=target_template_id, template_data={"code": code}
        )
        request = dm_models.SingleSendMailRequest(
            account_name=settings.ALIYUN_DM_ACCOUNT_NAME,
            address_type=1,
            reply_to_address=False,
            to_address=to_email,
            subject=settings.ALIYUN_DM_REGISTER_SUBJECT,
            from_alias=settings.ALIYUN_DM_FROM_ALIAS,
            template=template,
        )
        try:
            self.client.single_send_mail(request)
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="邮件发送失败，请稍后重试",
            )
