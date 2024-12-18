from seatools.ioc.config import cfg
from seatools.ioc.injects import Bean
from seatools.sqlalchemy.utils import new_client
from seatools.utils.dict_utils import deep_update
from loguru import logger
from seatools.sqlalchemy.dbconfig import CommonDBConfig


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
    for name, v in db_config.items():
        try:
            config = CommonDBConfig(**v)
            if config.sqlalchemy:
                if not sqlalchemy_config:
                    sqlalchemy_config = config.sqlalchemy
                else:
                    sqlalchemy_config = deep_update(sqlalchemy_config, config.sqlalchemy)
            client = new_client(config, config=sqlalchemy_config)
            # 注册bean
            Bean(name=config.name or name, primary=config.primary)(client)
        except Exception as e:
            logger.error(f'配置[db.{name}]存在不支持的参数, 请检查修改配置后重试')
            exit(1)

