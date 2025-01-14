import pandas as pd
import numpy as np
import math
import scipy.stats as stats
from matplotlib import pyplot as pl
import csv
from sklearn.decomposition import PCA
from matplotlib import pyplot as pl
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from statistics import mode




#AT THE MOMENT THE FIRST COLOUMN CONTAINS LETTER SO REMOVE IT
#MAYBE THIS NEEDS TO BE CHANGED LATER

#THE FUNCTION CALCULATES A VALUE BETWEEN [0,1] FOR EVERY INDEPENDANT VARIABLE Xi, THE VALUE OF THE DEPENDANT VARIABLE Y IS NOT IN THE OUTPUT 
#THE INDEPENDANT VARIABLE SHOULD ALWAYS BE IN THE LAST COLLUMN!!!!
#FOR THE CALCULATION OF THE VALUE FOR EVERY VARIABLE Xi WHICH HAS A HIGH CORRELATION WITH ANOTHER VARIABLE Xj -
#THE FORUMULAR IS |corXiY| - |corXiXj|/weight
#SO MAKE SURE TO TAKE THE RIGHT WEIGHT

def correlationPValues(data, weight):
    
    idToName = {}
    
    data = data.iloc[:,1:]
    names = data.columns
    
    for i in range(0,len(names) - 1):
        idToName[i] = names[i]
    
    corMatrix = data.corr()
    corMatrix = corMatrix.values
    print(corMatrix)
    
    for i in range(corMatrix.shape[0]):
        for j in range(corMatrix.shape[1]):
            if math.isnan(corMatrix[i][j]):
                corMatrix[i][j] = 0
    
    #get correlation from every independant variable with label
    correlationValues = corMatrix[data.shape[1] - 1]
    correlationWithLabel = corMatrix[data.shape[1] - 1]
    bestAttributes = []
    
    #add index of label to eliminatedAttributes
    eliminatedAttributes = [len(correlationValues)-1]

    variableToPValue = {}
    while(True):
        #get the highest correlation
        maxCor = -10
        bestAttribute = 0
        for i in range(0, len(correlationValues)):
            if i not in bestAttributes and i not in eliminatedAttributes:
                if correlationValues[i] > maxCor:
                    maxCor = correlationValues[i]
                    bestAttribute = i
                    
        variableToPValue[bestAttribute] = maxCor     
        #Add best index to best attributes
        bestAttributes.append(bestAttribute)
        #get correlation from every independant variable with best Attribute
        correlationWithBestAttribute = corMatrix.T[bestAttribute]

        #iterate through correlation and eliminate every variable with cor >= 0.7
        count = 0
        for i in range(0, len(correlationWithBestAttribute)):
            if not(i in bestAttributes or i in eliminatedAttributes):
                if correlationWithBestAttribute[i] >= 0.7:
                    count = count + 1
                    eliminatedAttributes.append(i)
                    variableToPValue[i] = np.maximum(np.abs(correlationWithLabel[i]) - np.abs(correlationWithBestAttribute[i])/weight, 0)

        if(len(correlationValues) == len(eliminatedAttributes) + len(bestAttributes)):
            break;
        
        #convert dictionary from id to name
        newDictionary = {}
        for i in variableToPValue.keys():
            newDictionary[idToName[i]] = np.abs(variableToPValue[i])
            print(str(i) + "  " + idToName[i])
    return newDictionary


import scipy.stats as stats
def Wilcoxon(big_data,col_name):
    col = big_data[col_name]
    labels = big_data[big_data.columns.values[len(big_data.T) -1]]
    ill = []
    healthy = []
    for i in range(len(col)):
        if labels[i] == 1:
            ill.append(col[i])
        else:
            healthy.append(col[i])
    #ill = [col[i] for i in range(len(col)) if labels[i] == 1 ]
    #healthy = [col[i] for i in range(len(col)) if labels[i] == 0 ]
    U = 0
    for i in ill:
        for h in healthy:
            if i < h:
                U += 1
            if i == h:
                U += 0.5
    n = len(ill)
    m = len(healthy)
    pvalue = stats.norm(loc = (n*m)/2 , scale = ((n*m)*(n+m+1)/12)**0.5).cdf(U)
    if pvalue > 0.5:
        pvalue = 1 - pvalue
    return pvalue


def wilxocon_for_all(data):
    col_names = data.columns.values[1:len(data.T)-1]
    dict = {}
    for name in col_names:
        dict[name] = Wilcoxon(data, name)
    return dict
    
    
#Calculates the cols to be deleted from the combination of Median and Covarianz filter
#please ensure to give two Dictionary with same size and no missing values...gaaarkein bock auf edge cases abfangen
def Efs(FilterMedian,FilterCov):

    #1. Calculate the importance values for the columns in Median

    minP = min(FilterMedian.values())
    medianImp = {}
    for col in FilterMedian.keys():
        impVal = 1 - FilterMedian[col] + minP
        medianImp[col] = impVal


    #2. Calculate the importance values for the columns in Cov

    maxBetha = max(FilterCov.values())
    covImp = {}
    for col in FilterCov.keys():
        impVal = FilterCov[col] / maxBetha
        covImp[col] = impVal


    #3. Combine the impVals
    combinedImp = {}
    for col in FilterMedian:
        combinedImp[col] = FilterMedian[col] + FilterCov[col]

    #4. Calculate the Cols to be deleted
    toDelete = []
    impMean = sum(combinedImp.values())/len(combinedImp)
    for col in combinedImp:
        if(combinedImp[col] <= impMean):
            toDelete.append(col)

    return toDelete


def minmaxNormalize(df):

    if not df.isnull().values.any() :

        for i in range(0,df.columns.size):

            max = df.iloc[:,i].max()
            min = df.iloc[:,i].min()
            for j in range(0, df.iloc[:,i].size):

                    if not max-min == 0:
                        df.iloc[j,i] = (df.iloc[j,i] - min) / (max - min)
            print(df.iloc[:,i])
    else:
        print("contains null")

    return df

def stdNormalize(df):

    for col in df.columns[0:-1]:
        print(col)
        colMean = df[col].mean()
        colSTD = np.std(df[col])
        #print(df[col, 0])
        for i in range(len(df[col])):
            #copy = df[col][i]
            df[col][i] = (df[col][i] - colMean)/colSTD
    return df

def stdNormalize2(df):

    print(df)

    normalized_df = df.copy

    normalized_df[1:-1] = (df[1:-1]-df[1:-1].mean()) / df[1:-1].std()

    print(normalized_df)
    return normalized_df

def createMetricsMatrix(df):
    metrics = []
    header = df.columns.values[1:]
    metrics.append(header)
    #meanMatrix = np.zeros((len(header)+1, len(header)))
    # header dataframes.columns.values[1:]
    metrics.append([])
    metrics.append([])
    #metrics.append([])
    for i in range(1, df.shape[1]-1):
        column = df.iloc[:,i].values
        metrics[1].append(np.mean(column))
        #meanMatrix[i-1,j-1] = np.mean(df.iloc[:,i].values)
        metrics[2].append(np.std(column))
        #metrics[3].append((metrics[2][i-1] / metrics[1][i-1])/len(column)**0.5)

    return metrics

def getIndicesWithLowByMeanThreshhold(df, threshhold):
    header = df.columns.values[1:-1]
    df_new = df.copy()
    for i in range(1, df.shape[1]-1):
        column = df.iloc[:,i].values
        if np.mean(column) < threshhold:
            df_new = df_new.drop(columns=header[i-1])
    return df_new

def boxplotHealthyAndSick(df):
    df_healthy = df[(df.label == 0)]
    df_sick = df[(df.label == 1)]

    pl.figure(1)
    df_healthy.boxplot()
    pl.figure(2)
    df_sick.boxplot()

def pca(df, n=2):
    '''
    Creates a PCA of the data in the dataframe. This method will remove the label column,
    but expects, that the sample_ID column is already removed from the df. For 2D data,
    (n=2), the PCA is plottet.
    :param df: df without sample_ID but labels column
    :return: Dataframe of the PCA with n compoments
    '''
    df_tmp = df.copy()
    pca = PCA(n_components=n)
    header = df_tmp.columns.values[1:]
    df_withoutLabels = df_tmp.drop(columns=header[-1])

    principalComponents = pca.fit_transform(df_withoutLabels.values)
    df_principal_components = pd.DataFrame(principalComponents)
    df_principal_components['label'] = df.iloc[:,-1].values
    if(n == 2):
        df_pc_healthy = df_principal_components[(df_principal_components.label == 0)]
        df_pc_T2D = df_principal_components[(df_principal_components.label == 1)]
        df_pc_IBD = df_principal_components[(df_principal_components.label == 2)]
        df_pc_CAD = df_principal_components[(df_principal_components.label == 3)]
        df_pc_CKD = df_principal_components[(df_principal_components.label == 4)]
        df_pc_healthy = df_pc_healthy.drop(columns=header[-1])
        df_pc_T2D = df_pc_T2D.drop(columns=header[-1])
        df_pc_IBD = df_pc_IBD.drop(columns=header[-1])
        df_pc_CAD = df_pc_CAD.drop(columns=header[-1])
        df_pc_CKD = df_pc_CKD.drop(columns=header[-1])

        pl.figure(3)
        pl.scatter(np.array(df_pc_healthy.values[0:, 0]), np.array(df_pc_healthy.values[0:, 1]))
        pl.scatter(np.array(df_pc_T2D.values[0:, 0]), np.array(df_pc_T2D.values[0:, 1]))
        pl.scatter(np.array(df_pc_IBD.values[0:, 0]), np.array(df_pc_IBD.values[0:, 1]))
        pl.scatter(np.array(df_pc_CAD.values[0:, 0]), np.array(df_pc_CAD.values[0:, 1]))
        pl.scatter(np.array(df_pc_CKD.values[0:, 0]), np.array(df_pc_CKD.values[0:, 1]))
        #pl.show()

    return df_principal_components

def clustering(df, eps=0.5, printCluster=False):
    '''
    Clusters the data of a df with DBSCAN. Data is normalized before clustering
    :param df:
    :param eps: The distance for clustering (Distance should fit with the normalized data)
    :param printCluster: Prints the clustering, set only true for 2D-daata
    :return:
    '''
    df_tmp = df.copy()
    header = df_tmp.columns.values[1:]
    df_n = StandardScaler().fit_transform(df_tmp.drop(columns=header[-1]).values)
    clustering = DBSCAN(eps=eps, min_samples=2).fit(df_n)
    labels = df.iloc[:,-1].values

    df_tmp = pd.DataFrame(df_n)
    df_tmp['cluster'] = clustering.labels_
    clusterDf = []
    for i in set(clustering.labels_):
        clusterDf.append(df_tmp[(df_tmp.cluster == i)])

    if(printCluster):
        pl.figure(4)
        header = df_tmp.columns.values[1:]
        for cDf in clusterDf:
            cDf_tmp = cDf.drop(columns=header[-1]).values
            pl.scatter(np.array(cDf_tmp[0:, 0]), np.array(cDf_tmp[0:, 1]))

    return clustering.labels_

def removeNoise(df, clusterLabels, keepMainCluster=True):
    '''
    Given a dataframe and a set of clusters, this method will remove all samples with a
    certain cluster.
    :param df: dataframe
    :param clusterLabels: The cluster labels of the samples
    :param keepMainCluster: If false, only samples with the cluster label noise will be removed
    (this means they have eps radius without neighbor). If true only the elements of the main
    cluster are kept.
    :return:
    '''
    df['cluster'] = clusterLabels
    if(keepMainCluster):
        df = df[(df.cluster != -1)]
    else:
        mainCluster = mode(clusterLabels)
        df = df[(df.cluster == mainCluster)]
    df = df.reset_index(drop=True)
    return df.drop(columns='cluster')

def reduceData(df):
    '''
    Removes data, which consists mainly of 0 entries as samples which are considered as outliers.
    :param df:
    :return:
    '''
    df_red = getIndicesWithLowByMeanThreshhold(df, 3)
    df_pca = pca(df_red.iloc[0:, 1:])
    clusterLabels = clustering(df_pca)
    df_reduced = removeNoise(df_red, clusterLabels, False)
    return df_reduced


def unionMatrix(level, meanFill = False):
    """
    Labels will be:
    0 - patient is healthy
    1 - patient has T2D
    2 - patient has IBD
    3 - patient has CAD
    4 - patient has CKD
    NOTE: meanFill seems to be useless, because all bacteria, which aren't in all disease-excels
    seem to be always 0 for all patients, so meanFill = True will produce the same result
    as meanFill = False, which is faster to calculate.
    :param level: Level, from which the union is created e.g. 'Class' or 'Species'
    :param meanFill: meanFill is now useless, after an intersection of bacteria should be used not
    the union
    :return: A pandas dataframe of all patients and bacteria
    """
    dataframes = []
    diseases = ['T2D', 'IBD', 'CAD', 'CKD']
    for i in diseases:
        df = pd.read_csv('../HackathonMicrobiomeData/' + i + '/' + level + i + '_train.csv')
        dataframes.append(df)

    unionHeader = []
    unionSamples = []

    for df in dataframes:
        unionHeader = set(unionHeader) | set(df.columns.values)
        unionSamples = set(unionSamples) | set(df.iloc[:,0])

    intersection_header = unionHeader
    for df in dataframes:
        intersection_header = set(intersection_header) & set(df.columns.values)

    tmp = []
    intersection_header.remove('sample_ID')
    intersection_header.remove('label')
    intersection_header = list(intersection_header)
    intersection_header.sort()
    unionSamples = list(unionSamples)
    unionSamples.sort()
    i = 0
    for sample in unionSamples:
        # Add sample as first element in the list
        tmp.append([sample])
        for header in intersection_header:
            data_found = False
            label = 0
            j = 1
            for df in dataframes:
                cell = []
                if header in df.columns:
                    row = df[(df.sample_ID == sample)]
                    cell = row[header].values
                    label_tmp = row['label'].values
                    if len(cell) != 0:
                        tmp[i].append(cell[0])
                        label = label_tmp
                        if label != 0:
                            label = [j];
                        data_found = True
                        break
                j = j + 1
            if not data_found:
                if meanFill:
                    for df in dataframes:
                        if header in df.columns:
                            df_tmp = df[(df.label == 0)]
                            h_mean = np.mean(df_tmp[header])
                            tmp[i].append(h_mean)
                            break
                else:
                    tmp[i].append(0)
        tmp[i].append(label[0])
        i = i + 1


    intersection_header.insert(0, 'sample_ID')
    intersection_header.append('label')
    df_union = pd.DataFrame(data=tmp, columns=intersection_header)
    df_union.to_csv('unionMatrix_' + level + '.csv', index=False)

    return df_union

def treeBasedFeatureSelection(df):
    from sklearn.ensemble import ExtraTreesClassifier
    from sklearn.feature_selection import SelectFromModel

    print(df)
    print(df.size)

    df.drop(df.columns[0], axis = 1, inplace=True)

    print(df)
    print(df.size)

    Y = np.array(df[["label"]]).ravel()
    X = df.drop(["label"], axis = 1)
    clf = ExtraTreesClassifier(n_estimators=50)
    clf = clf.fit(X, Y)
    #print(clf.feature_importances_)
    model = SelectFromModel(clf, prefit=True)
    X_new = model.transform(X)
    #print(model.get_feature_names_out())
    #print(model.get_support())
    selected_features = model.get_support()
    selected_features = selected_features.tolist()
    #selected_features.insert(0, True)
    selected_features.append(True)
    #print(selected_features)
    column_indices = []
    # Iterate over the list
    for i, item in enumerate(selected_features):
    # If the item is True, append its index to the list
        if item:
            column_indices.append(i)

    #print('New shape', X_new.shape)
    X_new = np.concatenate((X_new, Y.reshape(-1, 1)), axis=1)
    #X_new = np.concatenate((df["sample_ID"].values.reshape(-1, 1), axis=1))
    #df_new = pd.DataFrame(data=X_new, columns=df.columns[])+
    #print(column_indices)
    #print(df.columns[column_indices])
    selected_features = df.columns[column_indices]
    df_new = df[selected_features]
    return df_new

def overSampling(df):
    from imblearn.over_sampling import SMOTE

    oversample = SMOTE()

    X = df[df.columns[1:-1]].values
    y = df[df.columns[-1]]
    X, y = oversample.fit_resample(X, y)

    df_new = pd.DataFrame(X, columns=df.columns[1:-1])
    df_new['label'] = y
    return df_new



def pipeline():
    level = 'genus'
    #'../Hackathon_Microbiome_Train_Combined/Train_Combined/train_combined_Class.csv'
    #df = unionMatrix(level)
    #print('union', df.shape)

    # Use alternatively the tree based feature selection, or the reduce data method (remove outliers ond zero columns)
    #df = reduceData(df)
    #print('reducedUnion', df.shape)

    #pca(df.drop(columns=df.columns.values[0]))

    df = pd.read_csv('../Hackathon_Microbiome_Train_Combined/Train_Combined/train_combined_Genus.csv')

    df = treeBasedFeatureSelection(df)

    df.to_csv('DataMatrices/' + level + '/unionMatrix_TreeBasedClassifier_' + level + '.csv', index=False)

    df = stdNormalize(df)

    df.to_csv('DataMatrices/' + level + '/unionMatrix_TreeBasedClassifier_Normalized_' + level + '.csv', index=False)

    #df = overSampling(df)

    # SMOTE matrix does not have sample_ID anymore
    #df.to_csv('DataMatrices/' + level + '/unionMatrix_TreeBasedClassifier_Normalized_SMOTE_' + level + '.csv', index=False)

    #df = df.drop(columns=df.columns.values[0])
    #df.to_csv('unionMatrix_TreeBasedClassifier_Normalized_withoutSampleID_' + level + '.csv', index=False)



if __name__ == "__main__":
    pipeline()


