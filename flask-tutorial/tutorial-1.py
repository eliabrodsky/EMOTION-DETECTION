from flask import Flask, redirect, url_for

app = Flask(__name__) # name is constructor

# decorator
@app.route("/home/")  # To access the page
def home():
    return "Hello! this is the main page <h1>HELLO</h1>" # inline html

@app.route("/<name>/")
def user(name):
    return f"Hello {name}!"

@app.route("/admin/")
def admin():
    return redirect(url_for("home"))
if __name__ == '__main__':
    app.run()