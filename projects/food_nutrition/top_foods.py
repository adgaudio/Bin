import pandas as pd


nutr_def = pd.read_csv(
    './data/usda_nutrition_db/NUTR_DEF.csv', index_col=['Nutr_No'])
food_des = pd.read_csv(
    './data/usda_nutrition_db/FOOD_DES.csv', index_col=['NDB_No'])
header = pd.read_csv('./header_NUT_DATA.csv', index_col='Field Name')
df = data = pd.read_csv(
    './data/usda_nutrition_db/NUT_DATA.csv', index_col=['NDB_No', 'Nutr_No'])

# substances are unique by ndb_no and nutr_no
assert not (
    df.groupby(level=['NDB_No', 'Nutr_No'])['Nutr_Val'].count() > 1).any().any()

# substance max per category
good_foods = df.ix[
    df.groupby(level='Nutr_No', group_keys=False)\
        .apply(lambda x: x['Nutr_Val'] == x['Nutr_Val'].max())]
good_foods = good_foods.join(nutr_def['NutrDesc'])
good_foods = good_foods.join(food_des['Long_Desc'])

good_foods.head()
good_foods['Long_Desc'].value_counts()

z = good_foods['NutrDesc'].value_counts()
uncommon_nutrients = z[z <= z.quantile(.99)]
common_nutrients = z[z > z.quantile(.99)]
print("dropping", common_nutrients)
print("keeping")
z2 = good_foods.ix[good_foods['NutrDesc'].isin(uncommon_nutrients.index)]
print(z2['Long_Desc'].value_counts())

# For each nutrient, the mean and std grow at same rate
# zz = df.groupby(level='Nutr_No', group_keys=False)\
    # .apply(lambda x: x['Nutr_Val'].describe())
# zz.plot(kind='scatter', x='mean', y='std', logx=True, logy=True)
