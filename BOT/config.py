import multiprocessing

REG_USER: str = 'u1488792_userc'
REG_PASS: str = 'nO1yU1vQ8uhG8tC8'
REG_DB: str = 'u1488792_circle'
REG_IP: str = '37.140.192.84'
REG_PORT: int = 3306

POSTGRES_USER: str = 'postgres'
POSTGRES_PASS: str = 'postgres'
POSTGRES_DB: str = 'postgres_db'
POSTGRES_IP: str = 'circle-postgres'
POSTGRES_PORT: int = 5432


DB_MYSQL: str = f'mysql+aiomysql://{REG_USER}:{REG_PASS}@{REG_IP}:{REG_PORT}/{REG_DB}'
DB_POSTGRES: str = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_IP}:{POSTGRES_PORT}/{POSTGRES_DB}'

DATA_INPUT = 'DATA/input/'
TOKEN: str = '7139724856:AAGuY4tkE2KFVneDzizH7eQxxWP-EV-vGtw'
OWNER: int = 239203155
DANIEL: int = 5620433058

BOT = 7139724856
TAG: str = '1'


THREADS: int = max(multiprocessing.cpu_count() - 2, 1)







