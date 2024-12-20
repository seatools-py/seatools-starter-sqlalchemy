import importlib

from seatools.ioc.config import cfg
from seatools.ioc.base import get_bean_factory
from seatools.ioc.injects import Bean
from seatools.sqlalchemy.utils import new_client
from seatools.utils.dict_utils import deep_update
from loguru import logger
from seatools.sqlalchemy.dbconfig import CommonDBConfig



def __get_session_cls(module_cls: str):
    module_cls_seq = module_cls.split('.')
    module_name, class_name = '.'.join(module_cls_seq[:-1]), module_cls_seq[-1]
    return getattr(importlib.import_module(module_name) if module_name else globals(), class_name, None)


@Bean
def init_db_beans():
    db_config, sqlalchemy_config = None, None
    config = cfg()
    if 'seatools' in config and 'datasource' in config['seatools']:
        db_config = config['seatools']['datasource']
    # Backward compatibility with old configuration
    elif 'db' in config:
        db_config = config['db']

    # Backward compatibility with old sqlalchemy configuration
    sqlalchemy_config = (config.get('seatools') or {}).get('sqlalchemy') or config.get('sqlalchemy')

    if not db_config:
        logger.warning('Configuration [seatools.datasource] does not exist, unable to automatically initialize database bean instances.')
        return
    if not isinstance(db_config, dict):
        logger.error('Configuration [seatools.datasource] property is not of dict type, unable to automatically initialize database bean instances.')
        exit(1)
    bean_factory = get_bean_factory()
    for name, v in db_config.items():
        config = CommonDBConfig(**v)
        if config.sqlalchemy:
            if not sqlalchemy_config:
                sqlalchemy_config = config.sqlalchemy
            else:
                sqlalchemy_config = deep_update(sqlalchemy_config, config.sqlalchemy)
        if sqlalchemy_config and 'session_cls' in sqlalchemy_config:
            cls = __get_session_cls(sqlalchemy_config['session_cls'])
            if cls is not None:
                sqlalchemy_config['session_cls'] = cls
            else:
                del sqlalchemy_config['session_cls']
        client = new_client(config, config=sqlalchemy_config)
        # Register bean, not a lazy registration
        bean_factory.register_bean(name=config.name or name, cls=client, primary=config.primary, lazy=False)
