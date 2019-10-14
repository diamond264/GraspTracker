import pickle
import sys
import pandas as pd
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier

def load_data(file_dir):
	df = pd.read_csv(file_dir)
	df = df.loc[:len(df)//5*4]
	y = df['label'].tolist()
	X = df.drop('label', axis=1).values.tolist()

	return X, y


def train(X, y):
	# model = svm.SVC(kernel='poly', C=1.0)
	model = RandomForestClassifier()
	model.fit(X, y)

	return model


def save_model(model, filename):
	with open(filename, 'wb') as f:
		pickle.dump(model, f)


if __name__ == "__main__":
	X, y = load_data(sys.argv[1])
	model = train(X, y)
	save_model(model, sys.argv[2])
