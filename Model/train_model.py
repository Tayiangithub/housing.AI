import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle
import os

# Load dataset
data = pd.read_csv("data.csv")

# Prepare features and target
X = pd.get_dummies(data[['location', 'size', 'bedrooms']])
y = data['price']

# Train model
model = LinearRegression()
model.fit(X, y)

# Save model to backend folder
model_path = os.path.join("..", "backend", "model.pkl")
with open(model_path, 'wb') as f:
    pickle.dump(model, f)

print("Model trained and saved to backend/model.pkl")
