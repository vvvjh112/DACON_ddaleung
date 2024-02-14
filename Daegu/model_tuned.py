import optuna
from sklearn.linear_model import *
from sklearn.metrics import *
from lightgbm import LGBMRegressor, early_stopping
from xgboost import XGBRegressor
import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV
from pycaret.regression import *

# @ignore_warnings(category=ConvergenceWarning)
def huber_modeling(X_train, y_train, X_valid, y_valid):
    def objective(trial):
        param = {
            'epsilon': trial.suggest_uniform('epsilon', 1.0, 3.0),
            'alpha': trial.suggest_uniform('alpha', 0.0001, 0.01),
            'max_iter': trial.suggest_int('max_iter', 100, 1000),
            'tol': trial.suggest_uniform('tol', 1e-6, 1e-3)
        }

        model = HuberRegressor(**param)
        model.fit(X_train, y_train)
        preds = model.predict(X_valid)
        if (preds < 0).sum() > 0:
            print('음수 발생')
            preds = np.where(preds > 0, preds, 0)
        loss = mean_squared_error(y_valid, preds)

        return np.sqrt(loss)

    study_huber = optuna.create_study(direction='minimize', sampler=optuna.samplers.TPESampler(seed=100))
    study_huber.optimize(objective, n_trials=90, show_progress_bar=True)
    print("퓨버 최적 파라미터", study_huber.best_params)
    huber_reg = HuberRegressor(**study_huber.best_params)
    huber_reg.fit(X_train, y_train)

    return huber_reg, study_huber

def lgbm_modeling(X_train, y_train, X_valid, y_valid):
  def objective(trial):
    param = {
        'objective': 'regression',
        'verbose': -1,
        'metric': 'rmse',
        'num_leaves': trial.suggest_int('num_leaves', 2, 1024, step=1, log=True),
        'colsample_bytree': trial.suggest_uniform('colsample_bytree', 0.7, 1.0),
        'reg_alpha': trial.suggest_uniform('reg_alpha', 0.0, 1.0),
        'reg_lambda': trial.suggest_uniform('reg_lambda', 0.0, 10.0),
        'max_depth': trial.suggest_int('max_depth',3, 15),
        'learning_rate': trial.suggest_loguniform("learning_rate", 1e-8, 1e-2),
        'n_estimators': trial.suggest_int('n_estimators', 100, 3000),
        'min_child_samples': trial.suggest_int('min_child_samples', 5, 100),
        'subsample': trial.suggest_loguniform('subsample', 0.4, 1),
    }

    model = LGBMRegressor(**param, random_state=42, n_jobs=-1)
    bst_lgbm = model.fit(X_train,y_train, eval_set = [(X_valid,y_valid)], eval_metric='rmse',callbacks=[early_stopping(stopping_rounds=100)])

    preds = bst_lgbm.predict(X_valid)
    if (preds<0).sum()>0:
      print('negative')
      preds = np.where(preds>0,preds,0)
    loss = mean_squared_log_error(y_valid,preds)

    return np.sqrt(loss)

  study_lgbm = optuna.create_study(direction='minimize',sampler=optuna.samplers.TPESampler(seed=100))
  study_lgbm.optimize(objective,n_trials=90,show_progress_bar=True)
  print("lgbm 최적 파라미터",study_lgbm.best_params)
  lgbm_reg = LGBMRegressor(**study_lgbm.best_params, random_state=42, n_jobs=-1)
  lgbm_reg.fit(X_train,y_train,eval_set = [(X_valid,y_valid)], eval_metric='rmse', callbacks=[early_stopping(stopping_rounds=100)])

  return lgbm_reg,study_lgbm


def xgb_modeling(X_train, y_train, X_valid, y_valid):
  def objective(trial):
    params = {
        'learning_rate': trial.suggest_float('learning_rate', 0.0001, 0.1),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 20),
        'gamma': trial.suggest_float('gamma', 0.01, 1.0),
        'reg_alpha': trial.suggest_float('reg_alpha', 0.01, 1.0),
        'reg_lambda': trial.suggest_float('reg_lambda', 0.01, 1.0),
        'max_depth': trial.suggest_int('max_depth', 3, 15), # Extremely prone to overfitting!
        'n_estimators': trial.suggest_int('n_estimators', 300, 3000, 200), # Extremely prone to overfitting!
        'eta': trial.suggest_float('eta', 0.007, 0.013), # Most important parameter.
        'subsample': trial.suggest_discrete_uniform('subsample', 0.3, 1, 0.1),
        'colsample_bytree': trial.suggest_discrete_uniform('colsample_bytree', 0.4, 0.9, 0.1),
        'colsample_bylevel': trial.suggest_discrete_uniform('colsample_bylevel', 0.4, 0.9, 0.1),
    }

    model = XGBRegressor(**params, random_state=42, n_jobs=-1, objective='reg:squaredlogerror')
    bst_xgb = model.fit(X_train,y_train, eval_set = [(X_valid,y_valid)], eval_metric='rmsle', early_stopping_rounds=100,verbose=False)

    preds = bst_xgb.predict(X_valid)
    if (preds<0).sum()>0:
      print('negative')
      preds = np.where(preds>0,preds,0)
    loss = mean_squared_log_error(y_valid,preds)

    return np.sqrt(loss)

  study_xgb = optuna.create_study(direction='minimize', sampler=optuna.samplers.TPESampler(seed=100))
  study_xgb.optimize(objective,n_trials=90,show_progress_bar=True)
  print("xgb 최적 파라미터", study_xgb.best_params)
  xgb_reg = XGBRegressor(**study_xgb.best_params, random_state=42, n_jobs=-1, objective='reg:squaredlogerror')
  xgb_reg.fit(X_train,y_train,eval_set = [(X_valid,y_valid)], eval_metric='rmsle', early_stopping_rounds=100,verbose=False)

  return xgb_reg, study_xgb


def grid_search(model, param, trainX, trainY):
    print(model," 그리드 서치 시작")
    grid = GridSearchCV(model,param_grid=param,n_jobs=-1,scoring='rmse',cv=4,verbose=1)
    grid.fit(trainX,trainY)
    best_xgb = grid.best_estimator_
    print(model,' : 최적의 하이퍼 파라미터 : ', grid.best_params_)

    return grid

def compare_model(train_set):
    clf = setup(data=train_set, target='ECLO', train_size=0.8)
    best_model = compare_models()
    compare_models(n_select = 5, sort = 'RMSLE')

def pycaret_predict(model,test_set):
    model_py_1 = create_model(model)
    tuned_md = tune_model(model_py_1,optimize = 'RMSLE')
    print(tuned_md)
    final_model = finalize_model(tuned_md)
    prediction = predict_model(final_model, data = test_set)
    result = prediction['prediction_label']
    return result
