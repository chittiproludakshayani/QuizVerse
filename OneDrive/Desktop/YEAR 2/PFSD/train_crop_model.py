import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from joblib import dump

# Load feedback data
df = pd.read_csv('feedback.csv')

# Features and target
X = df[['soil', 'weather', 'region']]
y = df['crop']

# Encode categorical variables
le_soil = LabelEncoder()
le_weather = LabelEncoder()
le_region = LabelEncoder()
le_crop = LabelEncoder()

X['soil_enc'] = le_soil.fit_transform(X['soil'])
X['weather_enc'] = le_weather.fit_transform(X['weather'])
X['region_enc'] = le_region.fit_transform(X['region'])

X_enc = X[['soil_enc', 'weather_enc', 'region_enc']]
y_enc = le_crop.fit_transform(y)

# Train model
clf = DecisionTreeClassifier()
clf.fit(X_enc, y_enc)

# Save model and encoders
dump(clf, 'crop_model.joblib')
dump(le_soil, 'le_soil.joblib')
dump(le_weather, 'le_weather.joblib')
dump(le_region, 'le_region.joblib')
dump(le_crop, 'le_crop.joblib')

print('Model and encoders saved.')
