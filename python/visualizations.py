"""
Contains a class for visualizing the results of the genetic programming model.
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from sklearn.metrics import classification_report, accuracy_score
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from parse_tree import ParseTree
from genetic_programming import IrisGP


class Visualizations:
    """
    Class for visualizing the results of the genetic programming model.

    Attributes:
        parse_tree (ParseTree): A parse tree to evaluate, expected to be the
            best parse tree from the GP model.
        test_df (pd.DataFrame): The test set of the data.
        test_results (pd.DataFrame): A DataFrame containing the results of the
            predictions on the test set.
    """

    def __init__(self, parse_tree: ParseTree, test_df: pd.DataFrame):
        self.parse_tree: ParseTree = parse_tree
        self.test_df: pd.DataFrame = test_df
        self.test_results: pd.DataFrame = self.tabulate_results()

    def tabulate_results(self) -> pd.DataFrame:
        """
        Generate a table of the performance of a parse tree on the test set.
        The following columns are added:
            Correct (bool): Whether the prediction was correct.
            PredictedValue (int): The output value of the parse tree.
            PredictedSpecies (str): The predicted species of the flower.

        Returns:
            pd.DataFrame: A DataFrame containing the results.
        """
        test_results = self.test_df.copy()
        test_results["Correct"] = None
        test_results["PredictedValue"] = None
        test_results["PredictedSpecies"] = None
        for idx, row in test_results.iterrows():
            correctness, res = IrisGP.evaluate_row(self.parse_tree, row)
            test_results.at[idx, "Correct"] = correctness
            test_results.at[idx, "PredictedValue"] = res
            if res < IrisGP.THRESHOLD_LOW:
                species = "Iris-setosa"
            elif res < IrisGP.THRESHOLD_HIGH:
                species = "Iris-versicolor"
            else:
                species = "Iris-virginica"
            test_results.at[idx, "PredictedSpecies"] = species
        return test_results

    def plot_predictions_by_dimension(self, part: str):
        """
        Plot the predictions of the parse tree by either the sepal or petal
        dimensions. Points are colored by the predicted species. Correct
        predictions are smaller and transparent, while incorrect predictions
        are larger and opaque.

        Args:
            part (str): Either "Sepal" or "Petal".
        """
        COLOR_MAP = {
            "Iris-setosa": "tab:blue",
            "Iris-versicolor": "tab:orange",
            "Iris-virginica": "tab:green",
        }
        CORRECT_OPACITY = 0.3
        CORRECT_SIZE = 30
        INCORRECT_SIZE = 60
        CORRECT_LEGEND_SIZE = 6
        INCORRECT_LEGEND_SIZE = 10

        def legend_point(size: int, alpha: int, label: str):
            return Line2D(
                [],
                [],
                color="gray",
                marker="o",
                linestyle="None",
                markersize=size,
                alpha=alpha,
                label=label,
            )

        for _, row in self.test_results.iterrows():
            plt.scatter(
                row[f"{part}LengthCm"],
                row[f"{part}WidthCm"],
                color=COLOR_MAP[row["PredictedSpecies"]],
                alpha=CORRECT_OPACITY if row["Correct"] else 1,
                s=CORRECT_SIZE if row["Correct"] else INCORRECT_SIZE,
            )

        handles = [
            Patch(color="tab:blue", label="Predicted: Setosa"),
            Patch(color="tab:orange", label="Predicted: Versicolor"),
            Patch(color="tab:green", label="Predicted: Virginica"),
            legend_point(CORRECT_LEGEND_SIZE, CORRECT_OPACITY, "Correct prediction"),
            legend_point(INCORRECT_LEGEND_SIZE, 1.0, "Wrong prediction"),
        ]

        plt.legend(handles=handles, bbox_to_anchor=(1, 1), loc="upper left")
        plt.xlabel(f"{part} Length (cm)")
        plt.ylabel(f"{part} Width (cm)")
        plt.title(f"Species Predicted by GP, Plotted by {part} Dimensions")
        plt.show()

    def plot_confusion_matrix(self):
        """
        Plot the confusion matrix of the predicted species vs. the actual
        species.
        """
        cm = confusion_matrix(
            self.test_results["Species"], self.test_results["PredictedSpecies"]
        )
        disp = ConfusionMatrixDisplay(
            confusion_matrix=cm,
            display_labels=["Iris-setosa", "Iris-versicolor", "Iris-virginica"],
        )
        disp.plot(cmap=plt.cm.RdPu)
        plt.xlabel("Predicted Species")
        plt.ylabel("Actual Species")
        plt.title("GP Predicted Species Confusion Matrix")
        plt.grid(False)
        plt.show()

    def print_classification_report(self):
        """
        Print sklearn classification report and accuracy score.
        """
        y_true = self.test_results["Species"].tolist()
        y_pred = self.test_results["PredictedSpecies"].tolist()
        print("Accuracy:", accuracy_score(y_true, y_pred))
        print("\nClassification Report:")
        print(classification_report(y_true, y_pred))
