import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
import shap # Requires: pip install shap
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier # Requires: pip install xgboost
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score

# Ensure output directory exists
os.makedirs('evaluations', exist_ok=True)

# 1. Load Data
df = pd.read_csv('training_data/balanced_social_support_data.csv') 

# --- CORRELATION HEATMAP SECTION ---
def save_correlation_analysis(data):
    df_corr = data.copy()
    le = LabelEncoder()
    for col in df_corr.select_dtypes(include=['object']).columns:
        df_corr[col] = le.fit_transform(df_corr[col])
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(df_corr.corr(), annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('Correlation Heatmap: Independent vs Dependent Variables')
    plt.tight_layout()
    plt.savefig('evaluations/correlation_heatmap.png')
    plt.close()
    print("✅ Correlation Heatmap saved.")

save_correlation_analysis(df)

# 2. Preprocessing Setup
categorical_features = ['marital_status', 'employment_status']
numerical_features = ['age', 'family_size', 'dependents', 'monthly_income', 
                      'total_savings', 'property_value', 'has_disability', 'medical_severity']

X = df.drop('label', axis=1)
y = df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# 3. XGBoost Training & Tuning
xgb_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', XGBClassifier(random_state=42, eval_metric='logloss'))
])

xgb_param_grid = {
    'classifier__n_estimators': [100, 200],
    'classifier__learning_rate': [0.1, 0.2],
    'classifier__max_depth': [3, 5]
}

print("Starting XGBoost Hyperparameter Tuning...")
xgb_grid = GridSearchCV(xgb_pipeline, xgb_param_grid, cv=5, scoring='accuracy', n_jobs=-1)
xgb_grid.fit(X_train, y_train)
best_model = xgb_grid.best_estimator_

# 4. Evaluation
y_pred = best_model.predict(X_test)
y_prob = best_model.predict_proba(X_test)[:, 1]

# --- NEW: SAVE CONFUSION MATRIX AS PNG ---
def save_confusion_matrix_plot(y_test, y_pred):
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Ineligible', 'Eligible'], 
                yticklabels=['Ineligible', 'Eligible'])
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix: Social Support Eligibility')
    plt.savefig('evaluations/confusion_matrix.png')
    plt.close()
    print("✅ Confusion Matrix saved to 'evaluations/confusion_matrix.png'")

save_confusion_matrix_plot(y_test, y_pred)

# --- SAVE EVALUATION METRICS CHART ---
def save_metrics_plot(y_test, y_pred):
    report_dict = classification_report(y_test, y_pred, output_dict=True)
    metrics_df = pd.DataFrame(report_dict).transpose()
    plot_df = metrics_df.drop(['accuracy', 'macro avg', 'weighted avg'], errors='ignore')
    
    plt.figure(figsize=(10, 6))
    plot_df[['precision', 'recall', 'f1-score']].plot(kind='bar', ax=plt.gca())
    plt.title(f'Classification Metrics (Accuracy: {accuracy_score(y_test, y_pred):.2f})')
    plt.ylabel('Score')
    plt.ylim(0, 1.1)
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig('evaluations/evaluation_metrics.png')
    plt.close()
    print("✅ Evaluation Metrics chart saved.")

save_metrics_plot(y_test, y_pred)

# 5. Feature Importance
cat_encoder = best_model.named_steps['preprocessor'].named_transformers_['cat']
feat_names = numerical_features + list(cat_encoder.get_feature_names_out(categorical_features))
importances = best_model.named_steps['classifier'].feature_importances_

plt.figure(figsize=(10,6))
pd.Series(importances, index=feat_names).sort_values().plot(kind='barh', color='skyblue')
plt.title('XGBoost Feature Importance')
plt.tight_layout()
plt.savefig('evaluations/feature_importance.png')

# 6. SHAP Value Analysis
X_test_transformed = best_model.named_steps['preprocessor'].transform(X_test)
explainer = shap.TreeExplainer(best_model.named_steps['classifier'])
shap_values = explainer.shap_values(X_test_transformed)

plt.figure()
shap.summary_plot(shap_values, X_test_transformed, feature_names=feat_names, show=False)
plt.tight_layout()
plt.savefig('evaluations/shap_summary.png')

# 7. Finalize
joblib.dump(best_model, 'best_eligibility_model.pkl')
print("\n🚀 Model and all evaluation artifacts saved successfully.")