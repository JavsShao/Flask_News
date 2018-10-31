from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db, models



# 创建app
app = create_app('dev')

# 创建脚本管理器对象
manager = Manager(app)

# 数据库迁移
Migrate(app, db)
manager.add_command('mysql', MigrateCommand)


if __name__ == '__main__':
    manager.run()