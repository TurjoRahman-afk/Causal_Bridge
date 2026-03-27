"""
Data Quality Checks for Better Causal Inference
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


"""
df - The dataset
treatment- cause variable name 
outcome - Effect variable name
cofounders - List of control variables
"""
def check_data_quality(df: pd.DataFrame, treatment: str, outcome: str, 
                       confounders: List[str]) -> Dict:
    """
    Run diagnostic checks before causal analysis
    Returns warnings and suggestions
    """
    warnings = []
    recommendations = []
    
    # DEBUG: Print what we're checking
    print(f"🔍 DATA_QUALITY: Checking columns:")
    print(f"   Treatment: '{treatment}'")
    print(f"   Outcome: '{outcome}'")
    print(f"   Confounders: {confounders}")
    print(f"   Available DF columns: {list(df.columns)}")
    
    # Verify all columns exist
    required_cols = [treatment, outcome] + confounders
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"❌ DATA_QUALITY: Missing columns in DataFrame: {missing}")
    
    # 1. Check sample size
    n = len(df)
    if n < 30:
        warnings.append(f"⚠️ Small sample size ({n}). Need 30+ for reliable results.")
    elif n < 100:
        warnings.append(f"⚠️ Limited sample size ({n}). Results may be unstable.")
    
    # 2. Check missing data
    missing = df[[treatment, outcome] + confounders].isnull().sum()
    if missing.sum() > 0:
        warnings.append(f"⚠️ Missing data: {missing[missing > 0].to_dict()}")
        recommendations.append("Consider imputation or removing incomplete rows")
    
    # 3. Check treatment variation
    if df[treatment].nunique() < 2:
        warnings.append(f"❌ No variation in treatment! All values are the same.")
        return {"valid": False, "warnings": warnings}
    
    # 4. Check outcome variation
    if df[outcome].nunique() < 2:
        warnings.append(f"❌ No variation in outcome! All values are the same.")
        return {"valid": False, "warnings": warnings}
    
    # 5. Check for common support (overlap)
    if df[treatment].dtype in ['object', 'category', 'bool'] or df[treatment].nunique() == 2:
        # Binary treatment - only check numeric confounders for range overlap
        numeric_confounders = [c for c in confounders if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
        
        if numeric_confounders:
            treated_confounders = df[df[treatment] == df[treatment].unique()[0]][numeric_confounders].describe()
            control_confounders = df[df[treatment] == df[treatment].unique()[1]][numeric_confounders].describe()
            
            # Check if confounder distributions overlap
            for conf in numeric_confounders:
                treated_range = (treated_confounders[conf]['min'], treated_confounders[conf]['max'])
                control_range = (control_confounders[conf]['min'], control_confounders[conf]['max'])
                
                # Check overlap
                overlap = min(treated_range[1], control_range[1]) - max(treated_range[0], control_range[0])
                if overlap <= 0:
                    warnings.append(f"⚠️ No overlap in {conf} between treated/control groups")
                    recommendations.append(f"Results for {conf} may not be reliable")
    
    # 6. Check for multicollinearity
    if len(confounders) > 1:
        numeric_confounders = [c for c in confounders if pd.api.types.is_numeric_dtype(df[c])]
        if len(numeric_confounders) > 1:
            corr_matrix = df[numeric_confounders].corr()
            high_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if abs(corr_matrix.iloc[i, j]) > 0.8:
                        high_corr.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_matrix.iloc[i, j]))
            
            if high_corr:
                warnings.append(f"⚠️ High correlation between confounders: {high_corr}")
                recommendations.append("Consider removing redundant confounders")
    
    # 7. Check treatment balance
    if df[treatment].nunique() == 2:
        counts = df[treatment].value_counts()
        if counts.min() / counts.max() < 0.2:
            warnings.append(f"⚠️ Imbalanced treatment: {counts.to_dict()}")
            recommendations.append("Consider propensity score matching")
    
    return {
        "valid": True,
        "sample_size": n,
        "warnings": warnings,
        "recommendations": recommendations,
        "missing_data": missing.to_dict(),
        "treatment_distribution": df[treatment].value_counts().to_dict()
    }

def suggest_confounders(df: pd.DataFrame, treatment: str, outcome: str) -> List[str]:
    """
    Automatically suggest potential confounders using correlation analysis
    """
    suggestions = []
    
    # Find variables correlated with both treatment and outcome
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    numeric_cols = [c for c in numeric_cols if c not in [treatment, outcome]]
    
    for col in numeric_cols:
        # Correlation with treatment
        corr_treatment = abs(df[[col, treatment]].corr().iloc[0, 1])
        # Correlation with outcome  
        corr_outcome = abs(df[[col, outcome]].corr().iloc[0, 1])
        
        # If correlated with both (potential confounder)
        if corr_treatment > 0.1 and corr_outcome > 0.1:
            suggestions.append({
                "variable": col,
                "corr_treatment": round(corr_treatment, 3),
                "corr_outcome": round(corr_outcome, 3),
                "score": round((corr_treatment + corr_outcome) / 2, 3)
            })
    
    # Sort by score
    suggestions.sort(key=lambda x: x['score'], reverse=True)
    
    return suggestions[:5]  # Top 5 suggestions
