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
from joblib import dump, load

model_restricted_names= []
modelnames = []
models = []
models_restricted = []
modelnames_trait = []
models_trait = []

modelnames.append('models/model_both_raw_GaussianNB.sav')
modelnames.append('models/model_both_raw_KNN.sav')
modelnames.append('models/model_both_raw_LDA.sav')
modelnames.append('models/model_both_raw_Tree.sav')
modelnames.append('models/model_final_raw_GaussianNB.sav')
modelnames.append('models/model_final_raw_KNN.sav')
modelnames.append('models/model_final_raw_LDA.sav')
modelnames.append('models/model_final_raw_Tree.sav')
modelnames.append('models/model_button_raw_GaussianNB.sav')
modelnames.append('models/model_button_raw_KNN.sav')
modelnames.append('models/model_button_raw_LDA.sav')
model_restricted_names.append('models/model_button_raw_restricted_GaussianNB.sav')
model_restricted_names.append('models/model_button_raw_restricted_KNN.sav')
model_restricted_names.append('models/model_button_raw_restricted_LDA.sav')
modelnames_trait.append('model_button_GaussianNB.sav')
modelnames_trait.append('model_button_LDA.sav')
modelnames_trait.append('model_button_KNN.sav')
modelnames_trait.append('model_both_GaussianNB.sav')
modelnames_trait.append('model_both_LDA.sav')
modelnames_trait.append('model_both_KNN.sav')

data_file_1 = 'compare_models_Raw.txt'
#data_file_1 = 'alphabet_button_Raw.txt'
data_file_2 = 'compare_models.txt'

with open(data_file_1) as f:
	lines = f.read()
	first = lines.split('\n', 1)[0]
	first_list = first.split(', ')

name = [str(i) for i in range(len(first_list))]
name[0] = "class"


dataset = read_csv(data_file_1, index_col = False, names=name)

with open(data_file_2) as f:
	lines = f.read()
	first = lines.split('\n', 1)[0]
	first_list = first.split(', ')

print(first)
print(first_list)
names = [str(i) for i in range(len(first_list))]
names[0] = "class"


dataset_trait = read_csv(data_file_2, index_col = False, names=names)

for i in range(len(modelnames)):
	print('loading model from', modelnames[i])
	models.append(load(modelnames[i]))

for i in range(len(model_restricted_names)):
	print('loading model from', model_restricted_names[i])
	models_restricted.append(load(model_restricted_names[i]))

for i in range(len(modelnames_trait)):
	print('loading model from', modelnames_trait[i])
	models_trait.append(load(modelnames_trait[i]))


indexes = [str(i%5 + 14 * (i//5)+1) for i in range(0, 20*5)]
dataset_restricted = dataset.drop(columns = indexes)
indexes2 = [str(i%3 + 14 * (i//3)+12) for i in range(0, 20*5)]
dataset_restricted = dataset_restricted.drop(columns = indexes2)

# shape
print(dataset_trait.shape)

# head
print(dataset_trait.head(20))

print(dataset_trait.groupby('class').size())
print(dataset.groupby('class').size())

# Split-out validation dataset
array = dataset.values
X = array[:,1:]
y = array[:,0]
array2 = dataset_restricted.values
X_r = array2[:,1:]
y_r = array2[:,0]
array3 = dataset_trait.values
X_t = array3[:,1:]
y_t = array3[:,0]
print(y)
predictions = []
predictions_restricted = []
predictions_trait = []

for j in range(len(models)):
	prediction = models[j].predict(X)
	predictions.append(prediction)
	print('model:', modelnames[j] ,'Last predicted character:', prediction)
for i in range(len(models_restricted)):
	prediction = models_restricted[i].predict(X_r)
	predictions_restricted.append(prediction)
	print('model:', model_restricted_names[i] ,'Last predicted character:', prediction)
for j in range(len(models_trait)):
	prediction = models_trait[j].predict(X_t)
	predictions_trait.append(prediction)
	print('model:', modelnames_trait[j] ,'Last predicted character:', prediction)


# testing on validation dataset
for j in range(len(models)):
	print(modelnames[j])
	print(accuracy_score(y, predictions[j]))
	print(' ')
	'''
	ax = sns.heatmap(confusion_matrix(y, predictions[j]), annot=True, cmap='Blues')

	ax.set_title(str(modelnames[j]) + '\n\n');
	ax.set_xlabel('\nPredicted Values')
	ax.set_ylabel('Actual Values ');

	plt.show()
'''
for i in range(len(models_restricted)):
	print(model_restricted_names[i])
	print(accuracy_score(y, predictions_restricted[i]))
	print(' ')
	'''
	ax = sns.heatmap(confusion_matrix(y, predictions_restricted[i]), annot=True, cmap='Blues')

	ax.set_title(str(model_restricted_names[i]) + '\n\n');
	ax.set_xlabel('\nPredicted Values')
	ax.set_ylabel('Actual Values ');

	plt.show()
'''

for j in range(len(models_trait)):
	print(modelnames_trait[j])
	print(accuracy_score(y_t, predictions_trait[j]))
	print(' ')