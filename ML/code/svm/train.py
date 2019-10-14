import pickle
import sys
import pandas as pd
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier

def load_data(file_dir):
	df = pd.read_csv(file_dir)
	df.sample(frac=1)
	df_train = df.loc[:len(df)//5*4]
	y = df_train['label'].tolist()
	X = df_train.drop('label', axis=1).values.tolist()

	df_test = df.loc[len(df)//5*4:]
	y_test = df_test['label'].tolist()
	X_test = df_test.drop('label', axis=1).values.tolist()

	return X, y, X_test, y_test


def train(mode, X, y, X_test, y_test):
	if mode == "svm":
		model = svm.SVC(kernel='poly', C=1.0)
	if mode == "randomforest":
		model = RandomForestClassifier()
	model.fit(X, y)
	model.score(X_test, y_test)

	return model


def save_model(model, filename):
	with open(filename, 'wb') as f:
		pickle.dump(model, f)


if __name__ == "__main__":
	X, y, X_test, y_test = load_data(sys.argv[3])
	model = train(sys.argv[1], X, y, X_test, y_test)
	save_model(model, sys.argv[2])
