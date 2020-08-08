from sqlalchemy import Column, String, Integer, DateTime, Text, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

import enum
class CollectionEnum(enum.Enum):
	collection = 1
	text = 2
	picture = 3
	video = 4

class MomentEnum(enum.Enum):
	text = 1
	rich_text = 2
	picture = 3
	video = 4

base = declarative_base()

class Collection(base):
	__tablename__ = 'peekaboo_collection'

	id = Column(String(32), primary_key=True)
	baby_id = Column(String(32))
	created_at = Column(Integer)
	updated_at = Column(Integer)
	months = Column(Integer)
	days = Column(Integer)
	content_type = Column(SmallInteger)
	caption = Column(Text)

	def __repr__(self):
		return (f'\n---- Collection ----\n' 
		       f'id: {self.id}\n' 
		       f'baby_id: {self.baby_id}\n' 
		       f'created_at: {self.created_at}\n' 
		       f'updated_at: {self.updated_at}\n'
		       f'months: {self.months} \n' 
		       f'days: {self.days} \n' 
		       f'content_type: {self.content_type}\n' 
		       f'caption: {self.caption} \n' 
		       f'--------------------')



class Moment(base):
	__tablename__ = 'peekaboo_moment'

	id = Column(String(32), primary_key=True)
	event_id = Column(String(32), ForeignKey(f'{Collection.__tablename__}.id'))
	collection = relationship("Collection", backref=__tablename__)
	baby_id = Column(String(32))
	created_at = Column(Integer)
	updated_at = Column(Integer)
	content_type = Column(SmallInteger)
	content = Column(Text)
	src_url = Column(String(512))
	months = Column(Integer)
	days = Column(Integer)

	def __repr__(self):
		return (f'\n------ Moment ------\n'
		       f'id: {self.id}\n'
		       f'event_id: {self.event_id}\n'
		       f'baby_id: {self.baby_id}\n'
		       f'created_at: {self.created_at}\n'
		       f'updated_at: {self.updated_at}\n'
		       f'content_type: {self.content_type}\n'
		       f'content: {self.content}\n'
		       f'src_url: {self.src_url}\n'
		       f'months: {self.months}\n'
		       f'days: {self.days}\n'
		       f'--------------------')

print(f"Module {__file__} is loaded...")
