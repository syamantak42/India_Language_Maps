import pandas as pd
import numpy as np

#Calculates % for each language and language group
def find_perc(df):
    
    df_tot_pop = df[["AreaName", "Total", "Rural", "Urban"]].groupby(["AreaName"]).agg("sum").reset_index()    
    df_tot_pop.columns = ["AreaName", "Agg_Total", "Agg_Rural", "Agg_Urban"]
    #display(df_tot_pop)
    df = df.merge(df_tot_pop, on = "AreaName", how = "outer") 
    
    df_langGroup = df[[ "AreaName","LangGroup", "Total", "Rural", "Urban"]]\
    .groupby(["AreaName", "LangGroup"]).agg("sum").reset_index()
    
    df_langGroup.columns = ["AreaName", "LangGroup", "GroupAgg_Total", "GroupAgg_Rural", "GroupAgg_Urban"]
    df = df.merge(df_langGroup,  on = ["AreaName", "LangGroup"], how = "outer") 
    
    #display(df.head())
    
    for pop_col in ["Total", "Rural", "Urban"]:
        df["LangName_" + pop_col +"_%"] = 100*df[pop_col]/df["Agg_"+pop_col]
        df["LangGroup_" + pop_col +"_%"] = 100*df["GroupAgg_" + pop_col]/df["Agg_"+pop_col]
        
    df = df.fillna(0)
    return df      

#filters % of speakers of a language group or dialect at the state or district level
def filter_perc_lang(df, lang_col, lang_name, area_type):
    df2 = df.copy(deep=True)
    df2 = df2[df2[area_type]>0]
    if area_type == "State":
        df2=df2[df2["District"]==0]
    dflang= df2[df2[lang_col]==lang_name].drop_duplicates(subset = ["AreaName", lang_col])
    AllAreas =df2["AreaName"].unique().tolist()
    LangAreas = dflang["AreaName"].unique().tolist()
    emptyAreas = [a for a in AllAreas if a not in LangAreas]
    toAdd = {'AreaName': emptyAreas}
    #dflang.append(pd.DataFrame(toAdd)
    dflang.loc[len(dflang)] = toAdd              
    dflang.fillna(0)
    if lang_col == "LangGroup":
        dflang = dflang[['State', 'District', 'AreaName', lang_col, 
                         'GroupAgg_Total', 'GroupAgg_Rural', 'GroupAgg_Urban',                        
           'LangGroup_Total_%', 'LangGroup_Rural_%', 'LangGroup_Urban_%']]
    if lang_col == "LangName":
        dflang = dflang[['State', 'District', 'AreaName', lang_col, 'Total', 'Rural', 'Urban',                          
                         'LangName_Total_%', 'LangName_Rural_%', 'LangName_Urban_%']]
        
    dflang.columns = ['State', 'District' , area_type + 'Name', 
                      lang_col, 'Total', 'Rural', 'Urban',                         
                         'Total_%', 'Rural_%', 'Urban_%']  
    return dflang

#find % of speakers of a dialects within the speakers of the corresponding language group
def find_dialects_perc(df, lang_name):
    dftest = df[df["LangGroup"]==lang_name]
    df_summary = dftest[["LangName", "Total"]].groupby("LangName").agg("sum").reset_index()
    df_summary["Total"] =100*df_summary["Total"]/dftest["Total"].sum()
    df_summary = df_summary.sort_values(by = "Total", ascending = False)
    df_summary.columns = ["DialectName", "%_of_Speakers"]
    return df_summary


def find_top_langs(df, lang_type, rank):
    import warnings
    warnings.filterwarnings("ignore")
    pv = df[["AreaName", lang_type, lang_type + "_Total_%"]].pivot_table(index = "AreaName", 
                                                                      columns = lang_type, 
                                                                     values =  lang_type +"_Total_%")
    pv = pv.rename_axis(None, axis=0)  
    #pv = pv.rename_axis(None, axis=1)  
    pv.columns.name = None
    pv.index.name =None
    pv = pv.fillna(0)
    pv.head()
    pv = pv.rank(ascending=False, method='first', axis=1)
    pv = pv.reset_index().melt(id_vars='index')

    pv1 = pv[pv['value'] == rank]
    pd.DataFrame ( pv1.groupby('index')['variable'].apply(list).reset_index())
    pv1["rank_"+str(rank)] = pv1["variable"]
    return pv1