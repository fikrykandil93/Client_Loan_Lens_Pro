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
    "Logistic Regression": {"F1": 44.65, "Precision": 31.41, "Recall": 77.15},
    "Naive Bayes": {"F1": 36.44, "Precision": 22.99, "Recall": 87.84},
    "Decision Tree": {"F1": 31.37, "Precision": 31.48, "Recall": 31.28},
    "Random Forest": {"F1": 43.84, "Precision": 47.30, "Recall": 40.86},
    "XGBoost": {"F1": 46.74, "Precision": 33.98, "Recall": 74.84},
}
# Final XGBoost after GridSearchCV (learning_rate 0.1, max_depth 7, n_estimators 200)
FINAL_MODEL = {"name": "XGBoost", "F1": 47.00, "Precision": 34.24, "Recall": 74.91}
