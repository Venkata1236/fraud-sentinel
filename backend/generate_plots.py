import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from pathlib import Path
from sklearn.metrics import confusion_matrix, precision_recall_curve, average_precision_score
from sklearn.model_selection import train_test_split
import shap

MODELS_DIR = Path("models")
df = pd.read_csv("data/creditcard.csv")
model = joblib.load("models/fraud_model.pkl")
X = df.drop('Class', axis=1)
y = df['Class']
_, X_test, _, y_test = train_test_split(X, y, test_size=0.10, random_state=42, stratify=y)

# 1
class_counts = df['Class'].value_counts()
fig, ax = plt.subplots(figsize=(6,4))
ax.bar(['Legitimate','Fraud'], class_counts.values, color=['#2ecc71','#e74c3c'])
ax.set_title('Class Distribution')
plt.tight_layout()
plt.savefig(MODELS_DIR/"class_distribution.png", dpi=120)
plt.close()
print("1. class_distribution.png saved")

# 2
fig, ax = plt.subplots(figsize=(8,4))
df[df.Class==0]['Amount'].hist(bins=60,alpha=0.6,label='Legit',color='#2ecc71',ax=ax)
df[df.Class==1]['Amount'].hist(bins=60,alpha=0.8,label='Fraud',color='#e74c3c',ax=ax)
ax.legend(); ax.set_title('Amount Distribution')
plt.tight_layout()
plt.savefig(MODELS_DIR/"amount_distribution.png", dpi=120)
plt.close()
print("2. amount_distribution.png saved")

# 3
cols = [f'V{i}' for i in range(1,11)] + ['Amount','Class']
corr = df[cols].corr()
plt.figure(figsize=(10,8))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0)
plt.title('Correlation Heatmap')
plt.tight_layout()
plt.savefig(MODELS_DIR/"correlation_heatmap.png", dpi=120)
plt.close()
print("3. correlation_heatmap.png saved")

# 4
y_pred = model.predict(X_test)
cm = confusion_matrix(y_test, y_pred)
fig, ax = plt.subplots(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
    xticklabels=['Pred Legit','Pred Fraud'],
    yticklabels=['Actual Legit','Actual Fraud'], ax=ax)
ax.set_title('Confusion Matrix')
plt.tight_layout()
plt.savefig(MODELS_DIR/"confusion_matrix.png", dpi=120)
plt.close()
print("4. confusion_matrix.png saved")

# 5
y_proba = model.predict_proba(X_test)[:,1]
precision, recall, _ = precision_recall_curve(y_test, y_proba)
ap = average_precision_score(y_test, y_proba)
plt.figure(figsize=(8,5))
plt.plot(recall, precision, color='#e74c3c', lw=2, label=f'AP={ap:.4f}')
plt.xlabel('Recall'); plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.legend(); plt.tight_layout()
plt.savefig(MODELS_DIR/"pr_curve.png", dpi=120)
plt.close()
print("5. pr_curve.png saved")

# 6
print("Initialising SHAP (takes ~30s)...")
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test.iloc[:200])
plt.figure(figsize=(10,8))
shap.summary_plot(shap_values, X_test.iloc[:200], max_display=20, show=False)
plt.tight_layout()
plt.savefig(MODELS_DIR/"shap_summary.png", dpi=120, bbox_inches='tight')
plt.close()
print("6. shap_summary.png saved")

# 7
fraud_pos = X_test.index.get_loc(y_test[y_test==1].index[0])
sv = explainer(X_test.iloc[fraud_pos:fraud_pos+1])
shap.waterfall_plot(sv[0], max_display=15, show=False)
plt.tight_layout()
plt.savefig(MODELS_DIR/"shap_waterfall.png", dpi=120, bbox_inches='tight')
plt.close()
print("7. shap_waterfall.png saved")

print("\nAll 7 plots done.")