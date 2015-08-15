from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import *
from sqlalchemy.schema import *

Base = declarative_base()

class Calls(Base):
	__tablename__ = "Calls"
	id = Column('SID', Text(), primary_key=True,nullable=False)
	pnum = Column('pnum', Integer(), nullable=False)
	recordings = Column('recordings', Text(), nullable=True)

	def __init__(self, rid, pnum, recordings):
		self.id = rid
		self.pnum = pnum
		self.recordings = recordings

	def __repr__(self):
		return "<Calls(%s,%s,%s)>" % (self.id, self.pnum, self.recordings)
