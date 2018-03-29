import pandas as pd
from datetime import datetime
df = pd.read_csv('PLUTO17v1.1/MN2017V11.csv')
df2 = pd.read_csv("Rodent_Inspection.csv")

df.CT2010.fillna(0, inplace=True)
df['ct_f'] = df.CT2010.astype(int)
df['ct_f'] = df.apply(lambda x: (str(x['ct_f'])+'00').zfill(6), axis=1)
df['cbg'] = df.apply(lambda x: 'Block Group ' + str(x['CB2010'])[:1], axis=1)

df = df[['Address','cbg', 'ct_f']]

df2 = df2[df2.INSPECTION_TYPE == 'INITIAL']
df2 = df2[df2.BOROUGH.isin(['Manhattan'])]
df2 = df2[df2.HOUSE_NUMBER == df2.HOUSE_NUMBER]
df2['ADDRESS'] = df2.apply(lambda x: str(x['HOUSE_NUMBER']).strip() + " " + str(x['STREET_NAME']).strip(), axis=1)

def convert_ym_2_yq(ym):
    l = ym.split()
    if int(l[1]) <=3 and int(l[1]) >=1:
        return l[0] + " Q1"
    if int(l[1]) <=6 and int(l[1]) >=4:
        return l[0] + " Q2"
    if int(l[1]) <=9 and int(l[1]) >=7:
        return l[0] + " Q3"
    if int(l[1]) <=12 and int(l[1]) >=10:
        return l[0] + " Q4"

df2['INSPECTION_DATE_TS']= df2.apply(lambda x: datetime.strptime(x['INSPECTION_DATE'], '%m/%d/%Y %H:%M:%S %p'), axis=1)
df2['INSPECTION_MONTH'] = df2.apply(lambda x: x['INSPECTION_DATE_TS'].month, axis=1)
df2['INSPECTION_YEAR'] = df2.apply(lambda x: x['INSPECTION_DATE_TS'].year, axis=1)
df2['INSPECTION_YEAR_MONTH'] = df2.apply(lambda x: str(x['INSPECTION_DATE_TS'].year) + " " + str(x['INSPECTION_DATE_TS'].month), axis=1)
df2['INSPECTION_YEAR_Q'] = df2.apply(lambda x: (convert_ym_2_yq(x['INSPECTION_YEAR_MONTH'])), axis=1)

df2 = df2[df2['INSPECTION_YEAR'] >= 2010]
df2 = df2[df2['INSPECTION_YEAR'] < 2018]

df2['RESULT'] = df2.apply(lambda x: 1 if x['RESULT'] == 'Active Rat Signs' else 0, axis=1)

df2 = df2[['ADDRESS','RESULT', 'INSPECTION_YEAR_Q' ]]

df3 = df2.merge(df, left_on = 'ADDRESS', right_on = 'Address')

df3 = df3.groupby(['cbg','ct_f','INSPECTION_YEAR_Q'], as_index=False).agg({'RESULT':['sum','count']})
a = df3.columns.get_level_values(0).tolist()
b = df3.columns.get_level_values(1).tolist()
df3.columns = [m+n for m,n in zip(a,b)]

df_quarters = df2.groupby('INSPECTION_YEAR_Q', as_index=False)['RESULT'].sum()
del df_quarters['RESULT']

df_cb = df.groupby(['cbg','ct_f'], as_index=False)['Address'].first()
del df_cb['Address']

df_all = df_quarters.assign(foo=1).merge(df_cb.assign(foo=1)).drop('foo', 1)

df_combos = df_all.merge(df3, how='left', on=['INSPECTION_YEAR_Q','cbg','ct_f']).copy()
df_combos.fillna(0, inplace=True)

def b(failed,total):
    if total == 0:
        return 0
    elif failed >0:
        return 1
    else:
        return 2

df_combos['RESULT'] = df_combos.apply(lambda x: b(x['RESULTsum'],x['RESULTcount']), axis=1)

df_qn = df_all.groupby('INSPECTION_YEAR_Q', as_index=False).cbg.count()
df_qn.sort_values('INSPECTION_YEAR_Q', inplace= True)
df_qn.reset_index(inplace=True)
del df_qn['cbg']
df_combos = df_combos.merge(df_qn, on ='INSPECTION_YEAR_Q')
df_combos['Quarter_Number'] = df_combos['index']
del df_combos['index']
del df_combos['INSPECTION_YEAR_Q']
del df_combos['RESULTsum']
del df_combos['RESULTcount']

df_combos.to_csv('quarterly_rodent_data.csv')