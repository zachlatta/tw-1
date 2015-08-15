from sqlalchemy.engine.url import URL
from sqlalchemy import MetaData, create_engine, Table, Column 
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import *
from tables import *

class DB():
	def engineConnect(self):
		return create_engine('sqlite:///db.db', echo=False)

	def __init__(self, connect=True):
		if connect:
			self.engine = self.engineConnect()
			self.Session = sessionmaker(bind=self.engine)
			self.session = self.Session()
			try:
				Base.metadata.bind = self.engine
				Base.metadata.create_all()
			except:
				print "error"
				raise

	def addEntry(self, entry):
		try:
			if not self.getEntry(entry.__class__, (entry.__class__.id == entry.id)).count():
				self.session.add(entry)
				self.session.commit()
				print "added"
			print "not added"
			return entry.id
		except BaseException as e:
			print e
			self.session.rollback()
			return None

	def updateEntry(self, entry_type, entryId, data):
		try:
			entry = self.getEntry(entry_type, (entry_type.id == entryId))[0]
		except IndexError:
			print "Record not found"
			# self.session.rollback()
			return None

		for k, v in data.items():
			if k == "recordings":
				tmplst = eval(entry.recordings)
				tmplst.append(v)
				setattr(entry, k, str(tmplst))
			else:
				setattr(entry, k, v)

		try:
			self.session.add(entry)
			return self.session.commit()
		except BaseException as e:
			print e
			self.session.rollback()
			return None

	def getEntry(self, entry_type, efilter):
		try:
			if efilter is not None:
				query = self.session.query(entry_type).filter(efilter)
			else:
				query = self.session.query(entry_type)
		except BaseException as e:
			print e

		try:
			return query
		except BaseException as e:
			self.session.rollback()
			print e