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
