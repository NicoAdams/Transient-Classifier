from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np

#import training data
training_data_raw = pd.read_csv("/home/chwor001/Transient-Classifier/Transient-Classifier/data/training/TNS_SDSS_6arcsec_training.csv")

#Sources that are labelled SN are True (boolean)
training_data_raw['is_SN'] = training_data_raw['transient_label'].str.contains("SN")

#select attributes to train on
training_data = training_data_raw.drop(['id', 'ra','dec', 'transient_label','transient_filter'], axis = 1)

#Remove data with missing information
training_data.dropna(inplace=True)

#Randomly select data to train on, this will change when I use a seperate data set for testing
training_data['is_train'] = np.random.uniform(0, 1, len(training_data)) <= .75
##############################################################################################

train, test = training_data[training_data['is_train'] == True], training_data[training_data['is_train'] == False]

print('# obs in training data:', len(train))
print('# obs in test data:', len(test))

#Just train on offset redshift and transient magnitude for now
features = training_data.columns[1:4]

#Check for complete data
train[features].describe()
#train
#print(train[features].isna().sum())

#Training
clf = RandomForestClassifier(n_jobs=2, random_state=0)
clf.fit(train[features], train['is_SN'])

##############################################################################################
#Predictions etc.
preds = clf.predict(test[features])

#Converting to a boolean array -- there's probably a better way to do this?
preds = preds >= 1
#preds
#test['is_SN'].head()


# In[210]:


#Make a confusion matrix
pd.crosstab(test['is_SN'], preds, rownames = ['Actual SN'], colnames = ['Predicted SN'])

