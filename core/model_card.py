"""Results and descriptions shown in the app, copied from the project notebooks."""

# LoanLens_03_Segmentation: names and short descriptions of the five KMeans segments
SEGMENT_ORDER = ["Prime – Mass Affluent", "Prime – Professionals", "Near-Prime – Emerging",
                 "Subprime – Mature", "Subprime – Young"]
SEGMENT_TEXT = {
    "Prime – Mass Affluent": "The highest income per person and the best credit scores; mostly in their fifties.",
    "Prime – Professionals": "Almost all have higher education, with high income and good credit scores.",
    "Near-Prime – Emerging": "Young clients with the lowest income but good credit scores: future clients to grow.",
    "Subprime – Mature": "Older clients with weak credit scores, often in lower-rated regions.",
    "Subprime – Young": "Young clients with the lowest credit scores in the portfolio.",
}
SILHOUETTE = "0.17–0.21"

# LoanLens_02_Approval_Model: 5-fold cross-validation with class weights, default settings (%)
ALGORITHMS = {
    "Logistic Regression": {"F1": 44.64, "Precision": 31.37, "Recall": 77.32},
    "Naive Bayes": {"F1": 36.35, "Precision": 22.88, "Recall": 88.38},
    "Decision Tree": {"F1": 31.37, "Precision": 31.59, "Recall": 31.16},
    "Random Forest": {"F1": 44.10, "Precision": 47.29, "Recall": 41.31},
    "XGBoost": {"F1": 46.66, "Precision": 33.84, "Recall": 75.11},
}
# Final XGBoost after GridSearchCV (learning_rate 0.1, max_depth 7, n_estimators 200)
FINAL_MODEL = {"name": "XGBoost", "F1": 47.00, "Precision": 34.24, "Recall": 74.91}
