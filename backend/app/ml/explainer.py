"""
SHAP TreeExplainer wrapper.

Why TreeExplainer (not KernelExplainer)?
  - TreeExplainer uses the exact Shapley values algorithm optimised for
    tree-based models (XGBoost, LightGBM, RandomForest).
  - O(TLD) complexity vs O(2^F) brute force — 1000x faster on 30 features.
  - KernelExplainer is model-agnostic but too slow for real-time inference.
"""

import shap
import numpy as np
import pandas as pd
from loguru import logger
from xgboost import XGBClassifier


class FraudExplainer:
    def __init__(self, model: XGBClassifier, feature_names: list[str]):
        self.feature_names = feature_names
        logger.info("Initialising SHAP TreeExplainer...")
        self.explainer = shap.TreeExplainer(model)
        logger.info("SHAP TreeExplainer ready.")

    def explain(self, features: list[float]) -> dict:
        """
        Returns SHAP values + top 5 features for a single transaction.

        SHAP value semantics:
          - Positive SHAP  → pushes prediction TOWARD fraud
          - Negative SHAP  → pushes prediction TOWARD legitimate
          - Magnitude      → how much that feature moved the probability

        Returns:
            {
                "shap_values": [float, ...],     # one per feature
                "top_features": [
                    {"feature": str, "raw_value": float, "shap_impact": float}
                ]
            }
        """
        X = pd.DataFrame([features], columns=self.feature_names)
        shap_vals = self.explainer.shap_values(X)

        # shap_values returns shape (1, n_features) for binary classification
        # We take [0] → shape (n_features,)
        sv = shap_vals[0] if isinstance(shap_vals, list) else shap_vals[0]
        sv_list = sv.tolist()

        # Top 5 features by absolute SHAP impact
        abs_impacts = np.abs(sv)
        top5_idx = np.argsort(abs_impacts)[::-1][:5]

        top_features = [
            {
                "feature": self.feature_names[i],
                "raw_value": float(features[i]),
                "shap_impact": float(sv[i]),
            }
            for i in top5_idx
        ]

        return {"shap_values": sv_list, "top_features": top_features}
# end of explainer

# SHAP TreeExplainer uses exact Shapley values for tree models
