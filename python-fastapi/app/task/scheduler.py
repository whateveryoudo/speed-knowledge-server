"""定时任务调度器"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.task.knowledge_stats_job import rebuild_daily_knowledge_stats


def start_scheduler():
    """启动定时任务"""
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(
        rebuild_daily_knowledge_stats,
        trigger=CronTrigger(hour=10, minute=0), 
        id="knowledge_stats_job",
        name="每日知识库统计",
        replace_existing=True,
    )
    scheduler.start()
    print("定时任务已启动")
    return scheduler
