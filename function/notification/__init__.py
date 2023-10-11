import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
sender_email = os.environ["ADMIN_EMAIL_ADDRESS"]
sender_password = os.environ["ADMIN_EMAIL_PW"]

def send_email(recipient_email, subject, message):
    # Create a MIMEMultipart message
    email = MIMEMultipart()
    email["From"] = sender_email
    email["To"] = recipient_email
    email["Subject"] = subject

    # Create a MIMEText object for the email content
    email_text = MIMEText(message, "plain")
    # Attach the email content to the message
    email.attach(email_text)

    # Create an SMTP server connection
    try:
        smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
        smtp_server.starttls()  # Upgrade the connection to use TLS
        smtp_server.login(sender_email, sender_password)  # Log in to your Gmail account

        # Send the email
        smtp_server.sendmail(sender_email, recipient_email, email.as_string())
        print("Email sent successfully!")

    except Exception as e:
        print("Error sending email:", str(e))

    finally:
        smtp_server.quit()  # Close the SMTP server connection


def main(msg: func.ServiceBusMessage):
    notification_id = int(msg.get_body().decode("utf-8"))
    logging.info(
        "Python ServiceBus queue trigger processed message: %s", notification_id
    )

    # TODO: Get connection to database
    try:
        # TODO: Establish a connection to the PostgreSQL database
        connection = psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            host=os.environ["DB_HOST"],
        )

        cursor = connection.cursor()

        # TODO: Get notification message and subject from the database using the notification_id
        cursor.execute(
            "SELECT message, subject FROM notification WHERE id = %s",
            (notification_id,),
        )
        notification_data = cursor.fetchone()
        message = notification_data[0]
        subject = notification_data[1]

        # TODO: Get attendees' email and name
        cursor.execute(
            "SELECT email, first_name FROM attendee;",
            (notification_id,),
        )
        attendees_data = cursor.fetchall()
        count = 0

        for attendee in attendees_data:
            attendee_email = attendee[0]
            attendee_name = attendee[1]

            # TODO: Create a personalized email with the subject and message
            personalized_subject = f"Hello, {attendee_name} - {subject}"
            print("data =", attendee_email, personalized_subject, message)
            send_email(attendee_email, personalized_subject, message)
            count += 1
            
        status = f"Notified {str(count)} attendees"
        completed_date = datetime.now()
        print(status, completed_date)
        # TODO: Update the notification table by setting the completed date
        cursor.execute(
            "UPDATE notification SET status = %s WHERE id = %s",
            (status, notification_id),
        )
        cursor.execute(
            "UPDATE notification SET completed_date = %s WHERE id = %s",
            (str(completed_date), notification_id),
        )        
        # TODO: Commit the changes to the database
        connection.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error, exc_info=True)
    finally:
        # TODO: Close the cursor and database connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()
