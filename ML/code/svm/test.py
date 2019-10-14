import pickle
import sys
import pandas as pd

def load_data(file_dir):
    df = pd.read_csv(file_dir)
    df = df.loc[len(df)//5*4:]
    y = df['label'].tolist()
    X = df.drop('label', axis=1).values.tolist()
    print(y)

    return X, y


def load_model(model_dir):
    with open(model_dir, 'rb') as f:
        model = pickle.load(f)
    return model


if __name__ == "__main__":
    X_test, y_test = load_data(sys.argv[2])
    svc = load_model(sys.argv[1])
    print("테스트 세트 정확도: {:.2f}".format(svc.score(X_test, y_test)))