import logging
import os
logging.basicConfig(style='{',
                    format='[{name}:{levelname}] In {funcName}: {message}',
                    level=getattr(logging, os.getenv('LOG', ''), logging.WARNING))