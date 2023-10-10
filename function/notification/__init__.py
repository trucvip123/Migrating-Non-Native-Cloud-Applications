import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s', notification_id)

    # TODO: Get connection to database
    try:
        # TODO: Establish a connection to the PostgreSQL database
        connection = psycopg2.connect(
            dbname=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            host=os.environ['DB_HOST']
        )

        cursor = connection.cursor()

        # TODO: Get notification message and subject from the database using the notification_id
        cursor.execute("SELECT message, subject FROM notifications WHERE id = %s", (notification_id,))
        notification_data = cursor.fetchone()
        message = notification_data[0]
        subject = notification_data[1]

        # TODO: Get attendees' email and name
        cursor.execute("SELECT email, name FROM attendees WHERE notification_id = %s", (notification_id,))
        attendees_data = cursor.fetchall()

        for attendee in attendees_data:
            attendee_email = attendee[0]
            attendee_name = attendee[1]

            # TODO: Create a personalized email with the subject and message
            personalized_subject = f"Hello, {attendee_name} - {subject}"
            mail = Mail(
                from_email='your@email.com',
                to_emails=attendee_email,
                subject=personalized_subject,
                plain_text_content=message
            )

            # TODO: Send the email using SendGrid
            sendgrid_api_key = os.environ['SENDGRID_API_KEY']
            sendgrid_client = SendGridAPIClient(sendgrid_api_key)
            sendgrid_client.send(mail)

        # TODO: Update the notification table by setting the completed date
        completed_date = datetime.utcnow()
        cursor.execute("UPDATE notifications SET completed_date = %s WHERE id = %s", (completed_date, notification_id))

        # TODO: Commit the changes to the database
        connection.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close the cursor and database connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()
