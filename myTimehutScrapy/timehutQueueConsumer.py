import pika
import json
import requests
import os
import sys

import timehutLog
import timehutManageDB
import timehutDataSchema
from datetime import datetime

if os.getenv("TIMEHUT_DEBUG") is not None:
	import pdb
	pdb.set_trace()

RABBITMQ_SERVICE_DEV_URL = 'localhost'
RABBITMQ_TIMEHUT_QUEUE_NAME = 'timehut_queue'
RABBITMQ_PS_CMD = "ps -ef | grep rabbitmq-server | grep sbin | grep -v grep | awk '{print $2}'"

PEEKABOO_DB_NAME = 'peekaboo'

ENABLE_DB_LOGGING = False


# TODO better console message while parsing
class timehutQueueConsumer(object):
	def __init__(self):
		pass

	def DatetimeStringToTimeStamp(self, string):
		"""
		Convert datetime format into timestamp
		:param ts: string
		:return: timestamp
		"""
		string = string.split('+')[0]
		string = string.split('Z')[0]
		try:
			dt = datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.%f")
		except Exception as e:
			print(e)
			raise e

		return dt.timestamp()

	def parseCollectionBody(self, response_body):
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


	def parseMomentBody(self, response_body):

		moment_list = []
		response_body = json.loads(response_body)
		data_list = response_body['moments']
		src_url = ''

		for data in data_list:
			if data['type'] == 'picture':
				src_url = data['picture']
			elif data['type'] == 'video':
				src_url = data['video_path']

			m_rec = timehutDataSchema.Moment(id=data['id_str'],
											 event_id=data['event_id_str'],
											 baby_id=data['baby_id'],
											 created_at=data['taken_at_gmt'],
											 updated_at=self.DatetimeStringToTimeStamp(data['updated_at']),
											 content_type=timehutDataSchema.MomentEnum[data['type']].value,
											 content=data['content'],
											 src_url=src_url,
											 months=data['months'],
											 days=data['days'])

			# Add to return collection obj list
			moment_list.append(m_rec)
			# print(m_rec)

		return moment_list

	def onMessageCallback(self, ch, method, properties, body):
		response = json.loads(body)

		request = response["request"]
		# 将字符串转换为字典
		header = eval(json.loads(response["header"]))

		try:
			r = requests.get(url=request, headers=header, timeout=30)
			r.raise_for_status()
		except requests.RequestException as e:
			print(f'{e}')
		else:
			if response["type"] == "collection":
				print(f' [*] Receive collection')

				collection_list = self.parseCollectionBody(r.text)
				timehutManageDB.updateDBCollection(collection_list, self.collection_index_list, self._session)
			else:
				print(f' [*] Receive moment')
				moment_list = self.parseMomentBody(r.text)
				timehutManageDB.updateDBMoment(moment_list, self.moment_index_list, self._session)

		print(f' [*] Done')
		ch.basic_ack(delivery_tag=method.delivery_tag)

	def onChannelCloseCallback(self):
		# print('on connection close')
		timehutManageDB.closeSession(self._session)

	def onChannelOpenCallback(self):
		# print('on connection open')
		timehutManageDB.createDB(PEEKABOO_DB_NAME, timehutDataSchema.base, ENABLE_DB_LOGGING)
		self._engine = timehutManageDB.createEngine(PEEKABOO_DB_NAME, ENABLE_DB_LOGGING)
		self._session = timehutManageDB.createSession(self._engine)
		self.collection_index_list, self.moment_index_list = timehutManageDB.generateIndexList(self._session)

	def run(self):
		connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVICE_DEV_URL))
		channel = connection.channel()

		self.onChannelOpenCallback()

		channel.queue_declare(queue=RABBITMQ_TIMEHUT_QUEUE_NAME, durable=True)
		sys.stdout.write(f' [*] Waiting for message. To exit press CTRL+C\n')

		channel.basic_qos(prefetch_count=1)
		channel.basic_consume(queue=RABBITMQ_TIMEHUT_QUEUE_NAME, on_message_callback=self.onMessageCallback)

		try:
			channel.start_consuming()
		except KeyboardInterrupt:
			channel.stop_consuming()
			sys.stdout.write(f'Keyboard Interrupt\n')
		except Exception as e:
			channel.stop_consuming()
			timehutLog.logging.error(f'{e}')

		self.onChannelCloseCallback()
		connection.close()


def check_rabbit_exist():
	rabbit_result = ''
	timehutLog.logging.info(f'Checking RabbitMQ ... ')
	with os.popen(RABBITMQ_PS_CMD, "r") as f:
		rabbit_result = f.read()

	f.close()

	return False if not rabbit_result else True


if __name__ == "__main__":

	if check_rabbit_exist():
		sys.stdout.write(f' [*] RabbitMQ is running ... \n')
	else:
		sys.stderr.write(f" [x] RabbitMQ is not running. Please run `sudo rabbit-mq` on the server first\n")
		sys.exit(1)

	queueConsumer = timehutQueueConsumer()
	queueConsumer.run()
