# Seatools-starter-sqlalchemy

seatools ioc 的 sqlalchemy 启动器

## 仓库地址:
1. https://github.com/seatools-py/seatools-starter-sqlalchemy
2. https://gitee.com/seatools-py/seatools-starter-sqlalchemy

## 使用指南
1. 安装, `poetry add seatools-starter-sqlalchemy`
2. 配置文件配置如下
```yaml
# 数据库配置
db:
  # bean名称
  demo_db:
    host: xxx
    port: 1234
    user: xxx
    password: sss
    db: xxx
    orm_schema: sqlite # 其他示例, sqlite+aiosqlite (异步), mysql+pymysql, hive, clickhouse 等
    primary: false # 是否默认bean
```
3. 使用示例
```python
from seatools.ioc import run, Autowired
from seatools.sqlalchemy.decorators.ioc import new_session
from sqlalchemy.orm import Session
from seatools.sqlalchemy import SqlAlchemyClient


# 启动ioc
run(scan_package_names=['seatools.ioc.starters.sqlalchemy'], config='./config')

"""
方式一, 通过装饰器, 推荐
"""
@new_session
def xxx(session: Session):
    ...

# 调用
xxx()


# 方式二, 不推荐
client = Autowired(cls=SqlAlchemyClient)

with client.session() as session:
    ...

```
