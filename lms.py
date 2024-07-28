from flask import Flask, request, render_template, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)

BOOKS_FILE = 'books.json'

def load_data():
    if not os.path.exists(BOOKS_FILE):
        with open(BOOKS_FILE, 'w') as f:
            json.dump({"books": [], "borrowed_books": {}}, f)

    with open(BOOKS_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(BOOKS_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', books=data["books"], borrowed_books=data["borrowed_books"])

@app.route('/add_book', methods=['POST'])
def add_book():
    data = load_data()
    isbn = request.form['isbn']
    title = request.form['title']
    author = request.form['author']
    quantity = int(request.form['quantity'])

    if quantity < 1:
        return "Quantity must be 1 or more", 400

    new_book = {"ISBN": isbn, "Title": title, "Author": author, "Quantity": quantity}
    if new_book not in data["books"]:
        data["books"].append(new_book)
        save_data(data)

    return redirect(url_for('index'))

@app.route('/remove_book', methods=['POST'])
def remove_book():
    data = load_data()
    isbn = request.form['isbn']
    data["books"] = [book for book in data["books"] if book["ISBN"] != isbn]
    save_data(data)
    return redirect(url_for('index'))

@app.route('/search_book', methods=['GET'])
def search_book():
    data = load_data()
    search_query = request.args.get('query')
    results = [book for book in data["books"] if search_query.lower() in book["Title"].lower()]
    return jsonify(results)

@app.route('/borrow_book', methods=['POST'])
def borrow_book():
    data = load_data()
    isbn = request.form['isbn']
    user_id = request.form['user_id']

    for book in data["books"]:
        if book["ISBN"] == isbn and book["Quantity"] > 0:
            data["borrowed_books"][isbn] = {"Title": book["Title"], "UserID": user_id}
            book["Quantity"] -= 1
            save_data(data)
            break
    else:
        return "Book not available for borrowing or does not exist", 400

    return redirect(url_for('index'))

@app.route('/return_book', methods=['POST'])
def return_book():
    data = load_data()
    isbn = request.form['isbn']
    user_id = request.form['user_id']

    if isbn in data["borrowed_books"] and data["borrowed_books"][isbn]["UserID"] == user_id:
        for book in data["books"]:
            if book["ISBN"] == isbn:
                book["Quantity"] += 1
                break
        del data["borrowed_books"][isbn]
        save_data(data)
    else:
        return "Book with given ISBN and UserID combination not borrowed", 400

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)