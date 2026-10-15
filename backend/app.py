from flask import Flask

app = Flask(__name__)

@app.route("/")
def ana_sayfa():
    return "Akilli Ders Programi projesi calisiyor!"

if __name__ == "__main__":
    app.run(debug=True)