from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello World!'

# 确保有这个处理404的路由
@app.errorhandler(404)
def not_found(e):
    return "404 - 页面未找到", 404

# vercel需要这个
app = app