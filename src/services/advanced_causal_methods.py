"""
Advanced Causal Inference Methods
This only makes PSM, DiD and IV available as specialized methods.
"""
import pandas as pd
import numpy as np
from typing import Dict

def propensity_score_matching(df: pd.DataFrame, treatment: str, outcome: str, confounders: list) -> Dict:
    """
    Better for binary treatments (Yes/No, 0/1)
    Matches treated units with similar control units
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.neighbors import NearestNeighbors
    
    # Ensure binary treatment
    treatment_vals = df[treatment].values
    if not set(np.unique(treatment_vals)).issubset({0, 1}):
        raise ValueError("PSM requires binary treatment (0/1)")
    
    # 1. Estimate propensity scores (probability of treatment)
    X_conf = df[confounders].values
    propensity_model = LogisticRegression()
    propensity_model.fit(X_conf, treatment_vals)
    propensity_scores = propensity_model.predict_proba(X_conf)[:, 1]
    
    # 2. Match treated to control based on propensity
    treated_mask = treatment_vals == 1
    control_mask = treatment_vals == 0
    
    treated_ps = propensity_scores[treated_mask].reshape(-1, 1)
    control_ps = propensity_scores[control_mask].reshape(-1, 1)
    
    # Find nearest neighbor for each treated unit
    nn = NearestNeighbors(n_neighbors=1)
    nn.fit(control_ps)
    matches = nn.kneighbors(treated_ps, return_distance=False)
    
    # 3. Calculate ATE on matched sample
    treated_outcomes = df[outcome].values[treated_mask]
    control_indices = np.where(control_mask)[0][matches.flatten()]
    control_outcomes = df[outcome].values[control_indices]
    
    ate = np.mean(treated_outcomes - control_outcomes)
    
    # Bootstrap for CI
    bootstrap_estimates = []
    for _ in range(100):
        idx = np.random.choice(len(treated_outcomes), len(treated_outcomes), replace=True)
        boot_ate = np.mean(treated_outcomes[idx] - control_outcomes[idx])
        bootstrap_estimates.append(boot_ate)
    
    ci_lower = np.percentile(bootstrap_estimates, 2.5)
    ci_upper = np.percentile(bootstrap_estimates, 97.5)
    se = np.std(bootstrap_estimates)
    
    return {
        "ate": float(ate),
        "confidence_interval": [float(ci_lower), float(ci_upper)],
        "standard_error": float(se),
        "n_treated": int(treated_mask.sum()),
        "n_control": int(control_mask.sum()),
        "method": "propensity_score_matching"
    }

def difference_in_differences(df: pd.DataFrame, treatment: str, outcome: str, 
                             time_var: str, treated_group: str) -> Dict:
    """
    For before/after studies with treatment and control groups
    Example: Did policy change affect outcome?
    """
    # Requires: time variable (before/after) and group variable (treated/control)
    
    # Calculate means
    before_treated = df[(df[time_var] == 0) & (df[treated_group] == 1)][outcome].mean()
    after_treated = df[(df[time_var] == 1) & (df[treated_group] == 1)][outcome].mean()
    before_control = df[(df[time_var] == 0) & (df[treated_group] == 0)][outcome].mean()
    after_control = df[(df[time_var] == 1) & (df[treated_group] == 0)][outcome].mean()
    
    # DID estimator: (After_T - Before_T) - (After_C - Before_C)
    ate = (after_treated - before_treated) - (after_control - before_control)
    
    # Simple standard error (simplified)
    se = np.sqrt(
        df[outcome].var() / len(df)
    )
    
    return {
        "ate": float(ate),
        "method": "difference_in_differences",
        "standard_error": float(se)
    }

def instrumental_variable(df: pd.DataFrame, treatment: str, outcome: str, 
                         instrument: str, confounders: list) -> Dict:
    """
    For when treatment is endogenous (affected by unmeasured variables)
    Requires: an instrumental variable that affects treatment but not outcome directly
    """
    from sklearn.linear_model import LinearRegression
    
    # Two-stage least squares (2SLS)
    
    # Stage 1: Predict treatment using instrument
    X_stage1 = df[[instrument] + confounders].values
    treatment_vals = df[treatment].values
    
    model_stage1 = LinearRegression()
    model_stage1.fit(X_stage1, treatment_vals)
    predicted_treatment = model_stage1.predict(X_stage1)
    
    # Stage 2: Use predicted treatment to estimate effect
    X_stage2 = np.column_stack([predicted_treatment, df[confounders].values])
    outcome_vals = df[outcome].values
    
    model_stage2 = LinearRegression()
    model_stage2.fit(X_stage2, outcome_vals)
    
    ate = model_stage2.coef_[0]
    
    return {
        "ate": float(ate),
        "method": "instrumental_variable"
    }

# Add these imports to causal_inference_service.py:
# from .advanced_methods import propensity_score_matching, difference_in_differences
