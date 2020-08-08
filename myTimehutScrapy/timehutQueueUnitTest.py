import pika

import unittest
import sys
import json
import os

if os.getenv("TIMEHUT_DEBUG") is not None:
    import pdb
    pdb.set_trace()

RABBITMQ_PS_CMD = "ps -ef | grep rabbitmq-server | grep sbin | grep -v grep | awk '{print $2}'"
RABBIT_SERVICE_DEV_URL = 'localhost'
TIMEHUT_RABBITMQ_QUEUE_NAME = 'timehut_queue'

mock_collection_request = 'http://47.52.234.52/events.json?baby_id=537413380&v=2&width=700&include_rt=true&timestamp=1555119640&sign=abab0033bde56a74ff657191be8e34f8'
mock_collection_header = "{'Host': '47.52.234.52', 'Proxy-Connection': 'keep-alive', 'Accept': 'application/json, text/javascript, */*; q=0.01', 'X-NewRelic-ID': 'VwIPUF9SGwAGVlBRAAk=', 'X-Requested-With': 'XMLHttpRequest', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36', 'Referer': 'http://47.52.234.52/en/home/537413380', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.9', 'Cookie': 'locale=en; user_session=BAhJIj1qcF81MzY5MjMzNjNfU2dXeV9kMjFJcklTSElHYUVMZGdCVFNQUnZoOHlQT0RmMGR1d2xOUmdKVQY6BkVU--c45ddb3234e7259ee476c918f7826c9fff979cdf'}"
mock_moment_request = 'http://47.75.157.88/events/691967865671127659?timestamp=1555251647&sign=ca4f1ae30e4e8277f6b0508883f3ad51'
mock_moment_header = "{'Host': '47.75.157.88', 'Proxy-Connection': 'keep-alive', 'Accept': 'application/json, text/javascript, */*; q=0.01', 'X-NewRelic-ID': 'VwIPUF9SGwAGVlBRAAk=', 'X-Requested-With': 'XMLHttpRequest', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36', 'Referer': 'http://47.75.157.88/album_detail/537413380?id=691967865671127659', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.9', 'Cookie': 'locale=en; user_session=BAhJIj1qcF81MzY5MjMzNjNfUmtRVlFYNEZVVndXX0hOa1Nsdnh6bHNNSGhJdFZjSF9uZXdCdTYxbVlrbwY6BkVU--2c63befd401b0ac0a47a96727da51beaafbbda13'}"


def check_rabbit_exist():
    rabbit_result = ''
    sys.stdout.write(f'Checking RabbitMQ ... \n')
    with os.popen(RABBITMQ_PS_CMD, "r") as f:
        rabbit_result = f.read()
    f.close()

    return False if not rabbit_result else True


class MyTest(unittest.TestCase):  # 继承unittest.TestCase
    @classmethod
    def tearDownClass(cls):
        # 必须使用@classmethod 装饰器, 所有test运行完后运行一次
        print('End Timehut testing')
        print('----------------------------------')

    @classmethod
    def setUpClass(cls):
        # 必须使用@classmethod 装饰器,所有test运行前运行一次
        print('----------------------------------')
        print('Start Timehut testing')

    def tearDown(self):
        # 每个测试用例执行之后做操作
        # print('Tearing down the test env ...')
        print('Done tearing down the test env')

    def setUp(self):
        # 每个测试用例执行之前做操作
        # print('Setting up for the test ...')

        print('Done setting up for the test')

    def test_rabbitMQ_publish_collection(self):
        print('\n### Testing behavior of scrolling down to trigger ajax call to get more content')
        if check_rabbit_exist():
            sys.stdout.write(f'RabbitMQ is running ... \n')
        else:
            sys.stdout.write(f"Error: RabbitMQ is not running. Please run `sudo rabbit-mq` on the server first\n")
            self.assertEqual(0, 1)  # 测试用例

        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_SERVICE_DEV_URL))
        channel = connection.channel()
        channel.queue_declare(queue=TIMEHUT_RABBITMQ_QUEUE_NAME, durable=True)

        message = {"type": "collection", "request": mock_collection_request, "header": json.dumps(mock_collection_header)}
        
        channel.basic_publish(exchange='', routing_key=TIMEHUT_RABBITMQ_QUEUE_NAME,
                              body=json.dumps(message).encode('UTF-8'),
                              properties=pika.BasicProperties(delivery_mode=2,
                                                              content_type='application/json',
                                                              content_encoding='UTF-8'))

        print(f' [x] Message sent')
        connection.close()
        # check_db()
        # delete_to_db()
        self.assertEqual(0, 0)  # 测试用例

    def test_rabbitMQ_publish_moment(self):
        print('\n### Testing behavior of scrolling down to trigger ajax call to get more content')
        if check_rabbit_exist():
            sys.stdout.write(f'RabbitMQ is running ... \n')
        else:
            sys.stdout.write(f"Error: RabbitMQ is not running. Please run `sudo rabbit-mq` on the server first\n")
            self.assertEqual(0, 1)  # 测试用例

        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_SERVICE_DEV_URL))
        channel = connection.channel()
        channel.queue_declare(queue=TIMEHUT_RABBITMQ_QUEUE_NAME, durable=True)

        message = {"type": "moment", "request": mock_moment_request, "header": json.dumps(mock_moment_header)}

        channel.basic_publish(exchange='', routing_key=TIMEHUT_RABBITMQ_QUEUE_NAME,
                              body=json.dumps(message).encode('UTF-8'),
                              properties=pika.BasicProperties(delivery_mode=2,
                                                              content_type='application/json',
                                                              content_encoding='UTF-8'))

        print(f' [x] Message sent')
        connection.close()
        # check_db()
        # delete_to_db()
        self.assertEqual(0, 0)  # 测试用例


if __name__ == '__main__':
    unittest.main()  # 运行所有的测试用例
