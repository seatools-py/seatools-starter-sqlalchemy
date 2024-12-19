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
    # 兼容旧配置
    elif 'db' in config:
        db_config = config['db']

    # 兼容旧配置sqlalchemy
    sqlalchemy_config = (config.get('seatools') or {}).get('sqlalchemy') or config.get('sqlalchemy')

    if not db_config:
        logger.warning('配置[seatools.datasource]不存在, 无法自动初始化数据库bean实例')
        return
    if not isinstance(db_config, dict):
        logger.error('配置[seatools.datasource]属性不是字典类型, 无法自动初始化数据库bean实例')
        exit(1)
    bean_factory = get_bean_factory()
    for name, v in db_config.items():
        try:
            config = CommonDBConfig(**v)
            if config.sqlalchemy:
                if not sqlalchemy_config:
                    sqlalchemy_config = config.sqlalchemy
                else:
                    sqlalchemy_config = deep_update(sqlalchemy_config, config.sqlalchemy)
            if sqlalchemy_config and 'session_cls' in sqlalchemy_config:
                cls = __get_session_cls(sqlalchemy_config['session_cls'])
                if cls is not None:
                    sqlalchemy_config['cls'] = cls
                else:
                    del sqlalchemy_config['session_cls']
            client = new_client(config, config=sqlalchemy_config)
            # 注册bean, 非延迟注册
            bean_factory.register_bean(name=config.name or name, cls=client, primary=config.primary, lazy=False)
        except Exception as e:
            logger.error(f'配置[seatools.datasource.{name}]存在不支持的参数, 请检查修改配置后重试')
            exit(1)
