from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from aiosmtplib import send
from email.mime.text import MIMEText

# Define the app
app = FastAPI()

# Define the data model
class EmailPayload(BaseModel):
    recipient: EmailStr
    subject: str
    body: str

# Define the email sending function
async def send_email(recipient: str, subject: str, body: str):
    message = MIMEText(body)
    message["From"] = "@gmail.com"  # Your Gmail address
    message["To"] = recipient
    message["Subject"] = subject

    await send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        username="@gmail.com",  # Your Gmail address
        password="",  # Use an App Password if 2FA is enabled, https://myaccount.google.com/u/1/apppasswords under 2FA auth of Gaccount that you are trying to send email from
        start_tls=True,
    )

# Define the endpoint to receive POST requests
"""
# Expected input from post calls
{
           "recipient": "recipient@example.com",
           "subject": "Test Email",
           "body": "This is a test email sent from FastAPI."
         }
         
         """
@app.post("/send-email/")
async def trigger_email(payload: EmailPayload):
    try:
        await send_email(payload.recipient, payload.subject, payload.body)
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the app with: uvicorn script_name:app --reload
