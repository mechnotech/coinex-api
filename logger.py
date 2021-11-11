import logging.handlers

from settings import DEBUG, VERBOSITY_LEVELS, VERBOSITY

log = logging.getLogger('log')
log.setLevel(logging.DEBUG if DEBUG else logging.INFO)

file_handler = logging.handlers.RotatingFileHandler(
    'logs/debug.log',
    maxBytes=5000000,
    backupCount=5
)
ch = logging.StreamHandler()
ch.setLevel(VERBOSITY_LEVELS[VERBOSITY])
fmtstr = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
fmtdate = '%H:%M:%S'
formatter = logging.Formatter(fmtstr, fmtdate)
file_handler.setFormatter(formatter)
ch.setFormatter(formatter)

log.addHandler(file_handler)
log.addHandler(ch)
