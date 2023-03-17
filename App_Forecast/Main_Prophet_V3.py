# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 10:29:49 2023

@author: arnau
"""
#C:\Users\arnau\Projet_python\envproph\Scripts\activate
#streamlit run C:\Users\arnau\Projet_python\Prophet\Main_Prophet.py
#streamlit run Main_Prophet.py
#Dependancies
import pandas as pd
from prophet import Prophet
import streamlit as st
from PIL import Image
import os as os
from projet import Select_Project 
from projet import Project
from model import Model_P as mp

st.set_page_config(page_title="Prévisions avec Prophet", layout="wide")
liste_file=['dataset.csv','base_article.csv','config.csv','correction_records.csv','forecast.csv']
projet=Project()
debug=False

if 'Compteur' not in st.session_state:
    st.session_state.Compteur=0
if 'Projet' not in st.session_state:
    st.session_state.Projet=projet
if 'test' not in st.session_state:
    st.session_state.test=0
if 'av' not in st.session_state:
    st.session_state.av =0
if 'dico' not in st.session_state:
    st.session_state.dico ={}
if 'reload_data' not in st.session_state:
    st.session_state.reload_data ={}
    for elt in liste_file:
        st.session_state.reload_data[elt]=0
if 'Data_Load' not in st.session_state:
    st.session_state.Data_Load = {}
    for elt in liste_file:
        st.session_state.Data_Load[elt]=0
if 'Data_Load_base_ref' not in st.session_state:
    st.session_state.Data_Load_base_ref = 0

if debug:
    st.write(f'tesst {st.session_state.test}')
    st.write(f'av {st.session_state.av}')


img=Image.open('logo.png')
st.sidebar.image(img)


def set_av(i):
    st.session_state.av=i    
    st.write('test3',st.session_state.av)

def file_load_status(i):
    if 'uploader'+str(i) in st.session_state:
        st.session_state.Data_Load=2
def file_load_status2():
    if 'uploader2' in st.session_state:
        st.session_state.Data_Load=2

def choix_du_projet():
    if st.session_state.av==0:
        proj_def=st.container()
        with proj_def:
            st.header('Sur quel projet allons nous travailler?')
            c1,c2 = st.columns([4,4])
            with c1:        
                choix1 = st.selectbox("Sélectionnez une projet", Select_Project(),key='choix1')
                B1=False
                B1=st.button('Selectionner le projet')
                if B1 ==True:
                    # st.write(st.session_state.choix1)
                    projet.get_name(st.session_state.choix1)
                    st.session_state.Projet=projet
            with c2:  
                choix2 = st.text_input("Ou créez un nouveau projet ",key='choix2')  
                B2=False
                B2=st.button('Créer le projet')
                if B2 ==True:
                    # st.write(st.session_state.choix2)
                    projet.get_name(st.session_state.choix2)
                    st.session_state.Projet=projet                
            if B1==True or B2==True:   
                st.session_state.Projet_selected=True 
                st.write('Projet choisi:', str(projet.name) )
                st.session_state.Projet=projet 
                st.session_state.av=1 
                st.experimental_rerun()      

def choix_des_sources(projet,file):
    # st.write(f'le fichier est {file}')
    fichier={}
    valider_df={}
    choix={}
    reload_data={}
    if projet.check_file(file)==False:
        fichier[file]=st.file_uploader('charger un fichier',on_change=file_load_status(st.session_state.Compteur),key='uploader'+file)
        valider_df[file]=st.button("Valider le nouveaux fichier, attention cela écrasera l'ancien", key='valider_df'+file)
        if valider_df[file]:
            projet.save_file(fichier[file],file)            
            st.session_state.Projet=projet
            st.session_state.Data_Load[file]=2
        st.session_state.Compteur+=1
    else:
        st.session_state.Data_Load[file]=0
        
        choix[file]=st.selectbox("FIchier déjà enregistré, voulez recharger un nouveau fichier",['Non','Oui'],index= st.session_state.reload_data[file],key='reload_data'+file)
        if choix[file]=='Oui': 
            
            st.session_state.reload_data[file]=1   
            st.write(f'test1 {st.session_state.reload_data[file]}')            
            fichier[file]=st.file_uploader('charger un fichier',on_change=file_load_status(st.session_state.Compteur),key='uploader'+file)            
            file_tampon=fichier[file]          
        
            valider_df[file]=st.button("Valider le nouveaux fichier, attention cela écrasera l'ancien",key='valider_df'+file)
            if valider_df[file]:
                projet.save_file(file_tampon,file)
                fichier[file]=projet.get_file(file)                
                st.session_state.Projet=projet
                st.session_state.Data_Load[file]=2
        else:
            st.session_state.reload_data[file]=0   
            fichier[file]=projet.get_file(file)            
            st.session_state.Projet=projet
            st.session_state.Data_Load[file]=2
        st.session_state.Compteur+=1
    
def choix_colonnes(dico_col,df,projet):
    col_list=df.columns.tolist()
    save_config={}
    if projet.check_file('config.csv')==True:
        val_def=True
    else:
        val_def=False
    for elt in dico_col:
        cle=str(elt)+'key'
        if val_def:
            default_value=col_list.index(projet.get_config()[elt])
            st.selectbox(f'Selectionner la colonne {elt}',col_list,index=default_value,key=cle)
        else:
            st.selectbox(f'Selectionner la colonne {elt}',col_list,key=cle)

    save_config[st.session_state.Compteur]=st.button('Enregister le nom des colonnes',key='save_config'+str(st.session_state.Compteur))    
      
    if save_config[st.session_state.Compteur]:
        for elt in dico_col:
            dico_col[elt]=st.session_state[str(elt)+'key']
        projet.update_config(dico_col)
    st.session_state.Compteur+=1
def nettoyage_col(dico_col,dico_trad,df):
    keeplist=[]
    droplist=[]
    for elt in dico_col:
        keeplist.append(dico_trad[elt])
    for elt in df.columns.values:
         if elt not in keeplist:
            droplist.append(elt)
    df.drop(droplist, axis = 1, inplace=True)
    return df

def Description_donnees():
    projet=st.session_state.Projet
    dico=projet.get_config() 
    data_description=st.container()
    df=projet.df
    
# "nettoyage des colonnes"
    df=nettoyage_col(projet.dic_col_df,projet.get_config(),df)
    st.write('test',df.head())
    with data_description:
        st.header('Description des données du projet ',projet.name)
        col_desc,col_head,col_details = st.columns([5,7,2])
        # df[dico['Col_Date']]=pd.to_datetime(df[dico['Col_Date']], format='%d?%m%Y')

        df['Year']=df[dico['Col_Date']].apply(lambda x: str(x)[-4:])
        df['Month']=df[dico['Col_Date']].apply(lambda x: str(x)[-6:-4])
        df['Day']=df[dico['Col_Date']].apply(lambda x: str(x)[:-6])
        df['ds']=pd.DatetimeIndex(df['Year']+'-'+df['Month']+'-'+df['Day'])

        with col_desc:
            st.subheader('Description des données historiques ')
            st.write('date mini :',str(df['ds'].min())[:10])
            st.write('date maxi :',str(df['ds'].max())[:10])
            st.write('Nombre de références articles :',str(df[dico['Col_Ref']].nunique()))

        with col_head:
            st.subheader('Aperçu des premieres lignes ')
            st.write(df.head(5))
        projet.df=df
        projet.df_base=nettoyage_col(projet.dic_col_base,projet.get_config(),projet.df_base)
        projet.calcul_famille(3650)
        st.session_state.Projet=projet
        st.write('df_base',projet.df_base)

        # df_base[dico['Col_Ref']]=df_base[dico['Col_Base_Art']]
        # df_base.drop(dico['Col_Base_Art'],axis=1)
        # df3=pd.merge(df_data, df_base,  on=dico['Col_Ref'])
        # st.write(df3)
        # df3[dico['Col_Base_Family']]=df3[dico['Col_Base_Family']].fillna(df3[dico['Col_Ref']])
        # dfg=pd.DataFrame(df3.groupby([dico['Col_Base_Family'],'ds']).sum())
        # dfg=dfg.reset_index()
        # st.session_state.Projet.df=df3
        # st.session_state.Projet.dfg=dfg
        # st.write('Data regroupée',dfg.head(10))
    

def Lancer_model():
    forecast=st.container()
    projet=st.session_state.Projet
    dico=projet.get_config()     
    dfg=projet.dfg
    with forecast:
        st.header('Prevision selon le model Prophet pour le projet ',projet.name)
        ref_list=dfg[dico['Col_Base_Family']].unique().tolist()
        col_mod, col_param = st.columns([5,2])
        with col_mod:     
            ref=st.selectbox("Selectionner la référence",ref_list,key='selected_ref')
            Prev=mp(dfg,dico['Col_Value'],dico['Col_Base_Family'])
            st.write(f"Voici le model pour l'article {ref}",Prev.m[st.session_state.selected_ref].plot(Prev.futur_ref[st.session_state.selected_ref]))
            st.write(dfg.head())
        with col_param:
            st.write(f"Parametres de l'article {ref}")
            fam_ref=projet.get_fam_art(ref)            
            st.write(f"Famille {ref} contient les articles suivants",fam_ref)           
            


##### MAIN ######

if st.session_state.av==0:
    choix_du_projet()

if st.session_state.av==1:
    projet = st.session_state.Projet
    st.title(f'Configuration des données du projet: {projet.name}')
    col_dataset,col_base_ref,col_outliers,col_hist_forecast=st.columns([5,5,5,5])
    fichier={}
    with col_dataset:
        choix_des_sources(projet,str('dataset.csv'))
        if st.session_state.Projet.check_file('dataset.csv'):
            st.session_state.Projet.df=pd.read_csv(st.session_state.Projet.get_file('dataset.csv'))
            if st.session_state.Data_Load['dataset.csv']==2:
                projet= st.session_state.Projet                   
                choix_colonnes(projet.dic_col_df,projet.df,projet)
            
    
    with col_base_ref:
        choix_des_sources(projet,str('base_article.csv'))
        if st.session_state.Projet.check_file('base_article.csv'):
            st.session_state.Projet.df_base=pd.read_csv(st.session_state.Projet.get_file('base_article.csv'))   
            if st.session_state.Data_Load['base_article.csv']==2:
                projet= st.session_state.Projet                   
                choix_colonnes(projet.dic_col_base,projet.df_base,projet)

        #   Navigation sur la sidebar
    with st.sidebar:
        go_av0=st.button('Revenir au choix du projet')
        if go_av0:
            st.session_state.av=0
            st.experimental_rerun()
        if st.session_state.Projet.df.empty==False:
            go_av2=st.button('Valider la configuration des données')
            if go_av2:
                st.session_state.av=2
                st.experimental_rerun()
        else:
            st.write('En attente de la configuration des données')
 
if st.session_state.av==2:  
    Description_donnees()
            #   Navigation sur la sidebar
    with st.sidebar:
        go_av0=st.button('Revenir au choix du projet')
        if go_av0:
            st.session_state.av=0
            st.experimental_rerun()
        go_av1=st.button('Revenir à la configuration des données')
        if go_av1:
            st.session_state.av=1
            st.experimental_rerun()    
        go_av3=st.button('Lancer le model')
        if go_av3:
            st.session_state.av=3
            st.experimental_rerun()
 
if st.session_state.av==3:
    Lancer_model()
                #   Navigation sur la sidebar
    with st.sidebar:
        st.subheader('Navigation')
        go_av0=st.button('Revenir au choix du projet')
        if go_av0:
            st.session_state.av=0
            st.experimental_rerun()
        go_av1=st.button('Revenir à la configuration des données')
        if go_av1:
            st.session_state.av=1
            st.experimental_rerun()    
        go_av2=st.button('Revenir à la description des données')
        if go_av2:
            st.session_state.av=2
            st.experimental_rerun()
        st.subheader('')
        st.subheader('Parametres du model article')
    



                