import smtplib
import csv
import time
import os
import datetime
import random
from email.message import EmailMessage
from email.utils import formataddr
from dotenv import load_dotenv

# ================= CONFIG ================= #
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

EMAILS_CSV = "emails.csv"
SENT_LOG = "sent_log.csv"
RESUME_FILE = "Vruttant_Lihitkar_Data_Analyst_Resume.pdf"

MIN_DELAY = 45
MAX_DELAY = 70
# ========================================== #

SUBJECTS = [
    "Data Analyst Internship Inquiry",
    "Application for Data Analyst Internship",
    "Seeking Data Analyst Internship Opportunity",
    "Data Analytics Internship – Availability",
]

EMAIL_BODIES = [
    """Dear Hiring Team ,

I hope you are doing well.

I am a third-year B.Tech student at IIIT Nagpur, writing to express my interest in a Data Analyst internship at your organization. I have hands-on experience with SQL, Python, Excel, and data visualization tools through projects involving data cleaning, analysis, and dashboard creation.

I am particularly interested in applying my analytical skills to real-world business problems and gaining practical industry experience. I am flexible with my availability and open to short-term, semester-long, or long-term internship opportunities.

Please find my resume attached, and I would appreciate the opportunity to discuss any suitable roles.

Thank you for your time and consideration.

Kind regards,  
Vruttant Pramod Lihitkar  
Email: mail.vruttant@gmail.com  
Portfolio: https://www.vruttant.in  
LinkedIn: https://www.linkedin.com/in/vruttantlihitkar/
""",
    """Hello Hiring Team,

I hope this message finds you well.

I am a third-year B.Tech student at IIIT Nagpur and am interested in Data Analyst internship opportunities at your organization. I have experience working with SQL, Python, Excel, and data visualization tools, focusing on data cleaning, analysis, and dashboard creation.

I am eager to apply my skills to real-world problems and gain industry exposure. I am open to short-term, semester-based, or long-term internship roles.

My resume is attached for your consideration, and I would welcome the opportunity to discuss any relevant openings.

Best regards,  
Vruttant Pramod Lihitkar  
Email: mail.vruttant@gmail.com  
Portfolio: https://www.vruttant.in  
LinkedIn: https://www.linkedin.com/in/vruttantlihitkar/
"""
]

# ---------- TIME WINDOW ---------- #
def within_time_window():
    now = datetime.datetime.now()
    weekday = now.weekday()  # Tue=1 Wed=2 Thu=3 Fri=4

    if weekday not in (0,1, 2, 3 ,4):
        return False

    start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    end = now.replace(hour=12, minute=45, second=0, microsecond=0)

    return start <= now <= end


# ---------- SEND EMAIL ---------- #
def send_email(sender_email, to_email, server):
    msg = EmailMessage()
    msg["From"] = formataddr(("Vruttant Lihitkar", sender_email))
    msg["To"] = to_email
    msg["Subject"] = random.choice(SUBJECTS)
    msg.set_content(random.choice(EMAIL_BODIES))

    with open(RESUME_FILE, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=RESUME_FILE
        )

    server.send_message(msg)


# ---------- MAIN ---------- #
def main():
    # Ensure correct working directory (important for Task Scheduler / cron)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if not within_time_window():
        return

    load_dotenv()
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("APP_PASSWORD")

    if not EMAIL or not PASSWORD:
        return

    # Load sent emails
    sent_set = set()
    if os.path.exists(SENT_LOG):
        with open(SENT_LOG, newline="") as f:
            sent_set = {row[0] for row in csv.reader(f) if row}

    try:
        # 🔥 CONNECT ONCE
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL, PASSWORD)

            with open(EMAILS_CSV, newline="") as emails, \
                 open(SENT_LOG, "a", newline="") as log:

                reader = csv.reader(emails)
                writer = csv.writer(log)

                for row in reader:
                    if not within_time_window():
                        break

                    if not row:
                        continue

                    email = row[0].strip()
                    if not email or email in sent_set:
                        continue

                    try:
                        send_email(EMAIL, email, server)

                        writer.writerow([
                            email,
                            "SENT",
                            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ])
                        log.flush()  # 🔒 critical safety

                        sent_set.add(email)

                        time.sleep(random.randint(MIN_DELAY, MAX_DELAY))

                    except Exception as e:
                        writer.writerow([
                            email,
                            "FAILED",
                            str(e)
                        ])
                        log.flush()

    except Exception:
        # SMTP connection or login failed
        return


if __name__ == "__main__":
    main()


