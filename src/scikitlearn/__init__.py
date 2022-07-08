# See https://towardsdatascience.com/hybrid-rule-based-machine-learning-with-scikit-learn-9cb9841bebf2
from typing import Dict, Tuple, Any
from sklearn.base import BaseEstimator
from sklearn.ensemble import GradientBoostingClassifier
import pandas as pd
import numpy as np

# Tuple format: ("logical operator of rule", split criterion, value which model should return if rule is applicable)

rules_dict = {"Price": [
    ("<", 1000.0, 0.0),
    (">=", 500000, 1.0)
]}


class RuleAugmentedGbc(BaseEstimator):

    def __init__(self, base_model: BaseEstimator) -> None:
        self.base_model = base_model


    @property
    def rules(self) -> Dict[str, Any]:

        rules_dict = {"Price": [
                ("<", 1000.0, 0.0),
                (">=", 1000.0, 1.0)
            ],
            "NumberOfBedrooms": [
                ("<", 1.0, 0.0),
                (">=", 1.0, 1.0)
            ]}

        return rules_dict


    def fit(self, X: pd.DataFrame, y: pd.Series, **kwargs) -> None:
        train_x, train_y = self.__get_base_model_data(X, y)
        self.base_model.fit(train_x, train_y, **kwargs)


    def __get_base_model_data(self, X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
        train_x = X

        for category, rules in self.rules.items():
            
            if category not in train_x.columns.values:
                continue

            for rule in rules:
                if rule[0] == "=":
                    train_x = train_x.loc[train_x[category] != rule[1]]

                elif rule[0] == "<":
                    train_x = train_x.loc[train_x[category] >= rule[1]]

                elif rule[0] == ">":
                    train_x = train_x.loc[train_x[category] <= rule[1]]

                elif rule[0] == "<=":
                    train_x = train_x.loc[train_x[category] > rule[1]]

                elif rule[0] == ">=":
                    train_x = train_x.loc[train_x[category] < rule[1]]

                else:
                    print(f"Invalid rule detected: {rule}")

        indices = train_x.index.values
        train_y = y.iloc[indices]
        train_x = train_x.reset_index(drop=True)
        train_y = train_y.reset_index(drop=True)

        return train_x, train_y

    
    def predict(self, X: pd.DataFrame) -> np.array:

        p_X = X.copy()
        p_X["prediction"] = np.nan

        for category, rules in self.rules.items():

            if category not in p_X.columns.values:
                continue

            for rule in rules:

                if rule[0] == "=":
                    p_X.loc[p_X[category] == rule[1], "prediction"] = rule[2]

                elif rule[0] == "<":
                    p_X.loc[p_X[category] < rule[1], "prediction"] = rule[2]

                elif rule[0] == ">":
                    p_X.loc[p_X[category] > rule[1], "prediction"] = rule[2]

                elif rule[0] == "<=":
                    p_X.loc[p_X[category] <= rule[1], "prediction"] = rule[2]

                elif rule[0] == ">=":
                    p_X.loc[p_X[category] >= rule[1], "prediction"] = rule[2]

                else:
                    print(f"Invalid rule detected: {rule}")

        if len(p_X.loc[p_X["prediction"].isna()].index) != 0:
            base_X = p_X.loc[p_X["prediction"].isna()].copy()
            base_X.drop("prediction", axis=1, inplace=True)
            p_X.loc[p_X["prediction"].isna(), "prediction"] = self.base_model.predict(base_X)

        return p_X["prediction"].values


if __name__ == "__main__":

    gbc = GradientBoostingClassifier(n_estimators=50)
    rule_classifier = RuleAugmentedGbc(gbc)
    test_X = pd.read_excel('C:\\Users\\s.suthers\\Documents\\Github\\rules.engine.testing\\rules.engine.testing\\src\\scikitlearn\\x_test.xlsx', sheet_name="Sheet1")
    predictions = rule_classifier.predict(test_X)

    print(predictions)
