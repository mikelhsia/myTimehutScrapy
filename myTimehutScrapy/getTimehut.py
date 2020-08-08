import sys
import os
import re
import pika
import json

import timehutLog
import timehutSeleniumToolKit

if os.getenv("TIMEHUT_DEBUG") is not None:
	import pdb
	pdb.set_trace()

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
	rabbit_result = ''
	timehutLog.logging.info(f'Checking RabbitMQ ... ')
	with os.popen(RABBITMQ_PS_CMD, "r") as f:
		rabbit_result = f.read()

	f.close()

	return False if not rabbit_result else True


def enqueue_timehut_collection(channel, req_list, until=-200):
	next_flag = None

	for request in req_list:
		regex = r'.*&before\=(-?\d*).*'
		result = re.match(regex, request[0])

		if result is not None:
			current = int(result.group(1))
		else:
			current = 3000

		if current >= until:
			next_flag = True
		else:
			next_flag = False
			sys.stdout.write(f' [*] Out of range - collection: {current} < {until} ... \n{request[0]}\n')
			break

		message = {
			"type": PEEKABOO_COLLECTION_REQUEST,
			"request": request[0],
			"header": json.dumps(request[1].__str__().replace("'", "\""))}

		channel.basic_publish(exchange="", routing_key=RABBITMQ_TIMEHUT_QUEUE_NAME,
		                      body=json.dumps(message).encode('UTF-8'),
		                      properties=pika.BasicProperties(delivery_mode=2,
		                                                      content_type='application/json',
		                                                      content_encoding='UTF-8'))

		sys.stdout.write(f' [*] Enqueued - collection ... \n{request[0]}\n')

	return next_flag


def enqueue_timehut_moment(channel, req_list):

	for request in req_list:
		message = {
			"type": PEEKABOO_MOMENT_REQUEST,
			"request": request[0],
			"header": json.dumps(request[1].__str__().replace("'", "\""))}

		channel.basic_publish(exchange="", routing_key=RABBITMQ_TIMEHUT_QUEUE_NAME,
		                      body=json.dumps(message).encode('UTF-8'),
		                      properties=pika.BasicProperties(delivery_mode=2,
		                                                      content_type='application/json',
		                                                      content_encoding='UTF-8'))

		sys.stdout.write(f' [*] Enqueued - moment ... \n{request[0]}\n')


def main():
	# TODO: Using `tkinter` to implement the GUI interface
	baby = input(f'Do you want to get data for \n1) Anson or \n2) Angie\n')

	if baby == '1' or baby == '':
		__baby_id = PEEKABOO_ONON_ID
	else:
		__baby_id = PEEKABOO_MUIMUI_ID

	__timehut = timehutSeleniumToolKit.timehutSeleniumToolKit(PEEKABOO_HEADLESS_MODE)
	__timehut.fetchTimehutLoginPage(PEEKABOO_LOGIN_PAGE_URL)

	if not __timehut.loginTimehut(PEEKABOO_USERNAME, PEEKABOO_PASSWORD):
		timehutLog.logging.info(' [x] Login failed')
		sys.exit(1)
	else:
		sys.stdout.write(' [*] Login success\n')

		if baby == '1' or baby == '':
			sys.stdout.write(' [*] Going to Onon\n')
		else:
			sys.stdout.write(' [*] Going to MuiMui\n')
			mui_mui_homepage = __timehut.getTimehutPageUrl().replace(PEEKABOO_ONON_ID, PEEKABOO_MUIMUI_ID)
			__timehut.fetchTimehutContentPage(mui_mui_homepage)

	### TODO Not yet fully tested
	# __catalog = __timehut.getTimehutCatalog()
	# for k in __catalog:
	# 	print(f'{k}: {__catalog[k]}')
	#
	# start = input(f'Select a date you would like to start with: \n')
	#
	# try:
	# 	__timehut.selectTimehutCatalog(start)
	# except Exception as e:
	# 	timehutLog.logging.error(e)

	until = input(f'What days you would like to stop at: \n -200 (default) ~ XXXXX:\n')

	try:
		__until = int(until)
	except Exception as e:
		__until = -200
		timehutLog.logging.warning(f"before_day format invalid: {type(__until)}")

	__collection_list = []
	moment_set = None
	__cont_flag = True

	connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_SERVICE_DEV_URL))
	channel = connection.channel()
	channel.queue_declare(queue=RABBITMQ_TIMEHUT_QUEUE_NAME, durable=True)

	sys.stdout.write(f' [*] Start scraping the website\n')

	while __cont_flag:
		__timehut.scrollDownTimehutPage()
		# __timehut.scrollDownTimehutPage2()

		__req_list = __timehut.getTimehutRecordedCollectionRequest()

		# Send to queue
		__cont_flag = enqueue_timehut_collection(channel, __req_list, __until)

		moment_set = __timehut.getTimehutAlbumURLSet()
		__timehut.cleanTimehutRecordedRequest()

	# Start dumping all memories after finish updating Collection
	sys.stdout.write("\n-------------------------------\nDone updating collection, start parsing moment_set\n-------------------------------\n")

	i = 0
	l = len(moment_set)

	for moment_link in moment_set:
		i += 1

		__timehut.fetchTimehutContentPage(moment_link)

		__req_list = __timehut.getTimehutRecordedMomeryRequest()
		__timehut.cleanTimehutRecordedRequest()

		# Send to queue
		sys.stdout.write(f'{i}/{l}')
		enqueue_timehut_moment(channel, __req_list)

		# TODO 每次 enqueue 完 都有"Message:"字样

	__timehut.quitTimehutPage()


# Basic interactive interface
if __name__ == "__main__":

	if check_rabbit_exist():
		sys.stdout.write(f' [*] RabbitMQ is running ... \n')
	else:
		sys.stderr.write(f" [x] RabbitMQ is not running. Please run `sudo rabbit-mq` on the server first\n")
		sys.exit(1)

	main()
