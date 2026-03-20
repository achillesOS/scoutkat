from app.jobs.tasks import compute_scores_job, fetch_market_snapshots_job, run_signal_recorder_job


def main() -> None:
    fetch_market_snapshots_job()
    compute_scores_job()
    run_signal_recorder_job()


if __name__ == "__main__":
    main()
