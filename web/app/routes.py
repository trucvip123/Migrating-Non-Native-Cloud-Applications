from app import app, db
from datetime import datetime
from app.models import Attendee, Notification
from flask import (
    render_template,
    session,
    request,
    redirect,
    session,
)
import logging
from azure.servicebus import ServiceBusMessage, ServiceBusClient
import traceback


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/Registration", methods=["POST", "GET"])
def registration():
    try:
        if request.method == "POST":
            attendee = Attendee()
            attendee.first_name = request.form["first_name"]
            attendee.last_name = request.form["last_name"]
            attendee.email = request.form["email"]
            attendee.job_position = request.form["job_position"]
            attendee.company = request.form["company"]
            attendee.city = request.form["city"]
            attendee.state = request.form["state"]
            attendee.interests = request.form["interest"]
            attendee.comments = request.form["message"]
            attendee.conference_id = app.config.get("CONFERENCE_ID")

            try:
                db.session.add(attendee)
                db.session.commit()
                session["message"] = "Thank you, {} {}, for registering!".format(
                    attendee.first_name, attendee.last_name
                )
                return redirect("/Registration")
            except:
                logging.error("Error occured while saving your information")

        else:
            if "message" in session:
                message = session["message"]
                session.pop("message", None)
                return render_template("registration.html", message=message)
            else:
                return render_template("registration.html")
    except Exception as e:
        logging.error(e)


@app.route("/Attendees")
def attendees():
    attendees = Attendee.query.order_by(Attendee.submitted_date).all()
    return render_template("attendees.html", attendees=attendees)


@app.route("/Notifications")
def notifications():
    notifications = Notification.query.order_by(Notification.id).all()
    return render_template("notifications.html", notifications=notifications)


@app.route("/Notification", methods=["POST", "GET"])
def notification():
    if request.method == "POST":
        notification = Notification()
        notification.message = request.form["message"]
        notification.subject = request.form["subject"]
        notification.status = "Notifications submitted"
        notification.submitted_date = datetime.utcnow()
        try:
            db.session.add(notification)
            db.session.commit()

            notification_id = notification.id
            logging.info(f"** notification_id = {notification_id}")
            send_queue(notification_id)

            return redirect("/Notifications")
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            logging.error("log unable to save notification")
            return "An error occurred. Please try again later.", 500

    else:
        return render_template("notification.html")


def send_single_message(sender, notification_id):
    message = ServiceBusMessage(str(notification_id))
    sender.send_messages(message)
    logging.debug("Sent a single message")


def send_queue(notification_id):
    logging.debug("Start send into queue...")
    try:
        servicebus_client = ServiceBusClient.from_connection_string(
            conn_str=app.config.get("SERVICE_BUS_CONNECTION_STRING"),
            logging_enable=True,
        )
        with servicebus_client:
            sender = servicebus_client.get_queue_sender(
                queue_name=app.config.get("SERVICE_BUS_QUEUE_NAME")
            )
            with sender:
                send_single_message(sender, notification_id)
    except Exception as e:
        logging.error(e)
