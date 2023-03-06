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
import string

try:
	data_file = str(sys.argv[1])
except:
	data_file_1 = 'alphabet_button_Raw.txt'
	data_file_2 = 'alphabet_final_Raw.txt'
print('loading data from', data_file_1)

try:
	model_file = str(sys.argv[2])
except:
	model_file = 'model_final_raw.sav'
print('Finished model will be stored in', model_file)

with open(data_file_1) as f:
	lines = f.read()
	first = lines.split('\n', 1)[0]
	first_list = first.split(', ')


name = [str(i) for i in range(len(first_list))]
name[0] = "class"

dataset1 = read_csv(data_file_1, index_col = False, names=name)
dataset2 = read_csv(data_file_2, index_col = False, names=name)
dataset = dataset1.append(dataset2)

#dataset = dataset.iloc[:65]
#dataset = dataset.drop(labels=135, axis=0)
#dataset = dataset.fillna('?')

#count_nan_in_df = dataset.isnull().sum().sum()
#print ('Count of NaN: ' + str(count_nan_in_df))
#dataset['full_count'] = dataset.apply(lambda x: x.count(), axis=1)

pd.set_option('display.max_rows', dataset.shape[0]+5)
#print(dataset['full_count'])
#print(dataset.iloc[135])
#dataset.loc[dataset['class'] == 'WW']['class'] = 'W'
dataset['class'] = dataset['class'].replace(['WW'],'W')

start = 1

#indexes = [str(i%5 + 14 * (i//5)+1) for i in range(0, 45*5)]
indexes = [str(i) for i in range(14*30+12, 14*30+15)]
#indexes = ['286', '287', '288', '289', '290', '291']
#indexes = [str(i) for i in range(2, 630, 14*5)]
print('Indexes:', indexes)
columns = []
columns.append('class')
columns.extend(indexes)
print('columns:', columns)

subset = dataset[columns]

# shape
print(subset.shape)

# head
print(subset.head(20))

# descriptions
print(subset.describe())

# class distribution
print("Class distribution:")
print(subset.groupby('class').size())

# box and whisker plots
# subset.plot(kind='box', subplots=True, layout=(5,5), sharex=False, sharey=False)
# pyplot.show()

# histograms
# subset.hist()
# pyplot.show()

'''
df_temp = subset[subset["class"] == "X"]
df_temp.hist(range=(0.8,2.5))
pyplot.suptitle('Resistance 1: 0.2s, 0.4s, 0.6s, 0.8s, 1.0s, 1.2s, 1.4s, 1.6s, 1.8s', fontsize = 16)
#pyplot.xlim((0.8, 2.5))
pyplot.show()

'''
'''
alphabet = list(string.ascii_uppercase)

for letter in alphabet:
	df_temp = subset[subset["class"] == letter]

	fig = plt.figure(figsize=(13, 7))
	ax = fig.gca()
	df_temp.hist(ax=ax, range=[0.8, 2.4])
	pyplot.suptitle(letter, fontsize = 16)
	pyplot.show()
'''

#df_temp = subset[subset["class"].isin(['A', 'D', 'O', 'S', 'C', 'I'])]
df_temp = subset[subset["class"].isin(['T', 'F'])]
print("Class distribution:")
print(df_temp.groupby('class').size())
#g = sns.pairplot(subset, hue="class")
#for i in range(5):
#	g.axes[i,i].set_xlim((0.9,2.2))

df = pd.melt(subset, subset.columns[0], subset.columns[1:])

g = sns.FacetGrid(df, col="variable", hue="class", col_wrap=2)#, ylim=(0,20), xlim=(-2.5, 3))
g.map(sns.kdeplot, "value", shade=True)
g.add_legend()
plt.show()
# scatter plot matrix
# scatter_matrix(subset)
# pyplot.show()
