"""添加权限能力(单独脚本)"""

from app.db.session import SessionLocal  # 名字看你项目，通常叫 SessionLocal
from app.services.permission_ability_service import PermissionAbilityService
import argparse
from app.common.enums import KnowledgeAbility


def main():
    groupids = [
        "0f467374-262d-4ddc-9464-c854200f24a8",
        "441ac079-d3f5-4718-99a3-0d65013444a4",
        "5db8b9d3-d530-4ca3-af17-442d6294cef3",
        "9d2a872b-7074-43cc-8e79-9c52270cd50b",
        "c5693146-8ab9-45dc-a197-8530dc69c280",
        "e9ab5e61-bf58-433c-8ec1-853de2424b99",
    ]
    db = SessionLocal()
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--permission_group_id", type=str, required=True)
    # parser.add_argument("--ability_key", type=str, required=True)
    # parser.add_argument("--enable", type=bool, required=True)
    # args = parser.parse_args()
    for groupid in groupids:
        try:
            service = PermissionAbilityService(db)

            service.add_permission_ability_by_permission_group_id(
                permission_group_id=groupid,
                ability_key=KnowledgeAbility.READ_BOOK,
                enable=True,
            )
        finally:
            db.close()


if __name__ == "__main__":
    main()
