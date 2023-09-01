# -*- coding: utf-8 -*-
"""Machine Learning Model - Regression.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IgcMzJlqLS0ng10qpgPFM4IhGBv3ZDHc

# DAILY PRODUCT QUANTITY SALES PREDICTOR

# PREPARATION

## IMPORT LIBRARIES
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from math import sqrt

"""## LOAD DATA"""

# Customer
df1 = pd.read_csv('drive/MyDrive/DATA SCIENCE PORTFOLIO/PBI - KALBE NUTRITIONALS - DATA SCIENTIST/Minggu 4 - Final Project/Customer.csv')

# Store
df2 = pd.read_csv('drive/MyDrive/DATA SCIENCE PORTFOLIO/PBI - KALBE NUTRITIONALS - DATA SCIENTIST/Minggu 4 - Final Project/Store.csv')

# Product
df3 = pd.read_csv('drive/MyDrive/DATA SCIENCE PORTFOLIO/PBI - KALBE NUTRITIONALS - DATA SCIENTIST/Minggu 4 - Final Project/Product.csv')

# Transaction
df4 = pd.read_csv('drive/MyDrive/DATA SCIENCE PORTFOLIO/PBI - KALBE NUTRITIONALS - DATA SCIENTIST/Minggu 4 - Final Project/Transaction.csv')

"""## MERGE DATA"""

# Transcation with Customer
df = df4.merge(df1, left_on='CustomerID', right_on='CustomerID')
df.head()

# Transcation with Customer
df = df.merge(df3, left_on='ProductID', right_on='ProductID')
df.head()

# Transcation with Store
df = df.merge(df2, left_on='StoreID', right_on='StoreID')
df.head()

"""## CHECK MISSING VALUES"""

df.isnull().sum()

# Fill missing values with modes
df['Marital Status'].fillna(df['Marital Status'].mode()[0], inplace=True)

"""## CHECK DUPLICATED VALUES"""

df.duplicated().sum()

"""## DROP REDUNDANT COLUMNS"""

df.head()

# Drop ID's columns because it does not have any meaning
df = df.drop(['TransactionID', 'CustomerID', 'ProductID', 'StoreID'], axis=1)

"""## ENCODING"""

df.head()

from sklearn.preprocessing import LabelEncoder

categorical_columns=['Marital Status','Product Name','StoreName','GroupStore','Type', 'Longitude','Latitude']
for col in categorical_columns:
    # make the encoder
    encoder = LabelEncoder()
    # fit the encoder with col we want to label for information good
    encoder.fit(df[col])
    # print information
    print('Column:', col)
    print('Original categories:', encoder.classes_)
    print('Encoded values:', encoder.transform(encoder.classes_))
    print('\n')
    # fit transform to apply the label
    df[col] = encoder.fit_transform(df[col])

"""## DATA TRANSFORMATION"""

df.head()

df.info()

# Change Date to datetime
df = df.astype({
    'Date':'datetime64[ns]'
})

# Change Income
df['Income'] = df['Income'].str.replace(',', '.')
df = df.astype({
    'Income':'float64'
})

"""## OUTLIERS"""

from scipy import stats

# Using z-score to find outliers and removes it
print(f'Jumlah baris sebelum memfilter outlier: {len(df)}')

filtered_entries = np.array([True] * len(df))
for col in ['Price_x', 'Qty', 'TotalAmount', 'Age', 'Gender', 'Income', 'Price_y']:
    zscore = abs(stats.zscore(df[col]))
    filtered_entries = (zscore < 3) & filtered_entries

df = df[filtered_entries]

print(f'Jumlah baris setelah memfilter outlier: {len(df)}')

"""## GROUPED BY DATA"""

df_before_grouped = df

df = df_before_grouped.groupby(['Date']).agg({'Qty': 'sum'}).reset_index()

df

"""# ARIMA TIME-SERIES REGRESSION MODEL

## PLOT TIME-SERIES DATA
"""

plt.figure(figsize=(12,5))
plt.plot(df["Date"], df["Qty"])
plt.xlabel('Date')
plt.ylabel('Qty')

"""## IDENTIFY IF THE DATA IS STATIONARY"""

from statsmodels.tsa.stattools import adfuller

def ad_test(dataset):
  dftest = adfuller(dataset, autolag='AIC')
  print("1. ADF : ", dftest[0])
  print("2. P-value: ", dftest[1])
  print("3. Num of lags : ", dftest[2])
  print("4. Num of Observations used for ADF Regression and Critical Value Calculation : ", dftest[3])
  print("5. Critical Values : ")
  for key, val in dftest[4].items():
    print("\t", key, ": ", val)

ad_test(df['Qty'])

"""## SPLIT DATA INTO TRAIN AND TEST"""

print(df.shape)
train = df.iloc[:-30]
test = df.iloc[-30:]
print(train.shape, test.shape)

"""## TRAIN THE MODEL"""

from statsmodels.tsa.arima.model import ARIMA

model = ARIMA(train['Qty'], order=(40,1,1))
model = model.fit()
model.summary()

# Make prediction on test set
start = len(train)
end = len(train) + len(test) - 1
pred = model.predict(start=start, end=end, typ='levels')

# Evaluate model performance with mse
from sklearn.metrics import mean_squared_error
from math import sqrt
mse = sqrt(mean_squared_error(pred, test['Qty']))
print("MSE: ", round(mse, 3))

pred.plot(legend=True)
test['Qty'].plot(legend=True)

"""## RETRAIN MODEL WITH ALL DATA"""

model2 = ARIMA(df['Qty'], order=(40, 1, 1))
model2 = model2.fit()
df.tail()

"""## TEST MODEL FOR FUTURE DATES"""

# Predict daily
index_future_dates = pd.date_range(start='2023-01-01', end='2023-01-01')
pred_daily = model2.predict(start=len(df), end=len(df), typ='levels').rename('ARIMA Predictions')
pred_daily.index = index_future_dates

# Predict monthly
index_future_dates = pd.date_range(start='2023-01-01', end='2023-01-31')
pred_monthly = model2.predict(start=len(df), end=len(df)+30, typ='levels').rename('ARIMA Predictions')
pred_monthly.index = index_future_dates

# Round to int for daily prediction
pred_daily[0] = round(pred_daily[0])
print(pred_daily.index[0], " Qty: ", pred_daily.values[0])

# Round to int for monthly prediction
i = 0
for x in pred:
  pred_monthly[i] = round(x)
  i += 1

pred_df = {'Date': pred_monthly.index, 'Qty': pred_monthly.values}
pred_df = pd.DataFrame(pred_df)

final_df = pd.concat([df, pred_df])
plt.figure(figsize=(12,5))
plt.plot(pred_df['Date'], pred_df['Qty'])