import pandas as pd
pd.set_option('future.no_silent_downcasting', True)

def clean_data_history(data: pd.DataFrame)-> pd.DataFrame:
    data['RSI_14'] =  data['RSI_14'].fillna(0)
    return data


def clean_data_quarterly(data:pd.DataFrame)-> pd.DataFrame:
    data = data.loc[:,data.notna().sum() >=30]
    data = data.T.fillna(data.median(axis=1)).T.infer_objects(copy=False)

    return data

