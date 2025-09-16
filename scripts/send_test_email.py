import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from services.email_service import email_service
from dotenv import load_dotenv
import os

load_dotenv()

recipient = os.getenv('TEST_EMAIL') or 'vscardoso2005@gmail.com'

print(f"Sending test email to: {recipient}")

ok = email_service.send_templated_email(recipient, 'Seu material: Análise completa + guia de comunicação', 'welcome', {'name': 'Victor', 'materials_link': os.getenv('MATERIALS_LINK')})

print('Send result:', ok)
