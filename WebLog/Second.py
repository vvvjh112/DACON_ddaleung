import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# sessionID : 세션 ID
# userID : 사용자 ID
# TARGET : 세션에서 발생한 총 조회수
# browser : 사용된 브라우저
# OS : 사용된 기기의 운영체제
# device : 사용된 기기
# new : 첫 방문 여부 (0: 첫 방문 아님, 1: 첫 방문)
# quality : 세션의 질 (거래 성사를 기준으로 측정된 값, 범위: 1~100)
# duration : 총 세션 시간 (단위: 초)
# bounced : 이탈 여부 (0: 이탈하지 않음, 1: 이탈함)
# transaction : 세션 내에서 발생의 거래의 수
# transaction_revenue : 총 거래 수익
# continent : 세션이 발생한 대륙
# subcontinent : 세션이 발생한 하위 대륙
# country : 세션이 발생한 국가
# traffic_source : 트래픽이 발생한 소스
# traffic_medium : 트래픽 소스의 매체
# keyword : 트래픽 소스의 키워드, 일반적으로 traffic_medium이 organic, cpc인 경우에 설정
# referral_path : traffic_medium이 referral인 경우 설정되는 경로

# RMSE


#plt 한글출력
# plt.rcParams['font.family'] ='Malgun Gothic'
# plt.rcParams['axes.unicode_minus'] =False

# 한글 폰트 경로 지정
font_path = '/Library/Fonts/AppleGothic.ttf'  # 예시로 AppleGothic 폰트 사용

# 한글 폰트 설정
plt.rcParams['font.family'] = 'AppleGothic'

# row 생략 없이 출력
pd.set_option('display.max_rows', None)
# col 생략 없이 출력
pd.set_option('display.max_columns', None)

train = pd.read_csv('Data/train.csv')
test = pd.read_csv('Data/test.csv')
submission = pd.read_csv('Data/sample_submission.csv')


print(train.info())

# 사용된 브라우저별 총 거래 수익 - 완료
# 브라우저별 평균 거래
# 국가별 총 거래 수익 및 거래 수
# 브라우저별 이탈율
# 디바이스별
# OS별
# test셋어 없는 데이터들 제외
# 전체 데이터셋의 세션유지시간 비율

#파생변수
#브라우저별 수익 합계 및 거래 수
sum_browser = train[['browser','transaction_revenue']].groupby(['browser']).sum('transaction_revenue')
sum_browser = sum_browser.reset_index().rename(columns={'transaction_revenue': '합계'})
browser = sum_browser['browser'].unique()
dic={}
for idx, row in sum_browser.iterrows():
    dic[sum_browser.at[idx,'browser']]=sum_browser.at[idx,'합계']

for idx, row in train.iterrows():
    try:
        train.at[idx,'browser_sum'] = dic[train.at[idx,'browser']]
    except KeyError:
        train.at[idx, 'browser_sum'] = 0

for idx, row in test.iterrows():
    try:
        test.at[idx,'browser_sum'] = dic[test.at[idx,'browser']]
    except KeyError:
        test.at[idx, 'browser_sum'] = 0

print("브라우저 수익 합계 생성완료")
# # 국가별
sum_country = train[['country','transaction_revenue']].groupby(['country']).sum('transaction_revenue')
sum_country = sum_country.reset_index().rename(columns={'transaction_revenue': '합계'})
country = sum_country['country'].unique()
dic={}
for idx, row in sum_country.iterrows():
    dic[sum_country.at[idx,'country']]=sum_country.at[idx,'합계']

for idx, row in train.iterrows():
    try:
        train.at[idx,'country_sum'] = dic[train.at[idx,'country']]
    except KeyError:
        train.at[idx, 'country_sum'] = 0

for idx, row in test.iterrows():
    try:
        test.at[idx,'country_sum'] = dic[test.at[idx,'country']]
    except KeyError:
        test.at[idx, 'country_sum'] = 0

print("국가별 수익 합계 생성완료")

# # OS
sum_OS = train[['OS','transaction_revenue']].groupby(['OS']).sum('transaction_revenue')
sum_OS = sum_OS.reset_index().rename(columns={'transaction_revenue': '합계'})
OS = sum_OS['OS'].unique()
dic={}
for idx, row in sum_OS.iterrows():
    dic[sum_OS.at[idx,'OS']]=sum_OS.at[idx,'합계']

for idx, row in train.iterrows():
    try:
        train.at[idx,'OS_sum'] = dic[train.at[idx,'OS']]
    except KeyError:
        train.at[idx, 'OS_sum'] = 0

for idx, row in test.iterrows():
    try:
        test.at[idx,'OS_sum'] = dic[test.at[idx,'OS']]
    except KeyError:
        test.at[idx, 'OS_sum'] = 0

print("OS별 수익 합계 생성완료")

sum_device = train[['device','transaction_revenue']].groupby(['device']).sum('transaction_revenue')
sum_device = sum_device.reset_index().rename(columns={'transaction_revenue': '합계'})
device = sum_device['device'].unique()
dic={}
for idx, row in sum_device.iterrows():
    dic[sum_device.at[idx,'device']]=sum_device.at[idx,'합계']

for idx, row in train.iterrows():
    try:
        train.at[idx,'device_sum'] = dic[train.at[idx,'device']]
    except KeyError:
        train.at[idx, 'device_sum'] = 0

for idx, row in test.iterrows():
    try:
        test.at[idx,'device_sum'] = dic[test.at[idx,'device']]
    except KeyError:
        test.at[idx, 'device_sum'] = 0

print("디바이스별 수익 합계 생성완료")


train.to_csv('train1.csv',index = False)

#시각화 이전 그룹화
# 키워드 비율 브라우저 비율

group_os = train.groupby(['OS']).mean('TARGET')

group_browser = train.groupby(['browser']).mean('TARGET')[['TARGET']].reset_index('browser')
group_browser = group_browser[~group_browser['browser'].str.startswith(';__CT_JOB_ID__:')]

group_device = train.groupby(['device']).mean('TARGET')

group_new = train.groupby(['new']).mean('TARGET')

group_bounced = train.groupby(['bounced']).mean('TARGET')

group_country = train.groupby(['country']).mean('TARGET')

group_source = train.groupby(['traffic_source']).mean('TARGET')

plt.title('OS별 평균 조회수')
plt.xticks(fontsize = 7, rotation = 45, ha = 'right')
sns.lineplot(x=group_os.index, y= 'TARGET', data=group_os, marker = 'o')
# plt.show()

plt.title('브라우저별 평균 조회수')
plt.xticks(fontsize = 7, rotation = 45, ha = 'right')
sns.lineplot(x='browser', y='TARGET', data=group_browser, marker='o')
# plt.show()

plt.title('디바이스별 평균 조회수')
sns.lineplot(x=group_device.index, y= 'TARGET', data=group_device, marker = 'o')
# plt.show()

plt.title('신규여부별 평균 조회수')
sns.barplot(x=group_new.index, y= 'TARGET', data=group_new)
# plt.show()

plt.title('이탈여부별 평균 조회수')
sns.barplot(x=group_bounced.index, y= 'TARGET', data=group_bounced)
# plt.show()

plt.title('나라별 평균 조회수')
plt.xticks(fontsize = 7, rotation = 45, ha = 'right')
sns.lineplot(x=group_country.index, y= 'TARGET', data=group_country, marker = 'o')
# plt.show()

plt.title('소스별 평균 조회수')
plt.xticks(fontsize = 7, rotation = 45, ha = 'right')
sns.lineplot(x=group_source.index, y= 'TARGET', data=group_source, marker = 'o')
# plt.show()

#결측값
train.fillna('-',inplace=True)
test.fillna('-',inplace=True)
# print(train.isna().sum())
print(test.isna().sum())

from sklearn.model_selection import *
from sklearn.preprocessing import *
#인코딩
# category_cols = train_ft.select_dtypes(include="object").columns.tolist()
categorical_features = ["browser", "OS", 'new','bounced', "device", "continent", "subcontinent", "country", "traffic_source", "traffic_medium", "keyword", "referral_path"]
for i in categorical_features:
    # train[i] = LabelEncoder().fit_transform(train[i])
    # test[i] = LabelEncoder().fit_transform(test[i])
    train[i] = train[i].astype('category')
    test[i] = test[i].astype('category')

#합계는 스케일링 하자
mm = StandardScaler()
numeric = train.select_dtypes(exclude=["object", "category"]).drop(['TARGET'], axis=1).columns.tolist()
train[numeric] = mm.fit_transform(train[numeric])
test[numeric] = mm.fit_transform(test[numeric])

#데이터 분리
x = train.drop(['sessionID','userID','TARGET'],axis=1)
y = train['TARGET']

test= test.drop(['sessionID','userID'],axis =1)

trainX, testX, trainY, testY = train_test_split(x,y,test_size=0.2,random_state=2024)

print(trainX.columns)

#Catboost / xgboost / LGBM /
from catboost import CatBoostRegressor, Pool
from lightgbm import LGBMRegressor
from sklearn.metrics import *
import model_tuned as mt

#pycaret
# mt.compare_model(train.drop(['sessionID','userID'],axis=1),'TARGET')


#LGBM
# lgbm_model = LGBMRegressor()
# lgbm_model.fit(trainX,trainY)
# print(lgbm_model.feature_importances_)

# 옵튜나
# lgbm , lgbm_study = mt.lgbm_modeling(trainX,trainY,testX,testY)
# lgbm_predict = lgbm.predict(test)
# submission['TARGET'] = lgbm_predict
#1차
# hp = {'num_leaves': 741, 'colsample_bytree': 0.9497960333038377, 'reg_alpha': 0.31953049619109103, 'reg_lambda': 2.976008557172993, 'max_depth': 15, 'learning_rate': 0.002312138094213604, 'n_estimators': 2516, 'min_child_samples': 98, 'subsample': 0.6945329803389395}
#2차
# hp = {'num_leaves': 294, 'colsample_bytree': 0.8463048890782741, 'reg_alpha': 0.30820014520494504, 'reg_lambda': 1.9536106744358568, 'max_depth': 15, 'learning_rate': 0.0037663760814518783, 'n_estimators': 2580, 'min_child_samples': 35, 'subsample': 0.7301038177177746}
#3차 - 국가별 수익합계추가 후
hp = {'num_leaves': 343, 'colsample_bytree': 0.8799056412183298, 'reg_alpha': 0.9188535423836559, 'reg_lambda': 0.5661962662592113, 'max_depth': 13, 'learning_rate': 0.0022962143663780715, 'n_estimators': 2574, 'min_child_samples': 38, 'subsample': 0.9721091518154885}
#4차
# hp = {'num_leaves': 289, 'colsample_bytree': 0.9149895549919833, 'reg_alpha': 0.5263310142037994, 'reg_lambda': 2.7726892614197065, 'max_depth': 12, 'learning_rate': 0.007467321973137051, 'n_estimators': 2415, 'min_child_samples': 37, 'subsample': 0.6015072822715607}
#5차
# hp = {'num_leaves': 211, 'colsample_bytree': 0.9470521055101154, 'reg_alpha': 0.6178226193707839, 'reg_lambda': 0.8213178312797914, 'max_depth': 15, 'learning_rate': 0.002703201645609544, 'n_estimators': 2569, 'min_child_samples': 90, 'subsample': 0.8756407186241856}
lm = LGBMRegressor(**hp)
lm.fit(trainX,trainY)
print(lm.feature_importances_)
pred = lm.predict(testX)
print("점수 ", mean_squared_error(testY,pred,squared=False))
#1차 파생변수 추가 후 2.686622
#2차 파생변수 추가 후 2.630477 - 스케일링 전 / 옵튜나 전
#2차 옵튜나 후 ? 2.732848854424877 - 스케일링 전
#2차 스케일링 후 1차 파라미터로 2.6306
#3차 2.624112
#4차 2.652026
#5차 2.622864 - 3차 파라미터로함
# lgbm.fit(trainX,trainY)
# print(lgbm.feature_importances_)
# pred = lgbm.predict(testX)
# print("점수 ", mean_squared_error(testY,pred,squared=False))



# pred = lm.predict(test)
# submission['TARGET'] = pred
#
# print(trainX.columns)


# train_pool = Pool(data = trainX, label=trainY, cat_features=categorical_features)
# test_pool = Pool(data = test, cat_features=categorical_features)
# testY_pool = Pool(data = testX, cat_features=categorical_features)
# cat_model = CatBoostRegressor()
# cat_model.fit(train_pool)
# print(cat_model.feature_importances_)

#옵튜나
# cat, cat_study = mt.cat_modeling(trainX,trainY,testX,testY)
# cat_predict = cat.predict(test_pool)
# submission['TARGET'] = cat_predict

# 1차 최적화 'iterations': 5971, 'od_wait': 1305, 'learning_rate': 0.10223435608939285, 'reg_lambda': 58.80594893120358, 'subsample': 0.6930612709955952, 'random_strength': 17.7639310763122, 'depth': 8, 'min_data_in_leaf': 11, 'leaf_estimation_iterations': 5, 'bagging_temperature': 0.23513945991239923, 'colsample_bylevel': 0.7079422421178576
# param = {'iterations': 8769, 'od_wait': 501, 'learning_rate': 0.10526607776351413, 'reg_lambda': 14.1751878095561, 'subsample': 0.4300999921535704, 'random_strength': 49.66986335012443, 'depth': 10, 'min_data_in_leaf': 21, 'leaf_estimation_iterations': 14, 'bagging_temperature': 34.49049196510442, 'colsample_bylevel': 0.6744327714737617}
# cm = CatBoostRegressor(**param)
# cm.fit(train_pool)
# pred = cm.predict(testY_pool)
# print("Cat 점수 : ",mean_squared_error(testY,pred,squared=False))
# Cat 점수 :  2.800969683434413
# cat_pre = cm.predict(test_pool)
# submission['TARGET'] = cat_pre


#TARGET값 0보다 작은거 0으로 보정하기
import datetime
# title = 'LGBM'+str(datetime.datetime.now().month)+'_'+str(datetime.datetime.now().day)+'_'+str(datetime.datetime.now().hour)+'_'+str(datetime.datetime.now().minute)+'.csv'
# title = 'CAT'+str(datetime.datetime.now().month)+'_'+str(datetime.datetime.now().day)+'_'+str(datetime.datetime.now().hour)+'_'+str(datetime.datetime.now().minute)+'.csv'
# submission.loc[submission['TARGET'] < 0.0, 'TARGET'] = 0.0
# submission.to_csv(title,index=False)

