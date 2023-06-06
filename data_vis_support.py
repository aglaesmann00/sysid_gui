#%%
import pandas as pd
import numpy as np
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm
import statsmodels as sm
import copy

from sklearn.model_selection import cross_validate
from sklearn.model_selection import RepeatedKFold
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor 
from sklearn.neural_network import MLPRegressor

#import Model_Metrics as MM

cp = 1

def read_to_df(filename):
    #delete error data
    df = (pd.read_csv(filename,na_values=["[-11059] No Good Data For Calculation"]))
    df = df.dropna()
    #delete empty rows
    # nan_value = float("NaN")
    # df.replace("", nan_value, inplace=True)
    # df.dropna(subset = ["Time"], inplace=True)
    return df


def df_add_feature():
    return    

def to_database(df,variables):
    x = pd.DataFrame(df, columns=variables)
    return x

def print_info(database,filename):
    print('-------------------------------------------')
    print('DATA FILE: ',filename)
    print(database.info())
    with pd.option_context('display.max_columns', 40):
        print(database.describe(include='all'))
    print('-------------------------------------------')

def xy_plot(df,x_axis,y_axis):
    df.plot(x = x_axis, y = y_axis, kind = 'scatter', s = 5)
    plt.show()

def scatter_plot(df,variables):
    print('Data Count = ',len(df))
    sns.pairplot(df[variables].sample(int(len(df))),diag_kind="kde",plot_kws={'alpha':0.1})
    #sns.pairplot(df[variables],diag_kind="kde",plot_kws={'alpha':0.1})
    plt.show()

def filter(df,column,min_val,max_val,data_filtered):
    filter_variable = df[column]

    #print(max_val)
    if min_val and max_val:
        if min_val > max_val:
            df_copy1 = df[filter_variable > min_val]
            df_copy2 = df[filter_variable < max_val]
            df = pd.concat([df_copy1,df_copy2])
            data_filtered.append('%s < %s < %s' % (min_val,column,max_val))
        else:
            df = df[filter_variable > min_val]
            df = df[filter_variable < max_val]
            data_filtered.append('%s > %s > %s' % (min_val,column,max_val))
    elif min_val:
        print(min_val)
        df = df[filter_variable > min_val]
        data_filtered.append('%s > %s' % (column,min_val))
    elif max_val:
        df = df[filter_variable < max_val]
        data_filtered.append('%s < %s' % (column,max_val))
    return df, data_filtered

def contrast_plot(df,column,variables,min_val_str,max_val_str):
    df_copy = copy.copy(df)
    print(variables)
    if min_val_str and max_val_str:
        min_ = float(min_val_str)
        max_ = float(max_val_str)
        hue = '%s < %s < %s' % (min_,column,max_)
        variables.append(hue)
        df_copy[hue] = (df_copy[column] > min_) & (df_copy[column] < max_)
    elif min_val_str:
        min_ = float(min_val_str)
        hue = '%s > %s' % (column,min_)
        variables.append(hue)
        df_copy[hue] = df_copy[column] > min_
    elif max_val_str:
        max_ = float(max_val_str)
        hue = '%s < %s' % (column,max_)
        variables.append(hue)
        df_copy[hue] = df_copy[column] < max_
    row_count = int(len(df))
    column_count = int(len(variables))-1
    df_data_count = row_count*column_count
        
    if df_data_count > 350000:
        print('true')
        sample_size = 350000//column_count
    else:
        sample_size = row_count
    print(sample_size*column_count)
    #sns.pairplot(df_copy[variables].sample(sample_size),diag_kind="kde",hue=hue, plot_kws={'alpha':0.07})
    #plt.show()
    variables.remove(hue)

def corrolation_plot(df,factors,product):
    if product != '':
        factors.append(product)
    fig = plt.subplots(1,1,figsize=(15,10))
    df_gt1 = pd.DataFrame(df ,columns = factors)
    corr = df_gt1.corr(method = 'kendall')
#    corr = df_gt1.corr()
    sns.heatmap(corr, vmax  = 1, square = True, annot = True, cmap = 'viridis')
    plt.show()

    factors.remove(product)

def create_model(df,factors,product_str,reg_choice):
    x = pd.DataFrame(df, columns=factors)
    y = pd.DataFrame(df, columns=[product_str])
    products = y[product_str]
    #Robust Scalar
    # df = scaler.fit_transform(x)
    # df = scaler.fit_transform(y)
    #spliting the sets
    x_train, x_test, y_train, y_test = train_test_split(x,y, test_size = 0.4, random_state = 34)
    #train
    if reg_choice == 'LinearRegression':
        reg = LinearRegression().fit(x_train, y_train.values.ravel())
    if reg_choice == 'GradientBoostingRegressor':
        reg = GradientBoostingRegressor().fit(x_train, y_train.values.ravel())
    if reg_choice == 'MLPRegressor':
        Neural_regr = MLPRegressor(random_state=98, max_iter=1000).fit(x_train, y_train.values.ravel())
        print("%s : r2 = " %(reg_choice), Neural_regr.score(x_test, y_test))       
        #hypertuning routine
        # modelType = MLPRegressor()
        # params = {'hidden_layer_sizes': [(50,50,50,), (100,), (100,100,), (100,100,100,), (50,50,50,)], 
        #               'activation': ['relu','tanh','logistic', 'identity'],
        #               'alpha': [0.0001, 0.05, 0.02, 0.03, 0.09],
        #               'learning_rate': ['constant','adaptive'],
        #               'max_iter' :[5000],
        #               }
        
        # grid_search_capacity = GridSearchCV( modelType, params, cv = 5, scoring='neg_mean_squared_error', verbose=0, n_jobs=-1)
        # grid_result = grid_search_capacity.fit(x_train, y_train.values.ravel())
        # best_params = grid_result.best_params_
        # print(best_params)
        # best_mlp = MLPRegressor(hidden_layer_sizes = best_params["hidden_layer_sizes"], 
        #                         activation =best_params["activation"],
        #                         alpha= best_params['alpha'],
        #                         learning_rate= best_params['learning_rate'],
        #                         max_iter= 5000, 
        #                         n_iter_no_change = 200).fit(x_train, y_train.values.ravel())
        # #Print R2 score
        # print("r2 = ", best_mlp.score(x_test, y_test))
    
    df = checkNormalityPlots(df,reg.predict(x),y[product_str],'%s Model' %(product_str))
    #aic = MM.AIC(reg.predict(x), y[product_str], x.shape[0], x.shape[1])
    #bic = MM.BIC(reg.predict(x), y[product_str], x.shape[0], x.shape[1])
    print("%s : r2 = " %(reg_choice), reg.score(x_test, y_test))
    #print('AIC : ',aic)
    #('BIC : ',bic)
    print('factors: ', factors)
    print('product: ', [product_str])

    cv = RepeatedKFold(n_splits=5, n_repeats=5, random_state=0)
    cv_model = cross_validate(reg,x,y,cv=cv,return_estimator=True)

    coefs = pd.DataFrame([est[-1].regressor_.coef_ * est[:-1].transform(x.iloc[train_idx]).std(axis=0)
            for est, (train_idx, _) in zip(cv_model["estimator"], cv.split(x, y))],columns=factors,)
    plt.figure(figsize=(9, 7))
    sns.stripplot(data=coefs, orient="h", color="k", alpha=0.5)
    sns.boxplot(data=coefs, orient="h", color="cyan", saturation=0.5, whis=10)
    plt.axvline(x=0, color=".5")
    plt.xlabel("Coefficient importance")
    plt.title("Coefficient importance and its variability")
    plt.suptitle("Ridge model, small regularization")
    plt.subplots_adjust(left=0.3)

    return 

def checkNormalityPlots(df,predictions, actual, heading):
    df['Predictions'] = predictions
    predictions = predictions.flatten()
    residuals = actual - predictions
    
    residuals_normalized = (residuals - residuals.mean()) / residuals.std()
    df['Residuals'] = residuals
    df['Residuals_Norm'] = residuals_normalized
    
    fig, (ax1) = plt.subplots(1,1,figsize=(15,10))
    sns.scatterplot(x = predictions, y = residuals, ax = ax1, label = heading + ' Residual Plot', alpha = .1)
    
    fig, (ax2) = plt.subplots(1,1,figsize=(10,10))
    sm.qqplot(residuals_normalized, line = '45', ax = ax2,  ylabel = heading + ' QQ Norm Plot', alpha = .1)
    
    # Plot the histogram.
    fig, (ax3) = plt.subplots(1,1,figsize=(15,10))
    plt.hist(residuals_normalized, bins=100, density=True, alpha=0.2, color='b')
    x = np.arange(-3, 3, 0.001)
    plt.plot(x, norm.pdf(x, 0, 1), color = 'r')
    title = 'heading desnity curve'

    plt.show()
    return df

def common_text_tags(df, common_text):
    tag_list = []
    for column in df:
        if common_text in column:
            tag_list.append(column)
    return tag_list
# %%
