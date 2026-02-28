from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Canteen Project Working!"

if __name__ == "__main__":
    app.run(debug=True)
