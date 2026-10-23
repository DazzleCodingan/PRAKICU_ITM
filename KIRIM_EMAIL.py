import os
import smtplib
import sys
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from zoneinfo import ZoneInfo


BASE_DIR = Path(__file__).resolve().parent
SENDER_EMAIL = "bayufirdanan@gmail.com"
RECIPIENT_EMAILS = ["bayufirdanan@gmail.com", "titantapson1@gmail.com"]


def main() -> int:
    app_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not app_password:
        raise RuntimeError(
            "GitHub Secret GMAIL_APP_PASSWORD belum diatur."
        )

    image_path = BASE_DIR / "Prakiraan.png"
    csv_path = BASE_DIR / "prakiraan_cuaca.csv"
    for attachment in (image_path, csv_path):
        if not attachment.is_file():
            raise FileNotFoundError(f"Lampiran tidak ditemukan: {attachment}")

    message = EmailMessage()
    jakarta_time = datetime.now(ZoneInfo("Asia/Jakarta"))
    message["Subject"] = f"Prakiraan Cuaca - {jakarta_time:%Y-%m-%d}"
    message["From"] = SENDER_EMAIL
    message["To"] = ", ".join(RECIPIENT_EMAILS)
    message.set_content(
        "Terlampir prakiraan cuaca terbaru.\n"
        "Email ini dikirim otomatis setiap hari pukul 06.00 WIB."
    )

    for attachment, content_type in (
        (image_path, "image/png"),
        (csv_path, "text/csv"),
    ):
        main_type, sub_type = content_type.split("/", 1)
        message.add_attachment(
            attachment.read_bytes(),
            maintype=main_type,
            subtype=sub_type,
            filename=attachment.name,
        )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com", 465, timeout=30
    ) as smtp:
        smtp.login(SENDER_EMAIL, app_password)
        smtp.send_message(message, to_addrs=RECIPIENT_EMAILS)

    print(f"Email prakiraan berhasil dikirim ke {', '.join(RECIPIENT_EMAILS)}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"Gagal mengirim email: {error}", file=sys.stderr)
        raise SystemExit(1)
