import logging.handlers


log = logging.getLogger('log')
log.setLevel(logging.DEBUG)

file_handler = logging.handlers.RotatingFileHandler(
    'logs/debug.log',
    maxBytes=1000000,
    backupCount=5
)
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
fmtstr = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
fmtdate = '%H:%M:%S'
formatter = logging.Formatter(fmtstr, fmtdate)
file_handler.setFormatter(formatter)
ch.setFormatter(formatter)

log.addHandler(file_handler)
log.addHandler(ch)
