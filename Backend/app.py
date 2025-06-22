from flask import Flask, request, jsonify, session, redirect, render_template, flash
from flask import flash, redirect, render_template, request, session
import pickle
import pandas as pd
import os
from auth import verify_user, init_db
from flask_cors import CORS
from sklearn.linear_model import LinearRegression
import sqlite3
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = 'secret-key'
CORS(app)
init_db()


MODEL_PATH = 'model.pkl'
model = pickle.load(open(MODEL_PATH, 'rb'))

data_path = os.path.join("..", "model", "data.csv")

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = verify_user(username, password)
        if role:
            session['username'] = username
            session['role'] = role
            flash(f"Welcome back, {username}!", "success")
            return redirect(f'/{role}')
        flash("❌ Invalid username or password", "error")
    return render_template('home.html')

from flask import flash, redirect, render_template, request, session

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        second_name = request.form['second_name']
        username = request.form['username']
        password = request.form['password']

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Connect to DB
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Check if username already exists
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        if c.fetchone():
            flash('⚠️ Username already exists. Choose another one.', 'error')
            conn.close()
            return redirect('/register')

        # Otherwise, insert new user
        c.execute('INSERT INTO users (first_name, second_name, username, password, role) VALUES (?, ?, ?, ?, ?)',
                  (first_name, second_name, username, hashed_password, 'user'))
        conn.commit()
        conn.close()

        flash('✅ Registration successful! Please log in.', 'success')
        return redirect('/')  # back to login page

    return render_template('register.html')

@app.route('/user')
def user_dashboard():
    if session.get('role') != 'user':
        return redirect('/')
    return render_template('user.html')


@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/')
    return render_template('admin.html')


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()  # e.g. {"location":"Nairobi", "size":2000, "bedrooms":3}
    df = pd.get_dummies(pd.DataFrame([data]))

    # Ensure input columns match training model's
    model_input = pd.DataFrame(columns=model.feature_names_in_)
    df = pd.concat([model_input, df], axis=0).fillna(0).infer_objects(copy=False)


    prediction = model.predict(df)[0]
    return jsonify({'price': prediction})


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file uploaded"
    file = request.files['file']
    file.save(data_path)
    return "Dataset uploaded successfully. You can now retrain the model."


@app.route('/retrain', methods=['POST'])
def retrain():
    try:
        data = pd.read_csv(data_path)
        X = pd.get_dummies(data[['location', 'size', 'bedrooms']])
        y = data['price']
        new_model = LinearRegression()
        new_model.fit(X, y)
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(new_model, f)
        global model
        model = new_model
        return "Model retrained successfully."
    except Exception as e:
        return f"Error retraining model: {str(e)}"

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



if __name__ == '__main__':
    app.run(debug=True)
