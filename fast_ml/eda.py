import sys
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import norm
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import Markdown, display
from fast_ml.utilities import printmd , display_all, normality_diagnostic , plot_categories , \
plot_categories_with_target , calculate_mean_target_per_category , plot_target_with_categories


def df_summary(df):
    """
    This function gives following insights about each variable -
        Datatype of that variable
        Number of unique values is inclusive of missing values if any
        Also displays the some of the unique values. (set to display upto 10 values)
        Number of missing values in that variable
        Percentage of missing values for that variable

    Parameters:
    ----------
        df : dataframe for analysis

    Returns:
    --------
        df : returns a dataframe that contains useful info for the analysis
    """
    data_dict = {}
    for var in df.columns:
    
        data_dict[var] = {'data_type': df[var].dtype, 
                          'num_unique_values': df[var].nunique(),
                          'sample_unique_values' : df[var].unique()[0:10].tolist(),
                          'num_missing' : df[var].isnull().sum(),
                          'perc_missing' : 100*df[var].isnull().mean()
                         }

    info_df = pd.DataFrame(data_dict).transpose()
    info_df = info_df[['data_type', 'num_unique_values', 'sample_unique_values', 'num_missing', 'perc_missing']]
    return info_df
   
#### -------- Numerical Variables ------- #####
###############################################
def numerical_variable_detail(df, variable, model = None, target=None, threshold = 20):
    """
    This provides basic EDA of the Numerical variable passed,
        - Basic Statistics like Count, Data Type, min, max, mean, median, etc., 
        - Missing Values count and missing percentages 
        - Generates distribution plots. Histogram and KDE Plots 
        - Skewness and Kurtosis
        - Q-Q plot to check Normality
        - Box plot to check the spread outliers
        - Outliers using IQR
        - Various variable transformations
    Parameter :
    ----------
        df : Dataframe for which Analysis to be performed
        variable: Pass the Numerical variable for which EDA is required
        model : type of problem - classification or regression
            For classification related analysis. use 'classification' or 'clf'
            For regression related analysis. use 'regression' or 'reg'
        target : Define the target variable, if you want to see the relationship between given list of varaible with Target variable, default None
        threshold : if number of distinct value in a series is less than this value then consider that variable for categorical EDA
    
    Return :
    -------
        Returns summary & plots of given variable
    """
    eda_df = df.copy(deep=True)
    c = variable
    s = eda_df[c]
    
    # 1. Basic Statistics

    print ('Total Number of observations : ', len(s))
    print ()

    print ('Datatype :', (s.dtype))
    print ()

    print ('Number of distinct values :', s.nunique())
    print ()
    
    if s.nunique() < threshold:
        print (f' Number of unique values in this variable is less then threshold value of {threshold}')
        print ('\n Consider using Categorical EDA')
        sys.exit()
    
    else:
        printmd ('**<u>5 Point Summary :</u>**')

        print ('  Minimum  :\t\t', s.min(), '\n  25th Percentile :\t', np.percentile(s, 25), 
               '\n  Median :\t\t', s.median(), '\n  75th Percentile :\t', np.percentile(s, 75), 
               '\n  Maximum  :\t\t', s.max())

        print ()

        # 2. Missing values

        printmd ('**<u>Missing Values :</u>**')

        print ('  Number :', s.isnull().sum())
        print ('  Percentage :', s.isnull().mean()*100, '%')

        # 3. Histogram

        printmd ('**<u>Variable distribution and Spread statistics :</u>**')

        sns.distplot(s.dropna(), hist = True, fit = norm, kde = True)
        plt.show()

        # 4. Spread Statistics

        print ('Skewness :' , s.skew())
        print ('Kurtosis :', s.kurt())
        print ()

        # 5. Q-Q plot
        printmd ('**<u>Normality Check :</u>**')
        res = stats.probplot(s.dropna(), dist = 'norm', plot = plt)
        plt.show()

        # 6. Box plot to check the spread outliers
        print ()
        printmd ('**<u>Box Plot and Visual check for Outlier  :</u>**')
        sns.boxplot(s.dropna(), orient = 'v')
        plt.show()

        # 7. Get outliers. Here distance could be a user defined parameter which defaults to 1.5

        print ()
        printmd ('**<u>Outliers (using IQR):</u>**')

        quartile_1, quartile_3 = np.percentile(s, [25,75])
        IQR = quartile_3 - quartile_1
        upper_boundary = quartile_3 + 1.5 * IQR
        lower_boundary = quartile_1 - 1.5 * IQR

        print ('  Right end outliers :', np.sum(s>upper_boundary))
        print ('  Left end outliers :', np.sum(s < lower_boundary))


        # 8. Relationship with Target Variable
        
        printmd ('**<u>Bivariate plots: Relationship with Target Variable:</u>**')
        if target :
            if model == 'classification' or model == 'clf':
                plt.figure(figsize = (16, 4))
                plt.subplot(1, 2, 1)
                sns.boxplot(x=eda_df[target], y=c, data=eda_df)
                plt.subplot(1, 2, 2)
                sns.distplot(eda_df[eda_df[target] == 1][c], hist=False, label='Target=1')
                sns.distplot(eda_df[eda_df[target] == 0][c], hist=False, label='Target=0')
                plt.show()

        
        # 9. Various Variable Transformations

        print ()
        printmd (f'**<u>Explore various transformations for {c}</u>**')
        print ()

        print ('1. Logarithmic Transformation')
        try:
            s = np.where(s == 0, 1, s)
            s_log = np.log(s)
            normality_diagnostic(s_log,c)
        except:
            print ("Can't compute log transformation")

        print ('2. Exponential Transformation')
        try:
            s_exp = np.exp(s)
            normality_diagnostic(s_exp,c)
        except:
            print ("Can't compute Exponential transformation")

        print ('3. Square Transformation')
        try:
            s_sqr = np.square(s)
            normality_diagnostic(s_sqr,c)
        except:
            print ("Can't compute Square transformation")

        print ('4. Square-root Transformation')
        try:
            s_sqrt = np.sqrt(s)
            normality_diagnostic(s_sqrt,c)
        except:
            print ("Can't compute Square-root transformation")

        print ('5. Box-Cox Transformation')
        try:
            s_boxcox, lambda_param = stats.boxcox(s)
            normality_diagnostic(s_boxcox,c)
            print ('Optimal Lambda for Box-Cox transformation is :', lambda_param )
            print ()
        except:
            print ("Can't compute Box-Cox transformation")

        print ('6. Yeo Johnson Transformation')
        try:
            s = s.astype('float')
            s_yeojohnson, lambda_param = stats.yeojohnson(s)
            normality_diagnostic(s_yeojohnson,c)
            print ('Optimal Lambda for Yeo Johnson transformation is :', lambda_param )
            print ()
        except:
            print ("Can't compute Yeo Johnson transformation")

        
def numerical_plots(df, variables, normality_check = False):
    """
    This function generates the univariate plot for the all the variables in the input variables list. 
    normality check and kde plot is optional

    Parameters:
    -----------
        df : Dataframe for which Analysis to be performed
        variables : input type list. All the Numerical variables needed for plotting
        normality_check: 'True' or 'False'
            if True: then it will plot the Q-Q plot and kde plot for the variable
            if False: just plot the histogram of the variable

    Returns:
    --------
        Numerical plots for all the variables

    """
    eda_df = df.copy(deep=True)
    length_df = len(eda_df)

    if normality_check==True:
        for i, var in enumerate(variables, 1):
            
            try:
                printmd (f'**<u> {i}. Plot for {var}</u>**')
                s = eda_df[var]
                normality_diagnostic(s, var)

            except:
                print(f"Plots for variable : {var} can't be plotted")

    if normality_check==False:
        for i, var in enumerate(variables, 1):
            
            try:
                print (f'{i}. Plot for {var}')
                s = eda_df[var]

                plt.figure(figsize = (12, 4))
                ax1 = sns.distplot(s, hist = True)
                ax1.set_title('Histogram', fontsize=17)
                ax1.set_xlabel(var, fontsize=14)
                ax1.set_ylabel('Distribution', fontsize=14)
                plt.show()

            except:
                print(f"Plots for variable : {var} can't be plotted")





    
def numerical_plots_with_target(df, variables, target, model):
    """
    This function generates the bi-variate plot for the all the variables in the input variables list with the target

    Parameters:
    -----------
        df : Dataframe for which Analysis to be performed
        variables : input type list. All the Numerical variables needed for plotting
        target : Target variable
        model : type of problem - classification or regression
                For classification related analysis. use 'classification' or 'clf'
                For regression related analysis. use 'regression' or 'reg'
        

    Returns:
    --------
        Numerical plots for all the variables

    """
    eda_df = df.copy(deep=True)
    length_df = len(eda_df)

    if model == 'classification' or model == 'clf':

        for i, var in enumerate(variables, 1):

            try:
                printmd (f'**<u> {i}. Plot for {var}</u>**')
                plt.figure(figsize = (16, 4))
                ax1 = plt.subplot(1, 2, 1)
                ax1 = sns.boxplot(x=eda_df[target], y=var, data=eda_df)
                ax1.set_title('Box Plot', fontsize=17)
                ax1.set_xlabel(f'Target Variable ({target})', fontsize=14)
                ax1.set_ylabel(var, fontsize=14)

                ax2 = plt.subplot(1, 2, 2)
                ax2 = sns.distplot(eda_df[eda_df[target] == 1][var], hist=False, label='Target=1')
                ax2 = sns.distplot(eda_df[eda_df[target] == 0][var], hist=False, label='Target=0')
                ax2.set_title('KDE Plot', fontsize=17)
                ax2.set_xlabel(var, fontsize=14)
                plt.show()

            except:
                print(f"Plots for variable : {var} can't be plotted")

    if model == 'regression' or model == 'reg':
        for i, var in enumerate(variables, 1):
            try:
                print (f'{i}. Plot for {var}')
                plt.figure(figsize = (10, 4))
                ax = sns.regplot(data = eda_df, x = var, y=target)
                ax.set_title(f'Scatter Plot bw variable ({var}) and target ({target})', fontsize=17)
                ax.set_xlabel(var, fontsize=14)
                ax.set_ylabel(target, fontsize=14)
                plt.show()
            except:
                print(f"Plots for variable : {var} can't be plotted")


        

def numerical_check_outliers(df, variables=None, tol=1.5, print_vars = False):
    """
    This functions checks for outliers in the dataset using the Inter Quartile Range (IQR) calculation
    IQR is defined as quartile_3 - quartile_1
    lower_bound = quartile_1 - tolerance_value * IQR
    upper_bound = quartile_3 + tolerance_value * IQR
    
    Parameters:
    -----------
        df : dataset on which you are working on
        variables: optional parameter. list of all the numeric variables. 
                   if not provided then it automatically identifies the numeric variables and analyzes for them
        tol : tolerance value(default value = 1.5) Usually it is used as 1.5 or 3
        
    Returns:
    --------
        dataframe with variables that contain outliers
    """
    
    outlier_dict = {}
    
    if variables == None:
        #variables = df.select_dtypes(include = ['int', 'float']).columns
        variables = df.select_dtypes(exclude = ['object']).columns
        if print_vars:
            print(variables)
        
    else:
        variables = variables
        if print_vars:
            print(variables)
        
    for var in variables:
        s = df.loc[df[var].notnull(), var]
        
        quartile_1, quartile_3 = np.percentile(s, [25,75])
        iqr = quartile_3 - quartile_1
        lower_bound = quartile_1 - tol*iqr
        upper_bound = quartile_3 + tol*iqr
        
        lower_bound_outlier = np.sum(s<lower_bound)
        upper_bound_outlier = np.sum(s>upper_bound)
        #if lower_bound_outlier >0 or upper_bound_outlier>0:
        outlier_dict[var] = {'lower_bound_outliers': lower_bound_outlier, 
                                 'upper_bound_outliers' : upper_bound_outlier,
                                 'total_outliers' : lower_bound_outlier+upper_bound_outlier} 
    
    outlier_df = pd.DataFrame(data = outlier_dict).transpose()
    outlier_df = outlier_df.sort_values(by='total_outliers' , ascending = False)
    outlier_df['perc_outliers'] = (outlier_df['total_outliers'] / len(df)).mul(100)
    
    return outlier_df


#### -------- Categorical Variables ------- #####
#################################################

def categorical_plots(df, variables, add_missing = True, add_rare = False, rare_tol=5):
    """

    Parameters:
    -----------
        df : Dataframe for which Analysis to be performed
        variables : input type list. All the categorical variables needed for plotting
        add_missing : default True. if True it will replace missing values by 'Missing'
        add_rare : default False. If True it will group all the smaller categories in a 'rare' category
        rare_tol : Threshold limit (in percentage) to combine the rare occurrence categories, (rare_tol=5) i.e., less than 5% occurance categories will be grouped and forms a rare category 

    Returns:
    --------
        Category plots for all the variables

    """
    eda_df = df.copy(deep=True)
    length_df = len(eda_df)

    for i, var in enumerate(variables, 1):

        printmd (f'**<u> {i}. Plot for {var}</u>**')

        if add_missing:
            eda_df[var] = eda_df[var].fillna('Missing')
        
        s = pd.Series(eda_df[var].value_counts() / length_df)
        s.sort_values(ascending = False, inplace = True)
        
        if add_rare:
            non_rare_label = [ix for ix, perc in s.items() if perc>rare_tol/100]
            eda_df[var] = np.where(eda_df[var].isin(non_rare_label), eda_df[var], 'Rare')


        plot_df = pd.Series(100*eda_df[var].value_counts() / length_df)
        plot_df.sort_values(ascending = False, inplace = True)


        fig = plt.figure(figsize=(12,4))
        ax = plot_df.plot.bar(color = 'royalblue')

        ax.set_title(f'Distribution of variable {var}', fontsize=17)
        #ax.set_xlabel(var, fontsize=14)
        ax.set_ylabel('Percentage', fontsize=14)
        ax.axhline(y=rare_tol, color = 'red')
        ax.axhline(y=rare_tol+5, color = 'darkred')
        plt.show()


def  categorical_plots_with_target(df, variables, target, model='clf', add_missing = True,  rare_tol = 5):
    """
    Parameters:
    -----------
        df : Dataframe for which Analysis to be performed
        variables : input type list. All the categorical variables needed for plotting
        target : Target variable
        model : type of problem - classification or regression
                For classification related analysis. use 'classification' or 'clf'
                For regression related analysis. use 'regression' or 'reg'
        add_missing : default True. if True it will replace missing values by 'Missing'
        rare_tol : {5 or 10}
            percentage line to demonstrate categories with very less data
    Returns:
    --------
        Category plots for all the variables
    """
    eda_df = df.copy(deep=True)
    length_df = len(eda_df)

    for i, var in enumerate(variables, 1):

        printmd (f'**<u> {i}. Plot for {var}</u>**')

        if add_missing:
            eda_df[var] = eda_df[var].fillna('Missing')
        

        plot_df =  calculate_mean_target_per_category (eda_df, var, target)
        cat_order = list(plot_df[var])

        if model in('clf' or 'classification'):
            plot_df[target] = 100*plot_df[target]

        
        # Graph:1 to show the overall event rate across categories
        if model in ('clf', 'classification'):

            tmp = pd.crosstab(eda_df[var], eda_df[target], normalize='columns') * 100
            tmp = tmp.reset_index()
            tmp.rename(columns={0:'target_0', 1:'target_1'}, inplace=True)

            fig, ax = plt.subplots(figsize=(12,4))
            plt.xticks(plot_df.index, plot_df[var], rotation = 90)

            ax.bar(plot_df.index, plot_df['perc'], align = 'center', color = 'lightgrey')

            ax2 = ax.twinx()
            ax2 = sns.pointplot(data = tmp, x=var, y='target_1', order = cat_order, color='black')

            ax.axhline(y=rare_tol, color = 'red')
            ax.axhline(y=rare_tol+5, color = 'darkred')

            ax.set_title(f'Event rate of target ({target}) across all categories of variable ({var})', fontsize=17)
            #ax.set_xlabel(var, fontsize=14)
            ax.set_ylabel('Perc of Categories', fontsize=14)
            ax2.set_ylabel("Perc of Events across all Categories", fontsize=14)

            plt.show()


        # Graph:2 to show the mean target value within each category
        fig, ax = plt.subplots(figsize=(12,4))
        plt.xticks(plot_df.index, plot_df[var], rotation = 90)

        ax.bar(plot_df.index, plot_df['perc'], align = 'center', color = 'lightgrey')

        ax2 = ax.twinx()
        ax2 = sns.pointplot(data = plot_df, x=var, y=target, order = cat_order, color='green')

        ax.axhline(y=rare_tol, color = 'red')
        ax.axhline(y=rare_tol+5, color = 'darkred')


        if model in('clf' or 'classification'):
            ax.set_title(f'Event Rate of target ({target}) within each category of variable ({var})', fontsize=17)
            ax2.set_ylabel("Perc of Events within Category", fontsize=14)
            #ax.set_xlabel(var, fontsize=14)
            ax.set_ylabel('Perc of Categories', fontsize=14)

        elif model in('reg' or 'regression'):
            ax.set_title(f'Mean value of target ({target}) within each category of variable ({var})', fontsize=17)
            ax2.set_ylabel('Mean Target Value', fontsize=14) 
            #ax.set_xlabel(var, fontsize=14)
            ax.set_ylabel('Perc of Categories', fontsize=14)

        plt.show()

        display_all(plot_df.set_index(var).transpose())

        


def  categorical_plots_with_rare_and_target(df, variables, target, model = 'clf', add_missing = True, rare_v1=5, rare_v2=10):
    """
    Useful for deciding what percentage of rare encoding would be useful
    Parameters:
    -----------
        df : Dataframe for which Analysis to be performed
        variables : input type list. All the categorical variables needed for plotting
        target : Target variable
        model : type of problem - classification or regression
                For classification related analysis. use 'classification' or 'clf'
                For regression related analysis. use 'regression' or 'reg'
        add_missing : default True. if True it will replace missing values by 'Missing'
        rare_v1 : Input percentage as number ex 5, 10 etc (default : 5) combines categories less than that and show distribution
        rare_v2 : Input percentage as number ex 5, 10 etc (default : 10) combines categories less than that and show distribution
       
    Returns:
    --------
        Category plots for all the variables
    """
    eda_df = df.copy(deep=True)
    length_df = len(eda_df)


    for i, var in enumerate(variables, 1):

        print (f'{i}. Plot for {var}')

        if add_missing:
            eda_df[var] = eda_df[var].fillna('Missing')

        
        # 1st plot for categories as in in the dataset        

        plot_df =  calculate_mean_target_per_category (eda_df, var, target)
        cat_order = list(plot_df[var])

        if model in('clf' or 'classification'):
            plot_df[target] = 100*plot_df[target]


        fig, ax = plt.subplots(figsize=(12,4))
        plt.xticks(plot_df.index, plot_df[var], rotation = 90)

        ax.bar(plot_df.index, plot_df['perc'], align = 'center', color = 'lightgrey')

        ax2 = ax.twinx()
        ax2 = sns.pointplot(data = plot_df, x=var, y=target, order = cat_order, color='green')

        ax.set_title(f'As Is Distribution of {var}', fontsize=17)
        #ax.set_xlabel(var, fontsize=14)
        ax.set_ylabel('Perc of Categories', fontsize=14)

        ax.axhline(y=rare_v1, color = 'red')
        ax.axhline(y=rare_v2, color = 'darkred')

        if model in('clf' or 'classification'):
            ax2.set_ylabel("Perc of Events within Category", fontsize=14)

        elif model in('reg' or 'regression'):
            ax2.set_ylabel('Mean Target Value', fontsize=14) 

        plt.show()
        display_all(plot_df.set_index(var).transpose())
        print()

        # 2nd plot after combining categories less than 5%    
        if rare_v1:
            rare_v1_df = eda_df.copy()[[var, target]]
            s_v1 = pd.Series(rare_v1_df[var].value_counts() / length_df)
            s_v1.sort_values(ascending = False, inplace = True)
            non_rare_label = [ix for ix, perc in s_v1.items() if perc>rare_v1/100]
            rare_v1_df[var] = np.where(rare_v1_df[var].isin(non_rare_label), rare_v1_df[var], 'Rare')

            plot_df_v1 =  calculate_mean_target_per_category (rare_v1_df, var, target)
            cat_order = list(plot_df_v1[var])

            if model in('clf' or 'classification'):
                plot_df_v1[target] = 100*plot_df_v1[target]

            fig, ax = plt.subplots(figsize=(12,4))
            plt.xticks(plot_df_v1.index, plot_df_v1[var], rotation = 90)

            ax.bar(plot_df_v1.index, plot_df_v1['perc'], align = 'center', color = 'lightgrey')

            ax2 = ax.twinx()
            ax2 = sns.pointplot(data = plot_df_v1, x=var, y=target, order = cat_order, color='green')

            ax.set_title(f'Distribution of {var} after combining categories less than {rare_v1}%', fontsize=17)
            #ax.set_xlabel(var, fontsize=14)
            ax.set_ylabel('Perc of Categories', fontsize=14)

            ax.axhline(y=rare_v1, color = 'red')
            ax.axhline(y=rare_v2, color = 'darkred')

            if model in('clf' or 'classification'):
                ax2.set_ylabel("Perc of Events within Category", fontsize=14)

            elif model in('reg' or 'regression'):
                ax2.set_ylabel('Mean Target Value', fontsize=14) 

            plt.show()
            display_all(plot_df_v1.set_index(var).transpose())
            print()


        # 3rd plot after combining categories less than 10%  
        if rare_v2:
            rare_v2_df = eda_df.copy()[[var, target]]
            s_v2 = pd.Series(rare_v2_df[var].value_counts() / length_df)
            s_v2.sort_values(ascending = False, inplace = True)
            non_rare_label = [ix for ix, perc in s_v2.items() if perc>rare_v2/100]
            rare_v2_df[var] = np.where(rare_v2_df[var].isin(non_rare_label), rare_v2_df[var], 'Rare')

            plot_df_v2 =  calculate_mean_target_per_category (rare_v2_df, var, target)
            cat_order = list(plot_df_v2[var])

            if model in('clf' or 'classification'):
                plot_df_v2[target] = 100*plot_df_v2[target]

            fig, ax = plt.subplots(figsize=(12,4))
            plt.xticks(plot_df_v2.index, plot_df_v2[var], rotation = 90)

            ax.bar(plot_df_v2.index, plot_df_v2['perc'], align = 'center', color = 'lightgrey')

            ax2 = ax.twinx()
            ax2 = sns.pointplot(data = plot_df_v2, x=var, y=target, order = cat_order, color='green')

            ax.set_title(f'Distribution of {var} after combining categories less than {rare_v2}%', fontsize=17)
            #ax.set_xlabel(var, fontsize=14)
            ax.set_ylabel('Perc of Categories', fontsize=14)

            ax.axhline(y=rare_v1, color = 'red')
            ax.axhline(y=rare_v2, color = 'darkred')

            if model in('clf' or 'classification'):
                ax2.set_ylabel("Perc of Events within Category", fontsize=14)

            elif model in('reg' or 'regression'):
                ax2.set_ylabel('Mean Target Value', fontsize=14) 

            plt.show()
            display_all(plot_df_v2.set_index(var).transpose())



def  categorical_plots_for_miss_and_freq(df, variables, target, model = 'reg'):
    """
    Useful ONLY for Regression Model
    Plots the KDE to check whether frequent category imputation will be suitable

    Parameters:
    -----------
        df : Dataframe for which Analysis to be performed
        variables : input type list. All the categorical variables needed for plotting
        target : Target variable
        model : type of problem - classification or regression
                For classification related analysis. use 'classification' or 'clf'
                For regression related analysis. use 'regression' or 'reg'
        
    Returns:
    --------
        Missing Values for  variable
        Frequent Category for variable
        KDE plot between missing values and frequent category
        
    """
    miss_df = df.copy()

    if model in ('reg' , 'regression'):
        for i, var in enumerate(variables, 1):

            print (f'{i}. Plot for {var}')

            print ('Missing Values:')
            n_miss = miss_df[var].isnull().sum()
            n_miss_perc = miss_df[var].isnull().mean()*100
            print ('  Number :', n_miss)
            print ('  Percentage : {:1.2f}%'.format(n_miss_perc))
            
            if n_miss>10:
                fig = plt.figure(figsize = (12,4))
                ax = fig.add_subplot(111)

                value = miss_df[var].mode()
                # Careful : because some variable can have multiple modes
                if len(value) ==1:
                    print ('\n\nMost Frequent Category: ', value[0])
                    value = value[0]
                else:
                    raise ValueError(f'Variable {var} contains multiple frequent categories :', value)

                

                # Frequent Category
                miss_df[miss_df[var] == value][target].plot(kind = 'kde', ax = ax, color = 'blue')

                # NA Value
                miss_df[miss_df[var].isnull()][target].plot(kind = 'kde', ax = ax, color = 'red')

                # Add the legend
                labels = ['Most Frequent category', 'with NA']
                ax.legend(labels, loc = 'best')
                ax.set_title('KDE Plot for Frequent Category & Missing Values', fontsize=17)
                ax.set_xlabel('Distribution' , fontsize=14)
                ax.set_ylabel('Density', fontsize=14)
                plt.show()
            else:
                print ('Not plotting the KDE plot because number of missing values is less than 10')
                print()

    else:
        print ('ONLY suitable for Regression Models')


def categorical_variable_detail(df, variable, model = None, target=None,  rare_tol=5):
    """
    This function provides EDA for Categorical variable, this includes 
        - Counts
        - Cardinality, number of Categories in each Varaible
        - Missing values counts and percentages
       
    Also Category wise basic plots will be generated for the given variable 
        - Plot Categories
        - Plot Categories by including Missing Values
        - Plot categories by combining Rare label
        - Plot categories with target
        - Plot distribution of target variable for each categories (If Target Variable is passed)
   
    Parameters :
    ----------- 
        df : Dataframe for which Analysis to be performed
        variable: Pass the variable for which EDA is required
        model : type of problem - classification or regression
            For classification related analysis. use 'classification' or 'clf'
            For regression related analysis. use 'regression' or 'reg'
        target : Define the target variable, if you want to see the relationship between given list of varaible with Target variable, default None
        rare_tol : Threshold limit to combine the rare occurrence categories, (rare_tol=5) i.e., less than 5% occurance categories will be grouped and forms a rare category   
            
        
     Return :
     -------
     
     Returns summary & plots of given variable
    """
    eda_df = df.copy(deep=True)
    c = variable
    s = eda_df[c]
    
    # 1. Basic Statistics
    printmd ('**<u>Basic Info :</u>**')
    print ('Total Number of observations : ', len(s))
    print ()
    
    # 2. Cardinality
    printmd ('**<u>Cardinality of the variable :</u>**')
    print ('Number of Distinct Categories (Cardinality): ', len(s.unique()))
    if s.nunique()>100:
        print('Few of the values : ', s.unique()[0:50])
        print ()
    else:
        print ('Distinct Values : ', s.unique())
        print ()
    
    
    # 3. Missing Values

    printmd ('**<u>Missing Values :</u>**')
    
    nmiss = s.isnull().sum()
    print ('  Number :', s.isnull().sum())
    print ('  Percentage :', s.isnull().mean()*100, '%')

    # 4. Plot Categories
    
    printmd ('**<u>Category Plots :</u>**')
    plot_categories(eda_df, c)

    # 5. Plot Categories by including Missing Values
    
    if nmiss:
        printmd ('**<u>Category plot by including Missing Values**')
        plot_categories(eda_df, c, add_missing = True, add_rare = False, rare_tol = rare_tol)
        
    # 6. Plot categories by combining Rare label
    
    printmd ('**<u>Category plot by including missing (if any) and Rare labels**')
    print (f'Categories less than {rare_tol} value are clubbed in Rare label')
    plot_categories(eda_df, c, add_missing = True, add_rare = True, rare_tol = rare_tol)
    
    #7. Plot categories with target
    
    if target:
        printmd ('**<u>Category Plot and Mean Target value:</u>**')
        plot_categories_with_target(eda_df, c, target, rare_tol)
           

   #8. Plot distribution of target variable for each categories

    if target:
        if model == 'regression' or model == 'reg' :
            
            printmd ('**<u>Distribution of Target variable for all categories:</u>**')
            plot_target_with_categories(eda_df, c, target)
           
    
        
    