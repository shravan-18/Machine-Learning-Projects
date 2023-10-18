# -*- coding: utf-8 -*-
"""car-price-prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GFv7_C3Se29_riggx8K_UUH732_GMWpY

# **Car Price Predictions**

## **Install and Import Libraries**
"""

!pip install pandas-profiling

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pandas_profiling import ProfileReport

"""## **Exploratory Data Analysis**"""

# Load the data

df = pd.read_csv("/kaggle/input/used-car-price-predictions/true_car_listings.csv")

# Use pandas profiling for EDA

profile = ProfileReport(df, title='Dataset Report', explorative=True)
profile.to_notebook_iframe()

"""### **Inferences from the report**
* ### No Missing Values
* ### 3 Numeric and 5 Categorical columns
* ### "Vin" column - High Cardinality
* ### Reasonably high Inverted correlation between Year and Mileage
* ### "State" column - 59 distinct values - can One Hot encode
* ### "Make" column - 58 distinct values - can One Hot encode
* ### "Model" column - 2300+ distinct values - better to drop than One Hot encode
* ### "City" column - 2300+ distinct values - better to drop than One Hot encode
"""

# Remove Duplicate rows
df = df.drop_duplicates()

# Check the head of the data
df.head()

# Check datatypes of each column
for col in df.columns:
    print(f"{col}: {df[col].dtypes}")

df[df.drop(['Vin', 'Model', 'City'], axis=1).select_dtypes('object').columns]

"""## **Create Pipeline and Transformer for Data Preprocessing**"""

# Create Classes for Pipelining and create Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline

# Class for dropping Unnecessary and Unusable columns
class dropCols(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X.drop(['Vin', 'Model', 'City'], axis=1)

categorical_cols = list(df.select_dtypes('object').columns)
categorical_cols.append("Year")

numeric_cols = list(df.drop('Price', axis=1).select_dtypes(exclude='object').columns)
numeric_cols.remove("Year")

categorical_pipeline = Pipeline([("Drop_Columns", dropCols()),
                                 ("OneHot", OneHotEncoder())])
numeric_pipeline = Pipeline([("Scaler", StandardScaler())])

# Create Column Transformer
from sklearn.compose import ColumnTransformer

transformer = ColumnTransformer([('numeric_preprocessing', numeric_pipeline, numeric_cols),
                          ('categorical_preprocessing', categorical_pipeline, categorical_cols)])

"""## **Try Pycaret first**"""

!pip install pycaret

from pycaret.regression import *
clf = setup(df, target='Price')
best = compare_models()

"""## **Create Machine Learning Pipeline**"""

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor

# Define regression models
models = {
    'Linear Regression': LinearRegression(),
    'Ridge': Ridge(),
    'Lasso': Lasso(),
    'Elastic Net': ElasticNet(),
    'XG Boost Regressor': XGBRegressor(objective='reg:squarederror', n_estimators=200),
    'Gradient Boosting': GradientBoostingRegressor()
}

# Create a dictionary to store model performance results
results = {}

# Split DataFrame into X (features) and y (target)
X = df.drop('Price', axis=1)  # Replace 'target_column_name' with your target column name
y = df['Price']

# Split your data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a Scikit-Learn pipeline for data preprocessing and modeling
for model_name, model in models.items():
    pipeline = Pipeline([
        ('preprocessor', transformer),
        ('model', model)
    ])

    # Fit the pipeline on the training data
    pipeline.fit(X_train, y_train)

    # Predict on the test data
    y_pred = pipeline.predict(X_test)

    # Evaluate the model's performance (you can choose different metrics)
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    results[model_name] = [mse, mae, r2]

# Print the model performance results
for model_name, metrics in results.items():
    print(f'''{model_name}: Mean Squared Error = {metrics[0]}
                            Mean Absolute Error = {metrics[1]}
                            R2 Score = {metrics[2]}\n''')

