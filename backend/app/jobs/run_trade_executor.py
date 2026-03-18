from app.jobs.tasks import run_trade_executor_job


def main() -> None:
    run_trade_executor_job()


if __name__ == "__main__":
    main()
