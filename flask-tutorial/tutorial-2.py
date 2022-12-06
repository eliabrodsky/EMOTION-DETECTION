from flask import Flask, redirect, url_for, render_template

app = Flask(__name__) # name is constructor

# decorator
@app.route("/<name>/")  # To access the page
def home(name):
    return render_template("index.html", content=name, r=16, a_list=['Ismail','Ali','Haris'])


# @app.route("/<name>")
# def user(name):
#     return f"Hello {name}!"

# @app.route("/admin/")
# def admin():
#     return redirect(url_for("user", name="Admin!")) # func name in url, variable name = value
if __name__ == '__main__':
    app.run()