
import os
import pandas as pd
from prophet import Prophet
path='Data'


class Model_P:
    def __init__(self, df,val_col,ref_col):
        self.df_model=df
        self.mod_ref={}
        self.futur_ref={}
        drop_list=[]
        self.m={}
        
        for elt in df.columns.values:        
            if elt not in ['ds',val_col]:
                drop_list.append(elt)

        for art in df[ref_col].unique().tolist():
            
            df_ref=df.loc[df[ref_col]==art]       
            df_ref.drop(drop_list, axis = 1, inplace=True)
            df_ref.columns=['ds','y']    
            #completer le dictionnaire des forecast
            self.m[art]=Prophet(interval_width=0.95, daily_seasonality=True)
            self.mod_ref[art]=self.m[art].fit(df_ref)
            future=self.m[art].make_future_dataframe(periods=100,freq='D')
            self.futur_ref[art] = self.m[art].predict(future)    
            
    