import os
import smtplib
import sys
import time
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from zoneinfo import ZoneInfo


BASE_DIR = Path(__file__).resolve().parent
SENDER_EMAIL = "bayufirdanan@gmail.com"
RECIPIENT_EMAILS = [
    "bayufirdanan@gmail.com",
    "nurlialayla06@gmail.com",
    "hanagirsang62@gmail.com",
    "michaeljustine135@gmail.com",
    "aidilll0602@gmail.com",
]

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 20

ATTACHMENTS = [
    (BASE_DIR / "Prakiraan.png", "image/png"),
    (BASE_DIR / "prakiraan_cuaca.csv", "text/csv"),
]


def check_attachments() -> None:
    for path, _ in ATTACHMENTS:
        if not path.is_file():
            raise FileNotFoundError(f"Lampiran tidak ditemukan: {path}")
        if path.stat().st_size == 0:
            raise ValueError(f"Lampiran kosong (0 byte): {path}")


def build_message() -> EmailMessage:
    jakarta_time = datetime.now(ZoneInfo("Asia/Jakarta"))

    message = EmailMessage()
    message["Subject"] = f"Prakiraan Cuaca - {jakarta_time:%Y-%m-%d}"
    message["From"] = SENDER_EMAIL
    message["To"] = ", ".join(RECIPIENT_EMAILS)
    message.set_content(
        "Terlampir prakiraan cuaca terbaru.\n"
        f"Dibuat: {jakarta_time:%d-%m-%Y %H:%M} WIB\n"
        "Email ini dikirim otomatis setiap hari sekitar pukul 06.27 WIB."
    )

    for path, content_type in ATTACHMENTS:
        main_type, sub_type = content_type.split("/", 1)
        message.add_attachment(
            path.read_bytes(),
            maintype=main_type,
            subtype=sub_type,
            filename=path.name,
        )

    return message


def send_with_retry(message: EmailMessage, app_password: str) -> dict:
    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
                smtp.login(SENDER_EMAIL, app_password)
                return smtp.send_message(message, to_addrs=RECIPIENT_EMAILS)
        except smtplib.SMTPAuthenticationError:
            # Password salah tidak akan membaik dengan mengulang.
            raise
        except (smtplib.SMTPException, OSError) as error:
            last_error = error
            print(
                f"Percobaan {attempt}/{MAX_ATTEMPTS} gagal: {error}",
                file=sys.stderr,
            )
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECONDS)

    raise RuntimeError(
        f"Pengiriman gagal setelah {MAX_ATTEMPTS} percobaan: {last_error}"
    )


def main() -> int:
    app_password = os.environ.get("GMAIL_APP_PASSWORD", "").strip().replace(" ", "")
    if not app_password:
        raise RuntimeError("GitHub Secret GMAIL_APP_PASSWORD belum diatur.")

    check_attachments()
    message = build_message()
    refused = send_with_retry(message, app_password)

    if refused:
        print(f"Penerima yang ditolak server: {refused}", file=sys.stderr)
        return 1

    print(f"Email prakiraan berhasil dikirim ke {', '.join(RECIPIENT_EMAILS)}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"Gagal mengirim email: {error}", file=sys.stderr)
        raise SystemExit(1)
