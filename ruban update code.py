import os
import smtplib
import ssl
from twilio.rest import Client
from ultralytics import YOLO
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Initialize YOLO model with the trained model
model = YOLO("best (1).pt")

# Load credentials and config from environment variables or use defaults
TWILIO_SID = os.getenv("TWILIO_SID", "ACe2b0d50aeec15d43356b900046918bd7")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "60d2ae60f7d79b5578e209df216a4d9b")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+12183927266")
RECEIVER_PHONE_NUMBER = os.getenv("RECEIVER_PHONE_NUMBER", "+918667570687")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "rubanclement06052003@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "damw vmus vdex rhas")  # Use Google App Password
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "rubanclement@karunya.edu.in")

# Static Location (Change to your deployment location or use get_location() function later)
LOCATION = os.getenv("LOCATION", "Forest Zone A - Lat: 10.961, Lon: 76.991")

# Function to send SMS alert
def send_sms_alert(detected_animals):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        detection_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = (
            f"Alert: Detected animals - {', '.join(detected_animals)} at {detection_time}\n"
            f"Location: {LOCATION}"
        )
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=RECEIVER_PHONE_NUMBER
        )
        print("SMS alert sent!")
    except Exception as e:
        print(f" Failed to send SMS alert: {e}")

# Function to send email alert with an image attachment
def send_email_alert(detected_animals, image_path):
    subject = "🐾 Animal Detection Alert"
    detection_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = (
        f"The following animals were detected at {detection_time}:\n\n"
        f"{', '.join(detected_animals)}\n\n"
        f"Location: {LOCATION}"
    )

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Attach image if it exists
    if os.path.exists(image_path):
        with open(image_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(image_path)}"
            )
            msg.attach(part)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email alert sent!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Perform prediction and send alerts
def detect_and_alert(source):
    # Verify the source exists
    if not os.path.exists(source) and not isinstance(source, int):
        raise FileNotFoundError(f"Source file or camera does not exist: {source}")

    try:
        results = model.predict(source=source, show=False, save=True)
        detected_animals = set()
        image_path = "detected_image.jpg"

        for result in results:
            for cls in result.boxes.cls:
                animal_name = model.names[int(cls)]
                detected_animals.add(animal_name)
            result.save(filename=image_path)

        detected_animals = list(detected_animals)

        if detected_animals:
            print(f" Detected animals: {', '.join(detected_animals)}")
            send_sms_alert(detected_animals)
            send_email_alert(detected_animals, image_path)
        else:
            print("No animals detected.")
    except Exception as e:
        print(f"Error during prediction: {e}")

# Main function
if __name__ == "__main__":
    source_path = 'elephant 2 (1).png'  # Replace with 0 for webcam or a video/image path
    try:
        detect_and_alert(source_path)
    except Exception as e:
        print(f" Fatal error: {e}")
