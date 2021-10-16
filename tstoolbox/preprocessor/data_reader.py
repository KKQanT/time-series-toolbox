import pandas as pd
import glob

def get_yahoos(mainpath, folder_name):

  paths = glob.glob(f'{mainpath}/{folder_name}/*')
  df = pd.DataFrame()
  cols = []

  #print(paths)

  for path in paths:
    #print(path)
    df_ = pd.read_csv(path)
    df_ = df_.rename(columns = {'Date':'date'})
    df_ = pd.DataFrame(df_[['date', 'Close']])
    col_name = path[path.find(f'{folder_name}/') + len(f'{folder_name}/'):path.find('.csv')]
    cols.append(col_name)
    df_ = df_.rename(columns = {'Close':col_name})
    df_['date'] = pd.to_datetime(df_['date'])

    if len(df) == 0:
      df = df_.copy()
    else:
      df = pd.merge(df, df_, on = ['date'], how='left')

  df['date'] = pd.to_datetime(df['date'])

  df = df.dropna().reset_index(drop=True)
  cols = df.columns.tolist()[1:]

  df_filled = pd.DataFrame()

  df_filled['date'] = pd.date_range(df['date'].min(), df['date'].max())
  df_filled = pd.merge(df_filled, df, on=['date'], how='left')

  for col in cols:
    df_filled[col] = df_filled[col].fillna(method = 'ffill')
  
  return df_filled, cols

def get_investing(main_path, folder_name):
  names = [s[s.find(f'{folder_name}/') + len(f'{folder_name}/'):s.find('.csv')] for s in glob.glob(f'{main_path}/{folder_name}/*')]
  for i, name_ in enumerate(names):
    mainpath = f'{main_path}/{folder_name}/'
    path = mainpath + name_ + '.csv'
    df_invest = pd.read_csv(path)
    #print(name_)

    df_invest['date'] = pd.to_datetime(df_invest['วันเดือนปี'])
    #print(df_invest['date'].max())
    df_invest = df_invest.rename(columns = {'ราคาเปิด':name_})
    df_invest = df_invest[['date', name_]]
    df_invest_filled = pd.DataFrame()
    df_invest_filled['date'] = pd.date_range(df_invest['date'].min(), df_invest['date'].max())
    df_invest_filled = pd.merge(df_invest_filled, df_invest, on = ['date'], how='left')
    df_invest_filled[name_] = df_invest_filled[name_].fillna(method='ffill')

    if i == 0:
      df_invest_filled_main = df_invest_filled.copy()
    else:
      df_invest_filled_main = pd.merge(df_invest_filled_main, df_invest_filled, how='left', on = ['date'])

  return df_invest_filled_main, names