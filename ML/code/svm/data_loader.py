import pandas as pd

def load_data(file_dir):
	df = pd.read_csv(file_dir)
	y = df['label'].tolist()
	X = df.drop('label', axis=1).values.tolist()

	return X, y