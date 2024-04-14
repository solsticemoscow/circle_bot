import os
from sqlalchemy import create_engine, Column, Integer, String, inspect, and_, text, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class Task:
    def __init__(self, task_type: str, tg_id: int, video_note_time: int, complete: bool = False):
        self.task_type = task_type
        self.complete = complete
        self.tg_id = tg_id
        self.video_note_time = video_note_time

    def to_dict(self):
        return self.__dict__


# создаем директорию для базы данных, если ее не существует
if not os.path.exists('dbs'):
    os.makedirs('dbs')

engine = create_engine('sqlite:///dbs/tasks.db', echo=False)

Base = declarative_base()


class TasksModel(Base):
    __tablename__ = 'tasks'

    tg_id = Column(BigInteger, primary_key=True)
    task_type = Column(String)
    complete = Column(Boolean)
    video_note_time = Column(Integer)


inspector = inspect(engine)
if not inspector.has_table(TasksModel.__tablename__):
    Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

try:
    with engine.connect() as connection:
        alter_statement = text("ALTER TABLE tasks ADD COLUMN repeat INT")
        connection.execute(alter_statement)
except Exception:
    pass


def add_task(task: Task):
    new_task = TasksModel(
        id=task.tg_id,
        task_type=task.task_type,
        complete=task.complete,
        video_note_time=task.video_note_time,
    )
    session.add(new_task)
    session.commit()
    return new_task.tg_id


def update_task(task: Task):
    session.query(TasksModel).filter_by(telegram_id=task.tg_id).update({
        TasksModel.task_type: task.task_type,
        TasksModel.complete: task.complete,
        TasksModel.id: task.tg_id,
        TasksModel.video_note_time: task.video_note_time,
    })
    session.commit()


def can_add_task(telegram_id: int):
    a = session.query(TasksModel).filter(and_(TasksModel.tg_id == telegram_id, TasksModel.complete == 0)).first()
    if a:
        return False
    return True


def find_first_incomplete():
    return session.query(TasksModel).filter_by(complete=0).first()


def get_all_incomplete():
    return session.query(TasksModel).filter_by(complete=0).all()


def delete_all_complete():
    completed = session.query(TasksModel).filter_by(complete=1).all()
    for i in completed:
        session.delete(i)
        session.commit()


TASK: Task = {
    "tg_id": 239203155,
    "task_type": "1",
    "complete": False,
    "video_note_time": 5
}

print(add_task(task=TASK))
