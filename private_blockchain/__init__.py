from flask import Flask

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

if __name__ == '__main__':
    app.run()
