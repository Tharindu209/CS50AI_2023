import csv
import sys
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix

TEST_SIZE = 0.4


def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    evidence = []
    labels = []

    months = {
        "Jan": 0,
        "Feb": 1,
        "Mar": 2,
        "Apr": 3,
        "May": 4,
        "June": 5,
        "Jul": 6,
        "Aug": 7,
        "Sep": 8,
        "Oct": 9,
        "Nov": 10,
        "Dec": 11,
    }

    # read csv file
    csv_file = pd.read_csv(filename)

    # prepare labels dataframe
    labels_df = csv_file["Revenue"]

    # prepare evidence dataframe
    evidence_df = csv_file.drop(columns=["Revenue"])

    # replace month names with numerical values
    evidence_df = evidence_df.replace(months)

    # replace boolean with 0/1 values
    evidence_df["VisitorType"] = evidence_df["VisitorType"].apply(
        lambda x: 1 if x == "Returning_Visitor" else 0
    )
    evidence_df["Weekend"] = evidence_df["Weekend"].apply(
        lambda x: 1 if x == "True" else 0
    )
    labels_df = labels_df.apply(lambda x: 1 if x is True else 0)

    # convert dataframes to lists
    evidence_list = evidence_df.values.tolist()
    labels_list = labels_df.values.tolist()

    return evidence_list, labels_list


def train_model(evidence, labels):
    neigh = KNeighborsClassifier(n_neighbors=1)
    neigh.fit(evidence, labels)
    return neigh


def evaluate(labels, predictions):
    tn, fp, fn, tp = confusion_matrix(labels, predictions).ravel()
    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)

    return sensitivity, specificity


if __name__ == "__main__":
    main()
