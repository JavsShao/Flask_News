from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import create_app, db


# 创建app
app = create_app('dev')

# 创建脚本管理器对象
manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


@app.route('/index')
def index():
    return 'index'

if __name__ == '__main__':
    app.run()