from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
ENV_FILE = ROOT_DIR / '.env'
ALEMBIC_DIR = APP_DIR / 'database' / 'migration'
ALEMBIC_INI = ROOT_DIR / 'alembic.ini'
ALEMBIC_VERSIONS_DIR = ALEMBIC_DIR / 'versions'
HOME_DIR = Path.home()
