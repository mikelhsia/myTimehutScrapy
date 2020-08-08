import sys
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InternalError

import timehutDataSchema
import timehutLog

if os.getenv('USER') == 'michael':
	DB_ACCOUNT = "root"
	DB_PASSWORD = "hsia0521"
	DB_HOST = "127.0.0.1"
	DB_PORT = "3306"
	DB_ENCODING = "utf-8"
else:
	DB_ACCOUNT = "root"
	DB_PASSWORD = "michael0512"
	DB_HOST = "127.0.0.1"
	DB_PORT = "3306"
	DB_ENCODING = "utf-8"


def createDB(dbName, base, loggingFlag):
	engine = create_engine(f'mysql+pymysql://{DB_ACCOUNT}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}',
	                       encoding=DB_ENCODING, echo=loggingFlag)

	try:
		engine.execute(f"CREATE DATABASE IF NOT EXISTS {dbName} DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;")
		# timehutLog.logging.info(f"CREATE DATABASE IF NOT EXISTS {dbName} DEFAULT CHARSET utf8mb4 COLLATE utf8_general_ci;")

		engine.execute(f"USE {dbName}")
		# timehutLog.logging.info(f"USE {dbName}")

		ans = input(f"Do you want to drop the previous saved table (y/N)")

		if ans == 'y' or ans == 'Y':
			engine.execute(f"DROP TABLE {timehutDataSchema.Moment.__tablename__}")
			# timehutLog.logging.info(f"DROP TABLE {timehutDataSchema.Moment.__tablename__}")

			engine.execute(f"DROP TABLE {timehutDataSchema.Collection.__tablename__}")
			# timehutLog.logging.info(f"DROP TABLE {timehutDataSchema.Collection.__tablename__}")

	except InternalError as e:
		base.metadata.create_all(engine)

		engine.execute(f"ALTER DATABASE {dbName} CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;")
		engine.execute(f"ALTER TABLE {timehutDataSchema.Collection.__tablename__} CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
		engine.execute(f"ALTER TABLE {timehutDataSchema.Collection.__tablename__} MODIFY caption TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
		engine.execute(f"ALTER TABLE {timehutDataSchema.Moment.__tablename__} CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
		engine.execute(f"ALTER TABLE {timehutDataSchema.Moment.__tablename__} MODIFY content TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")

	finally:
		engine.dispose()


def createEngine(dbName, loggingFlag):

	engine = create_engine(f'mysql+pymysql://{DB_ACCOUNT}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{dbName}?charset=utf8mb4',
	                       encoding=DB_ENCODING, echo=loggingFlag)

	return engine


def createSession(engine):
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	return session


def closeSession(session):
	session.close()


def generateIndexList(session):
	__collectionIndexList = []
	__momentIndexList = []

	for row in session.query(timehutDataSchema.Collection):
		__collectionIndexList.append(row.id)

	for row in session.query(timehutDataSchema.Moment):
		__momentIndexList.append(row.id)

	return __collectionIndexList, __momentIndexList


def updateDBCollection(data_list, existed_index_list, session):
	"""

	:param data_list
	:return: 
	"""
	if not isinstance(data_list, list):
		# If it's an single object, then put it in the list to simplify the following logic
		data_list = [data_list]

	for data in data_list:
		if isinstance(data, timehutDataSchema.Collection):
			if data.id not in existed_index_list:
				# Insert collection object
				session.add(data)
		else:
			timehutLog.logging.error(f'[{sys._getframe().f_code.co_name}] Wrong Collection Type')
			return False
	else:
		session.commit()


def updateDBMoment(data_list, existed_index_list, session):
	"""

	:param data_list
	:return: 
	"""
	if not isinstance(data_list, list):
		# If it's an single object, then put it in the list to simplify the following logic
		data_list = [data_list]

	for data in data_list:
		if isinstance(data, timehutDataSchema.Moment):
			if data.id not in existed_index_list:
				# Insert collection object
				session.add(data)
		else:
			timehutLog.logging.error(f'[{sys._getframe().f_code.co_name}] Wrong Moment Type')
			return False
	else:
		session.commit()
