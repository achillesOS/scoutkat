from app.core.config import get_settings
from app.jobs.tasks import send_hourly_digest_job


def main() -> None:
    settings = get_settings()
    print(
        "run_hourly_digest: starting hourly digest for "
        f"{','.join(settings.hourly_digest_symbol_list)}"
    )
    send_hourly_digest_job()


if __name__ == "__main__":
    main()
