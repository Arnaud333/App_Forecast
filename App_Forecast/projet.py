import os
import pandas as pd
import streamlit as st
import datetime
path='Data'
def Select_Project():

# Utilisez os.listdir() pour obtenir la liste de tous les éléments dans le répertoire
    elements = os.listdir(path)
# Utilisez une boucle for pour parcourir tous les éléments et filtrer seulement les répertoires
    dossiers = []
    for element in elements:
        if os.path.isdir(os.path.join(path, element)):
            dossiers.append(element)
    return dossiers

# La liste 'dossiers' contient maintenant tous les noms des répertoires dans le répertoire spécifié
#print(dossiers)
class Project:
    def __init__(self):
        self.name = ''
        self.path=''
        self.df=pd.DataFrame({})
        self.df_base=pd.DataFrame({})
        self.dfg=pd.DataFrame({})
        
        self.dic_col_df={'Col_Date':[''],
                    'Col_Value':[''],
                    'Col_Ref':['']}
        self.dic_col_base={'Col_Base_Art':[''],
                    'Col_Base_Des':[''],
                    'Col_Base_Family':['']}
        self.dic_col_corr={'Col_Corr_Date':[''],
                    'Col_Corr_Value':[''],
                    'Col_Corr_ref':['']}
        
        
    def get_name(self,nom):
        self.name = nom
        if nom not in Select_Project():
            os.makedirs(os.path.join(path, nom))
        self.path = os.path.join(path, nom)
       
    
    def check_file(self,file_name):
        path_data=os.path.join(path, self.name)
        elements = os.listdir(path_data)
        file_exist=False
        for element in elements:
            if element==file_name:
                file_exist=True
        return file_exist
    
    def get_file(self,file_name):
        path_data=os.path.join(path, self.name)
        elements = os.listdir(path_data)
        for element in elements:
            if element==file_name:
               return os.path.join(path_data,element)
        

    def create_conf_file(self):
        if self.check_file('config.csv')==False:
            path_data=os.path.join(path, self.name)
            data = {'Col_Date':['Date'],
                    'Col_Value':['Value'],
                    'Col_Ref':['Article'],
                    'Col_Base_Art':[''],
                    'Col_Base_Des':[''],
                    'Col_Base_Family':['']}
            df= pd.DataFrame(data,columns=['Col_Date','Col_Value', 'Col_Ref','Col_Base_Art','Col_Base_Des','Col_Base_Family'])
            df.to_csv(os.path.join(path_data, 'config.csv'), index=False)
    
    def get_config(self):
        path_data=os.path.join(path, self.name)
        if self.check_file('config.csv')==True:
            df=pd.read_csv(os.path.join(path_data,'config.csv'))
            dico=df.iloc[0].to_dict()
            return dico
        else:
            return False
        
    def update_config(self,dico):
        path_data=os.path.join(path, self.name)
        if self.check_file('config.csv')==True:
            df=pd.read_csv(os.path.join(path_data,'config.csv'))
            for elt in dico:
                df.at[0,elt]=dico[elt]
            df.to_csv(os.path.join(path_data,'config.csv'),index=False)
        else:
            self.create_conf_file()
            self.update_config(dico)

    def save_file(self,file,filename):
        path_data=os.path.join(path, self.name)
        df=pd.read_csv(file)
        df.to_csv(os.path.join(path_data,filename),index=False)
        # with open(path_data, 'w') as f:
        #     f.write(file)
    
    def calcul_famille(self, nb_periode):
        df_data=self.df
        df_base = self.df_base
        dico=self.get_config()
        df_base[dico['Col_Ref']]=df_base[dico['Col_Base_Art']]
        df_base.drop(dico['Col_Base_Art'],axis=1)
        df3=pd.merge(df_data, df_base,  on=dico['Col_Ref'])        
        df3[dico['Col_Base_Family']]=df3[dico['Col_Base_Family']].fillna(df3[dico['Col_Ref']])
        dfg=pd.DataFrame(df3.groupby([dico['Col_Base_Family'],'ds']).sum())
        dfg=dfg.reset_index()
        self.df=df3        
        date_max=datetime.date.today()
        date_min=date_max-datetime.timedelta(days=nb_periode)
        date_min= pd.to_datetime(date_min)
        date_max= pd.to_datetime(date_max)
        #création d'un filtre sur la periode désirée pour le calcul des poids des articles par famille
        mask=(df3['ds']>=date_min) & (df3['ds']<=date_max)
        st.write('date min et max',date_min, date_max)
        st.write('DF',df3)
        df3_periode=df3.loc[mask]
        st.write('DF3periode',df3_periode)
        #calcul du poids des articles par famille sur la periode
        df3_periode['Poids']=df3_periode.groupby([dico['Col_Ref']])[dico['Col_Value']].transform('sum')/df3_periode.groupby([dico['Col_Base_Family']])[dico['Col_Value']].transform('sum')
        df3_periode=df3_periode[[dico['Col_Ref'],dico['Col_Base_Family'],'Poids']]
        df3_periode=df3_periode.drop_duplicates()
        #calcul du nombre de ref par famille pour la répartion dans le cas ou il n'y a pas d'historique de la famille sur la periode
        df_base['nb_art_fam']=df_base.groupby(dico['Col_Base_Family'])[dico['Col_Ref']].transform('count')
        #rajout des poids dans la base_article
        df_base=pd.merge(df_base,df3_periode[['Poids',dico['Col_Ref']]],on= dico['Col_Ref'],how='left')
        st.write('dfbase1',df_base)
        #traitement des valeurs erreurs sur les poids, on remplace d'abord les erreurs (dues à l'absence d'historique sur la periode) par 1/nombre de ref par famille, 
        #puis si il reste des cas on remplace par 1 (car cela signifie qu'il n'y a pas de famillle rattachée)
        df_base['Poids']=df_base['Poids'].fillna(1/df_base['nb_art_fam'])
        df_base['Poids']=df_base['Poids'].fillna(1)
        self.dfg=dfg
        self.df_base =df_base

    def get_fam_art(self,ref):
        dfbase=self.df_base
        col=self.get_config()['Col_Base_Family']
        sous_df=dfbase.loc[dfbase[col]==ref]        
        col=self.get_config()['Col_Base_Art']
       
        if sous_df.empty==False:
            fam_art=sous_df[[col,'Poids']]
            # calcul des poids
        else:
            fam_art=False   
        return fam_art

