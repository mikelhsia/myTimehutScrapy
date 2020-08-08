import mitmproxy.http
from mitmproxy import ctx

import json
import timehutDataSchema

import re
import pika
import sys
import subprocess

# Constant list
PEEKABOO_USERNAME = "mikelhsia@hotmail.com"
PEEKABOO_PASSWORD = "f19811128"
PEEKABOO_ONON_ID = "537413380"
PEEKABOO_MUIMUI_ID = "537776076"
PEEKABOO_DB_NAME = "peekaboo"
PEEKABOO_LOGIN_PAGE_URL = "https://www.shiguangxiaowu.cn/zh-CN"
PEEKABOO_HEADLESS_MODE = True
PEEKABOO_COLLECTION_REQUEST = "collection"
PEEKABOO_MOMENT_REQUEST = "moment"

RABBITMQ_PS_CMD = "ps -ef | grep rabbitmq-server | grep sbin | grep -v grep | awk '{print $2}'"
RABBITMQ_SERVICE_DEV_URL = "localhost"
RABBITMQ_TIMEHUT_QUEUE_NAME = "timehut_queue"


def check_rabbit_exist():
    sys.stdout.write(f'Checking RabbitMQ ... \n')
    rabbit_result = subprocess.getoutput(RABBITMQ_PS_CMD)

    return True if rabbit_result else False


def parseCollectionBody(response_body):
    collection_list = []

    response_body = json.loads(response_body)
    data_list = response_body['list']

    for data in data_list:

        if data['layout'] == 'collection' or \
                data['layout'] == 'picture' or \
                data['layout'] == 'video' or \
                data['layout'] == 'text':

            c_rec = timehutDataSchema.Collection(id=data['id_str'],
                                                 baby_id=data['baby_id'],
                                                 created_at=data['taken_at_gmt'],
                                                 updated_at=data['updated_at_in_ts'],
                                                 months=data['months'],
                                                 days=data['days'],
                                                 content_type=timehutDataSchema.CollectionEnum[data['layout']].value,
                                                 caption=data['caption'])

            # Add to return collection obj list
            collection_list.append(c_rec)
            # print(c_rec)

        elif data['layout'] == 'milestone':
            continue

        else:
            print(data)
            raise TypeError

    return collection_list


def enqueue_timehut_collection(channel, url, headers):

    print(headers)
    message = {
        "type": PEEKABOO_COLLECTION_REQUEST,
        "request": url,
        "header": json.dumps(headers.__str__().replace("'", "\""))}

    channel.basic_publish(exchange="", routing_key=RABBITMQ_TIMEHUT_QUEUE_NAME,
                          body=json.dumps(message).encode('UTF-8'),
                          properties=pika.BasicProperties(delivery_mode=2,
                                                          content_type='application/json',
                                                          content_encoding='UTF-8'))

    sys.stdout.write(f' [*] Enqueued - collection ... \n{url}\n')

    return


def enqueue_timehut_moment(channel, url, headers):

    message = {
        "type": PEEKABOO_MOMENT_REQUEST,
        "request": url,
        "header": json.dumps(headers.__str__().replace("'", "\""))}


    channel.basic_publish(exchange="", routing_key=RABBITMQ_TIMEHUT_QUEUE_NAME,
                          body=json.dumps(message).encode('UTF-8'),
                          properties=pika.BasicProperties(delivery_mode=2,
                                                          content_type='application/json',
                                                          content_encoding='UTF-8'))

    sys.stdout.write(f' [*] Enqueued - moment ... \n{url}\n')

class bcolors:
    '''
    To color the response when print or console write
    '''
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @classmethod
    def style(cls, string: str, color: str):
        return f'{color}{string}{cls.ENDC}'


class TimehutScraper:
    collectionIdList = []
    connection = ''
    channel = ''

    def __init__(self):
        collectionIdList = []

        if check_rabbit_exist():
            sys.stdout.write(f' [*] RabbitMQ is running ... \n')
        else:
            sys.stderr.write(f" [x] RabbitMQ is not running. Please run `sudo rabbit-mq` on the server first\n")

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVICE_DEV_URL))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=RABBITMQ_TIMEHUT_QUEUE_NAME, durable=True)

        sys.stdout.write(f' [*] Start scraping the website\n')

    def request(self, flow: mitmproxy.http.HTTPFlow):
        if 'events/updates' in flow.request.path:
            ctx.log(bcolors.style(flow.request.pretty_url, bcolors.OKBLUE))

        elif 'events' in flow.request.path and 'comments' not in flow.request.path:
            ctx.log(bcolors.style(flow.request.pretty_url, bcolors.OKBLUE))
            # ctx.log(bcolors.style(flow.request.headers, bcolors.OKBLUE))

    def response(self, flow: mitmproxy.http.HTTPFlow):
        if 'events/updates' in flow.request.path:
            collectionList = parseCollectionBody(flow.response.content)
            self.collectionIdList += [x.id for x in collectionList]

            url = flow.request.url
            headers = {key:flow.request.headers[key] for key in flow.request.headers}

            headers = json.dumps(headers)
            enqueue_timehut_collection(self.channel, url, headers)

        elif 'events' in flow.request.path and 'comments' not in flow.request.path:
            regex = r'(.*events/)(\d+)'
            result = re.match(regex, flow.request.url)
            host = result.group(1)
            # ctx.log(bcolors.style(self.collectionIdList, bcolors.OKBLUE))
            headers = {key:flow.request.headers[key] for key in flow.request.headers}
            headers = json.dumps(headers)

            for collectionId in self.collectionIdList:
                url = host + collectionId
                enqueue_timehut_moment(self.channel, url, headers)


addons = [
    TimehutScraper()
]