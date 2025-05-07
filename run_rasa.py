import os
from dotenv import load_dotenv
import subprocess

load_dotenv()  # Load .env vào biến môi trường

# Kiểm tra license có được nạp chưa
assert os.getenv("RASA_PRO_LICENSE") is not None, "Missing RASA_PRO_LICENSE"

# Chạy lệnh Rasa, ví dụ:
subprocess.run(["rasa", "--version"])
