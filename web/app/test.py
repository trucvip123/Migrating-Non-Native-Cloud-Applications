from azure.servicebus import ServiceBusMessage, ServiceBusClient


SERVICE_BUS_CONNECTION_STRING = "Endpoint=sb://trucnvservicebus.servicebus.windows.net/;SharedAccessKeyName=trucnvpolicy;SharedAccessKey=pVgOpG+He5/dMpoo2DEvA5tmXcaXOj1nW+ASbNgVtI0=;EntityPath=notificationqueue"
SERVICE_BUS_QUEUE_NAME = "notificationqueue"


def send_single_message(sender, notification_id):
    # Create a Service Bus message and send it to the queue
    message = ServiceBusMessage(str(notification_id))
    sender.send_messages(message)
    print("Sent a single message")


def send(notification_id):
    # create a Service Bus client using the connection string
    servicebus_client =  ServiceBusClient.from_connection_string(
        conn_str=SERVICE_BUS_CONNECTION_STRING, logging_enable=True)
    with servicebus_client:
        # Get a Queue Sender object to send messages to the queue
        sender = servicebus_client.get_queue_sender(queue_name=SERVICE_BUS_QUEUE_NAME)
        with sender:
            # Send one message
            send_single_message(sender, notification_id)


# asyncio.run(send(10))
send(10)
print("Done sending messages")
print("-----------------------")
