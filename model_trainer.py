import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import pickle

# Generate metabolic data for training
np.random.seed(42)
data = {
    'age': np.random.randint(15, 80, 5000),
    'weight': np.random.randint(40, 150, 5000),
    'height': np.random.randint(140, 200, 5000),
    'gender': np.random.randint(0, 2, 5000), # 0: Female, 1: Male
    'activity': np.random.randint(1, 6, 5000)
}
df = pd.DataFrame(data)
df['target'] = (10 * df['weight']) + (6.25 * df['height']) - (5 * df['age']) + (df['gender'] * 5) + (df['activity'] * 250)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(df.drop('target', axis=1), df['target'])

with open('wellness_model.pkl', 'wb') as f:
    pickle.dump(model, f)
print("✅ ML Model wellness_model.pkl created!")