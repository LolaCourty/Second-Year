##############################
######     Setup        ######
##############################


# Load libraries
import pandas as pd
from pandas import read_csv
from pandas.plotting import scatter_matrix
from matplotlib import pyplot
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

try:
	#try to pass the name of the database as an argument when running the script
	#this only works, if there is one big database (at the moment)
	data_file_1 = str(sys.argv[1])
except:
	#manually entering the database names
	data_file_1 = 'alphabet_button_Raw.txt'
	data_file_2 = 'alphabet_final_Raw.txt'
#print('loading data from', data_file)

try:
	#name of the finished AI model can be passed as an argument
	model_file = str(sys.argv[2])
except:
	#name of the finished AI model, added by hand
	#one has to choose only one model (in this version)
	model_file = 'model_both_raw_KNN.sav'
print('Finished model will be stored in', model_file)

#alternative way to load a database
#data = pickle.load(open(data_file, 'rb'))
#dataset = pd.DataFrame(data)





##############################
######   Load Database  ######
##############################

#The database doesn't include names for the individual variables, neither the number of variables measured.
#This code reads the first line of the database in order to determine the length of one line (all lines should have the
#same number of variables).
with open(data_file_1) as f:
	lines = f.read()
	first = lines.split('\n', 1)[0]
	first_list = first.split(', ')

#print(first)
#print(first_list)

#enumerating the variables, the letter/word to be determines is marked as "class"
name = [str(i) for i in range(len(first_list))]
name[0] = "class"

#print(name)


#Load the databases into a pandas dataframe. Here, two different databases are combined
dataset1 = read_csv(data_file_1, index_col = False, names=name)
dataset2 = read_csv(data_file_2, index_col = False, names=name)
dataset = dataset1.append(dataset2)
#dataset = dataset2


#ERROR CORRECTION
#The databases sometimes include corrupted lines. Here, you find commented code to possibly find those lines and correct
#or erase them.

#dataset = dataset.iloc[:65]
#dataset = dataset.drop(labels=135, axis=0)
dataset = dataset.fillna('?')

#count_nan_in_df = dataset.isnull().sum().sum()
#print ('Count of NaN: ' + str(count_nan_in_df))
#dataset['full_count'] = dataset.apply(lambda x: x.count(), axis=1)

pd.set_option('display.max_rows', dataset.shape[0]+5)
#print(dataset['full_count'])
#print(dataset.iloc[135])
#dataset.loc[dataset['class'] == 'WW']['class'] = 'W'
dataset['class'] = dataset['class'].replace(['WW'],'W')

dataset = dataset[dataset["class"] != '?']

'''
#Code proposition for data postprocessing. Here, certain columns were erased.
indexes = [str(i%5 + 14 * (i//5)+1) for i in range(0, 20*5)]
dataset = dataset.drop(columns = indexes)
indexes2 = [str(i%3 + 14 * (i//3)+12) for i in range(0, 20*5)]
print(indexes2)
dataset = dataset.drop(columns = indexes2)
'''



##############################
######  Visualization   ######
##############################
# shape
print(dataset.shape)

# head
print(dataset.head(20))

# descriptions
print(dataset.describe())

# class distribution
print(dataset.groupby('class').size())

# box and whisker plots
# dataset.plot(kind='box', subplots=True, layout=(2,2), sharex=False, sharey=False)
# pyplot.show()

# histograms
# dataset.hist()
# pyplot.show()

# scatter plot matrix
# scatter_matrix(dataset)
# pyplot.show()


##############################
######     Learning     ######
##############################
#The database is split into training and validation data. The training data are used to train different models.
#The prefered model can be selected and will be saved and visualized.

# Split-out validation dataset
array = dataset.values
X = array[:,1:]
y = array[:,0]
X_train, X_validation, Y_train, Y_validation = train_test_split(X, y, test_size=0.20, random_state=1)

# Spot Check Algorithms
models = []
models.append(('LR', LogisticRegression(solver='liblinear', multi_class='ovr')))
models.append(('LDA', LinearDiscriminantAnalysis()))
models.append(('KNN', KNeighborsClassifier()))
models.append(('CART', DecisionTreeClassifier()))
models.append(('NB', GaussianNB()))
models.append(('SVM', SVC(gamma='auto')))

# evaluate each model in turn
results = []
names = []
for name, model in models:
	kfold = StratifiedKFold(n_splits=3, random_state=1, shuffle=True)
	cv_results = cross_val_score(model, X_train, Y_train, cv=kfold, scoring='accuracy')
	results.append(cv_results)
	names.append(name)
	print('%s: %f (%f)' % (name, cv_results.mean(), cv_results.std()))


# Compare Algorithms
pyplot.boxplot(results, labels=names)
pyplot.title('Algorithm Comparison')
pyplot.show()


# Fitting best model, to be chosen manually
model = KNeighborsClassifier()
model.fit(X, y)

# save the model to disk
pickle.dump(model, open(model_file, 'wb'))

# testing on validation dataset
predictions = model.predict(X_validation)
print(predictions)
print(accuracy_score(Y_validation, predictions))
print(confusion_matrix(Y_validation, predictions))
print(classification_report(Y_validation, predictions))

#visualisation of the confusion matrix
ax = sns.heatmap(confusion_matrix(Y_validation, predictions), annot=True, cmap='Blues')

ax.set_title('Seaborn Confusion Matrix with labels\n\n');
ax.set_xlabel('\nPredicted Values')
ax.set_ylabel('Actual Values ');

## Ticket labels - showing the letters on the axes
# ax.xaxis.set_ticklabels(['1', '3', '5', 'A','C', 'E','G','I','L', 'N', 'P', 'R', 'T', 'V', 'X'])
# ax.yaxis.set_ticklabels(['1', '3', '5', 'A','C', 'E','G','I','L', 'N', 'P', 'R', 'T', 'V', 'X'])

## Display the visualization of the Confusion Matrix.
plt.show()
