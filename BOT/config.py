import multiprocessing
import os.path

ROOT_DIR: str = os.path.dirname((__file__))
ROOT_DIR_ABS = os.path.abspath((__file__))
DATA_INPUT = ROOT_DIR + '/data/input/'



REG_USER: str = 'u1488792_userc'
REG_PASS: str = 'nO1yU1vQ8uhG8tC8'
REG_DB: str = 'u1488792_circle'
REG_IP: str = '37.140.192.84'
REG_PORT: int = 3306

MYSQL_USER: str = 'root'
MYSQL_PASS: str = 'secret'
MYSQL_DB: str = 'DB'
MYSQL_IP: str = 'circle-mysql_db'
MYSQL_IP: str = 'localhost'
MYSQL_PORT: int = 3306

DB_MYSQL_DOCKER: str = f'mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_IP}:{MYSQL_PORT}/{MYSQL_DB}'
DB_MYSQL: str = f'mysql+aiomysql://{REG_USER}:{REG_PASS}@{REG_IP}:{REG_PORT}/{REG_DB}'

TOKEN: str = '7139724856:AAGuY4tkE2KFVneDzizH7eQxxWP-EV-vGtw'
OWNER: int = 239203155
DANIEL: int = 5620433058

BOT = 7139724856
TAG: str = '1'


THREADS: int = max(multiprocessing.cpu_count() - 2, 1)







