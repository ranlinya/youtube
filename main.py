from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello World!'

@app.errorhandler(404)
def not_found(e):
    return "404 - 页面未找到", 404

@app.errorhandler(500)
def server_error(e):
    return "500 - 服务器错误", 500

# 正确的导出方式
if __name__ == '__main__':
    app.run()