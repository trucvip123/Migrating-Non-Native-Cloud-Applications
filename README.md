# TechConf Registration Website

## Project Overview
The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:
 - The web application is not scalable to handle user load at peak
 - When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
 - The current architecture is not cost-effective 

In this project, you are tasked to do the following:
- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:
- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App
1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
      - `POSTGRES_URL`
      - `POSTGRES_USER`
      - `POSTGRES_PW`
      - `POSTGRES_DB`
      - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function
1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

      **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.
      - The Azure Function should do the following:
         - Process the message which is the `notification_id`
         - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
         - Query the database to retrieve a list of attendees (**email** and **first name**)
         - Loop through each attendee and send a personalized subject message
         - After the notification, update the notification status with the total number of attendees notified
2. Publish the Azure Function

### Part 3: Refactor `routes.py`
1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis
Complete a month cost analysis of each Azure resource to give an estimate total cost using the table below:

| Azure Resource | Service Tier | Monthly Cost |
| ------------ | ------------ | ------------ |
| *Azure Postgres Database* | Basic | $43.55 |
| *Azure Service Bus* | Basic | $0.01 |
| *Azure App Service* | Premium V3 P1V3 | $113.15 |
| *Azure Storage* | Basic | $0.10 |

Here are explanations for each resource mentioned in my cost analysis:

1/ Azure Postgres Database (Basic):
This resource is an Azure Database for PostgreSQL, which is a managed database service. It's used to store and manage structured data for my application, such as attendees information, notifications.

2/ Azure Service Bus (Basic):
Azure Service Bus is a messaging service used for decoupling application components and enabling asynchronous communication. In my project, it may be used for queuing notification_id. The "Basic" tier is suitable for low to moderate message throughput suitable for admin.

3/ Azure App Service (Premium V3 P1V3):
Azure App Service is a Platform-as-a-Service (PaaS) offering for hosting web applications and APIs. It provides a scalable and managed environment for my web app, which is used for queuing notification_id. The "Premium V3 P1V3" tier is a high-performance option designed for production-level workloads.

4/ Azure Storage (Basic):
Azure Storage is used for storing unstructured data, such as files related to my application. The "Basic" tier provides a cost-effective storage solution for my project's needs.

### Drawbacks of Previous Architecture:

Limited Scalability: The previous architecture, which used a basic web app for both queuing emails and serving web traffic, had limited scalability. During peak periods, the web app could become overwhelmed, leading to performance degradation and potential downtime.

Resource Contention: Resource contention was a significant issue, as email queuing and sending tasks competed with web traffic for resources. This resulted in suboptimal performance and increased latency for both web visitors and email processing.

Inefficient Resource Utilization: The basic web app operated at a fixed resource level, even during low-traffic periods, leading to inefficient resource utilization and unnecessary costs.

### Advantages of the Current Architecture:

Enhanced Scalability: The current architecture, which combines a web app for queuing and Azure Function Apps for email processing, offers enhanced scalability. Azure Function Apps can automatically scale based on demand, ensuring that email processing can handle peak loads effectively without affecting web traffic.

Resource Isolation: Resource isolation is a key advantage of the current architecture. By segregating email processing tasks in Azure Function Apps, resource contention is minimized, resulting in improved performance and responsiveness for both web traffic and email processing.

Cost-Efficiency: The architecture's flexibility and scalability ensure cost-efficiency. Azure Function Apps can automatically adjust resources based on email volume, preventing overprovisioning during low-traffic periods and optimizing costs.


*In summary, the current architecture leverages Azure resources to address the drawbacks of the previous architecture. It provides enhanced scalability, resource isolation, and cost-efficiency, ensuring a better user experience and more effective email processing. Azure's flexible and managed services play a key role in achieving these advantages.*


## Architecture Explanation
I've adopted a two-tier architecture: a web app for queuing notification_id and Azure Function Apps for listing attendees and sending emails. Selecting a production-level server SKU like "P1V3" (estimated $113.15) for my web app is generally a good approach when i have high performance, load, and usage requirements; while email sending costs are variable, depending on email volume and attendees. This choice ensures cost-efficiency for dynamic workloads and enhances overall performance and user experience.