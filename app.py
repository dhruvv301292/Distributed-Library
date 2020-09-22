from flask import Flask, jsonify

app = Flask(__name__)

library = {}
library["Harry Potter"] = 4
library["Asterix"] = 3

@app.route("/")
def intro():
    introString = "Welcome to the library. You may borrow the following books:\n"
    for key in library:
        introString += str(key) + "\n"
    return introString

@app.route("/heartbeat")
def heartbeat():
    # return jsonify({"status": "healthy"})
    return "Alive"

@app.route("/info/<bookName>")
def infoBook(bookName):
    if bookName in library.keys() and library.get(bookName) != 0:
        infoString = "Yes! {} copy/copies of {} available!".format(library.get(bookName), bookName)
        return infoString

    else:
        return "Sorry! {} is not available at the moment.".format(bookName)

@app.route("/get/<bookName>")
def getBook(bookName):
    if bookName in library.keys() and library.get(bookName) != 0:
        library[bookName] = library.get(bookName) - 1
        getString = "Yes! {} has been shared with you! {} more copy/copies available!".format(bookName, library.get(bookName))
        return getString

    else:
        return "Sorry! {} is not available at the moment.".format(bookName)