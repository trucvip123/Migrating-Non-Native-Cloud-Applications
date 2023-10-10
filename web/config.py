import os


class BaseConfig:
    DEBUG = True
    POSTGRES_URL="trucnvserver.postgres.database.azure.com"  #TODO: Update value
    POSTGRES_USER="trucnv@trucnvserver" #TODO: Update value
    POSTGRES_PW="Lumia930@"   #TODO: Update value
    POSTGRES_DB="techconfdb"   #TODO: Update value
    DB_URL = 'postgresql://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
    # postgres://trucnv%40trucnvserver:Lumia930@@trucnvserver.postgres.database.azure.com/postgres?sslmode=require
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or DB_URL
    CONFERENCE_ID = 1
    SECRET_KEY = 'LWd2tzlprdGHCIPHTd4tp5SBFgDszm'
    SERVICE_BUS_CONNECTION_STRING ='Endpoint=sb://trucnvservicebus.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=b7O/MtrNbA/F2mtb5PyQAoFcckJKiLY1O+ASbHiNds0=' #TODO: Update value
    SERVICE_BUS_QUEUE_NAME ='notificationqueue'
    ADMIN_EMAIL_ADDRESS: 'trucvip132@gmail.com'
    SENDGRID_API_KEY = '' #Configuration not required, required SendGrid Account

class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False