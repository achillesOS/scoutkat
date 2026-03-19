from apscheduler.schedulers.background import BackgroundScheduler

from app.jobs.tasks import (
    compute_scores_job,
    detect_signals_job,
    fetch_grok_shortlist_job,
    fetch_market_snapshots_job,
    fetch_positioning_snapshots_job,
    run_trade_executor_job,
    send_hourly_digest_job,
)


class SchedulerManager:
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler(timezone="UTC")
        self._configured = False

    def start(self) -> None:
        if not self._configured:
            self.scheduler.add_job(fetch_market_snapshots_job, "interval", minutes=10)
            self.scheduler.add_job(fetch_positioning_snapshots_job, "interval", minutes=10)
            self.scheduler.add_job(fetch_grok_shortlist_job, "interval", minutes=10)
            self.scheduler.add_job(compute_scores_job, "interval", minutes=10)
            self.scheduler.add_job(detect_signals_job, "interval", minutes=10)
            self.scheduler.add_job(send_hourly_digest_job, "interval", minutes=10)
            self.scheduler.add_job(run_trade_executor_job, "interval", minutes=10)
            self._configured = True
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)


scheduler_manager = SchedulerManager()
