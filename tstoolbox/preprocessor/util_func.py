import numpy as np
import pandas as pd
import datetime as dt
from sklearn.preprocessing import MinMaxScaler

def window_sliding(X, y, idxs, window):

  """time series window sliding
  
  Parameters
  ----------
  X : (n, f) array of time series (predictor)
  y : (n, 1) array of time series (target variables) or None
  idxs : list, 1d array
    start to finish index
  window : int 
    lookback window
  """
  X_windows = []
  if y is not None:
      y_windows = []

  for i in idxs:
    X_t = X[i-window:i].copy()
    if y is not None:
      y_t = y[i].copy()
    X_windows.append(X_t)
    if y is not None:
      y_windows.append(y_t)
  
  X_windows = np.array(X_windows)
  if y is not None:
      y_windows = np.array(y_windows) 
  return X_windows, y_windows


def windowlized(df, cols, val_date, test_date, window, 
  target_col='target', target_date_col='target_date', return_df=False):

  """time window sliding for dataframe with train val test split
  
  Params
  ------
  df : dataframe
  cols : list 
    predictors
  val_date : datetime
  test_date : datetime
  window : int 
    window size
  target_col : str, optional
    target variable column
  target_date_col : str, optional
    datetime corresponding with target variable column
  return_df : bool, optional
    return df of train val test
  """
  
  valid_date = df[df[target_col].isna() == False][target_date_col].min() - dt.timedelta(window)
  df_valid = pd.DataFrame(df[df[target_date_col] >= valid_date]).reset_index(drop=True)
  valid_target_date = df[df[target_col].isna() == False][target_date_col].max()
  df_valid = pd.DataFrame(df_valid[df_valid[target_date_col] <= valid_target_date]).reset_index(drop=True)

  X_org = df[cols].values
  scaler_X = MinMaxScaler()
  scaler_X.fit(X_org)

  y_org = df[[target_col]].values
  scaler_y = MinMaxScaler()
  scaler_y.fit(y_org)

  train_date = val_date - dt.timedelta(7*12)

  X_valid, y_valid = df_valid[cols].values, df_valid[[target_col]]
  X_valid = scaler_X.transform(X_valid)
  y_valid = scaler_y.transform(y_valid)

  train_idx = df_valid[df_valid[target_date_col] <= train_date].dropna().index.tolist()
  val_idx = df_valid[(df_valid[target_date_col] >= val_date)&(df_valid[target_date_col] < test_date)].index.tolist() 
  test_idx = df_valid[df_valid[target_date_col] >= test_date].index.tolist() 

  X_train, y_train = window_sliding(X_valid, y_valid, train_idx, window)
  X_val, y_val = window_sliding(X_valid, y_valid, val_idx, window)
  X_test, y_test = window_sliding(X_valid, y_valid, test_idx, window)

  if return_df == True:
    df_train = df_valid[df_valid.index.isin(train_idx)].reset_index(drop=True)
    df_val = df_valid[df_valid.index.isin(val_idx)].reset_index(drop=True)
    df_test = df_valid[df_valid.index.isin(test_idx)].reset_index(drop=True)

    return ((X_train, y_train), (X_val, y_val), (X_test, y_test), (scaler_X, scaler_y)), (df_train, df_val, df_test)
  else:
    return (X_train, y_train), (X_val, y_val), (X_test, y_test), (scaler_X, scaler_y)


  