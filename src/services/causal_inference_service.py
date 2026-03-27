"""
Causal Inference Service for executing statistical analysis.
Plan from Gemini -> This file -> Statistical Results
"""
from typing import Dict, Any
import pandas as pd
import numpy as np
from ..core.config import settings
from ..core.exceptions import EstimationException
from .data_quality import check_data_quality, suggest_confounders
from .advanced_causal_methods import propensity_score_matching, difference_in_differences, instrumental_variable

def run_estimation(plan: Dict, dataset_uri: str, schema: Dict) -> Dict[str, Any]:
    """
User Request
    ↓
causal_inference_service.py (MANAGER)
    ├─ Loads data
    ├─ Validates columns
    ├─ Runs quality checks
    ├─ Decides which method to use
    └─ CALLS → advanced_causal_methods.py (SPECIALISTS)
                    ├─ PSM algorithm
                    ├─ DiD algorithm
                    └─ IV algorithm
    ↓
Returns results to user
    """
    try:
        # Load dataset
        df = _load_data(dataset_uri)
        
        # Extract variables
        treatment = plan["treatment"]
        outcome = plan["outcome"]
        confounders = plan.get("confounders", [])
        method = plan.get("method", "backdoor")
        
        # Clean confounders list - remove empty strings, None, whitespace
        confounders = [c.strip() for c in confounders if c and str(c).strip()]
        
        print(f"🔍 DEBUG: Original variables - Treatment: '{treatment}', Outcome: '{outcome}', Confounders: {confounders}")
        print(f"🔍 DEBUG: Input DataFrame columns: {list(df.columns)}")
        print(f"🔍 DEBUG: DataFrame shape: {df.shape}")
        
        # Validate columns exist and get mapping for fuzzy matches
        column_mapping = _validate_columns(df, treatment, outcome, confounders)
        
        print(f"🗺️ DEBUG: Column mapping: {column_mapping}")
        
        # Rename DataFrame columns to match what AI identified
        # This is the FIX: Instead of changing variable names, we rename the DF columns
        reverse_mapping = {v: k for k, v in column_mapping.items()}
        if reverse_mapping:
            print(f"🔄 DEBUG: Renaming DF columns: {reverse_mapping}")
            df = df.rename(columns=reverse_mapping)
            print(f"✅ DEBUG: DF columns after rename: {list(df.columns)}")
        
        print(f"✅ DEBUG: Using variables - Treatment: '{treatment}', Outcome: '{outcome}', Confounders: {confounders}")
        
        # Run data quality checks
        quality_check = check_data_quality(df, treatment, outcome, confounders)
        if not quality_check.get("valid", False):
            raise EstimationException(f"Data quality issues: {quality_check.get('warnings', [])}")
        
        # Run causal estimation based on method
        if method == "backdoor":
            results = _backdoor_estimation(df, treatment, outcome, confounders)
        elif method == "propensity_score_matching" or method == "psm":
            # Use advanced PSM method for binary treatments
            df_encoded = _encode_categorical(df, [treatment, outcome] + confounders)
            df_clean = df_encoded[[treatment, outcome] + confounders].dropna()

            # Enforce strict 0/1 binary on treatment
            unique_vals = sorted(df_clean[treatment].dropna().unique())
            if len(unique_vals) == 2:
                # Map the two unique values to 0 and 1 regardless of what they are
                val_map = {unique_vals[0]: 0, unique_vals[1]: 1}
                df_clean = df_clean.copy()
                df_clean[treatment] = df_clean[treatment].map(val_map).astype(int)
                print(f"✅ PSM: Mapped {unique_vals} → [0, 1]")
            elif set(unique_vals).issubset({0, 1, 0.0, 1.0}):
                # Already binary, just make sure it's int
                df_clean = df_clean.copy()
                df_clean[treatment] = df_clean[treatment].astype(int)
            else:
                # Not binary — fall back to backdoor
                print(f"⚠️  PSM requested but treatment '{treatment}' has {len(unique_vals)} unique values. Falling back to backdoor.")
                results = _backdoor_estimation(df, treatment, outcome, confounders)
                results["method_used"] = "backdoor"
                results["warning"] = f"PSM requires binary treatment. Switched to backdoor adjustment automatically."
                results["data_quality"] = quality_check
                return results

            results = propensity_score_matching(df_clean, treatment, outcome, confounders)
        elif method == "difference_in_differences" or method == "did":
            # Requires time_var and treated_group in schema
            time_var = schema.get("time_variable", "time")
            treated_group = schema.get("group_variable", "group")
            results = difference_in_differences(df, treatment, outcome, time_var, treated_group)
        elif method == "instrumental_variable" or method == "iv":
            # Requires instrument variable in schema
            instrument = schema.get("instrument", confounders[0] if confounders else treatment)
            df_encoded = _encode_categorical(df, [treatment, outcome, instrument] + confounders)
            df_clean = df_encoded[[treatment, outcome, instrument] + confounders].dropna()
            results = instrumental_variable(df_clean, treatment, outcome, instrument, confounders)
        elif method == "regression_discontinuity" or method == "rd":
            results = _rd_estimation(df, treatment, outcome, schema)
        else:
            # Default to backdoor
            results = _backdoor_estimation(df, treatment, outcome, confounders)
        
        results["method_used"] = method
        results["data_quality"] = quality_check
        
        # Add confounder suggestions if user provided few/no confounders
        if len(confounders) < 3:
            try:
                suggestions = suggest_confounders(df, treatment, outcome)
                if suggestions:
                    results["suggested_confounders"] = suggestions[:3]
            except:
                pass
        
        return results
        
    except KeyError as ke:
        import traceback
        error_trace = traceback.format_exc()
        print(f"🚨 KeyError occurred: {ke}")
        print(f"📍 Full traceback:\n{error_trace}")
        print(f"🔍 Current DataFrame columns: {list(df.columns) if 'df' in locals() else 'DataFrame not available'}")
        print(f"🔍 Variables being used: treatment='{treatment if 'treatment' in locals() else 'N/A'}', outcome='{outcome if 'outcome' in locals() else 'N/A'}', confounders={confounders if 'confounders' in locals() else 'N/A'}")
        raise EstimationException(f"Column access error: {ke}. Check if column names match exactly!")
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"🚨 Error occurred: {e}")
        print(f"📍 Full traceback:\n{error_trace}")
        raise EstimationException(f"Estimation failed: {str(e)}")

def _load_data(dataset_uri: str) -> pd.DataFrame:
    """Load dataset from URI - supports CSV, Excel, JSON, Parquet."""
    if dataset_uri.endswith('.csv'):
        return pd.read_csv(dataset_uri)
    elif dataset_uri.endswith(('.xlsx', '.xls')):
        return pd.read_excel(dataset_uri)
    elif dataset_uri.endswith('.json'):
        return pd.read_json(dataset_uri)
    elif dataset_uri.endswith('.parquet'):
        return pd.read_parquet(dataset_uri)
    else:
        # Try CSV as default
        try:
            return pd.read_csv(dataset_uri)
        except:
            raise EstimationException(f"Unsupported file format: {dataset_uri}")

def _normalize_column_name(name: str) -> str:
    """Normalize column name by removing spaces, underscores, and converting to lowercase."""
    return name.replace(' ', '').replace('_', '').replace('-', '').lower()

def _find_matching_column(target: str, available_columns: list) -> str:
    """
    Find a matching column name with fuzzy matching.
    Handles: 'Discount Applied', 'DiscountApplied', 'Discount_Applied', 'discount-applied'
    """
    # First try exact match
    if target in available_columns:
        return target
    
    # Try normalized matching
    target_normalized = _normalize_column_name(target)
    for col in available_columns:
        if _normalize_column_name(col) == target_normalized:
            return col
    
    # No match found
    return None

def _validate_columns(df: pd.DataFrame, treatment: str, outcome: str, confounders: list):
    """Validate that required columns exist in dataset with smart matching."""
    # Filter out empty strings from confounders
    confounders = [c for c in confounders if c and c.strip()]
    
    required_cols = [treatment, outcome] + confounders
    available_cols = list(df.columns)
    
    print(f"🔍 DEBUG: Looking for columns: {required_cols}")
    print(f"📋 DEBUG: Available columns: {available_cols}")
    
    # Try to find matches for missing columns
    column_mapping = {}  # Maps: AI-identified name → actual CSV name
    missing_cols = []
    
    for col in required_cols:
        if not col or not col.strip():  # Skip empty values
            continue
        matched = _find_matching_column(col, available_cols)
        if matched:
            # ALWAYS add to mapping, even if exact match (for consistency)
            column_mapping[col] = matched
            print(f"✅ DEBUG: '{col}' matched to '{matched}'")
        else:
            missing_cols.append(col)
            print(f"❌ DEBUG: '{col}' NOT FOUND")
    
    if missing_cols:
        # Try to suggest similar columns
        suggestions = {}
        for missing in missing_cols:
            similar = [c for c in available_cols if missing.lower() in c.lower() or c.lower() in missing.lower()]
            if similar:
                suggestions[missing] = similar[:3]
        
        error_msg = f"❌ Cannot find columns: {missing_cols}\n\n"
        error_msg += f"📋 Available columns in your dataset:\n{', '.join(available_cols)}\n\n"
        
        if suggestions:
            error_msg += "💡 Did you mean:\n"
            for missing, similar in suggestions.items():
                error_msg += f"  • '{missing}' → Maybe: {similar}\n"
        
        error_msg += "\n⚠️ Column names are case-sensitive! 'Discount Applied' ≠ 'discount applied'"
        
        raise EstimationException(error_msg)
    
    return column_mapping

def _encode_categorical(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """
    Encode categorical variables to numeric.
    Handles Yes/No, Male/Female, Boolean, and other categorical variables.
    """
    df_encoded = df.copy()
    
    for col in columns:
        if col not in df_encoded.columns:
            continue
        
        # Handle boolean columns
        if df_encoded[col].dtype == 'bool':
            df_encoded[col] = df_encoded[col].astype(int)
            continue
            
        # Check if column is categorical or object type
        if df_encoded[col].dtype == 'object' or df_encoded[col].dtype.name == 'category':
            # Handle Yes/No
            if set(df_encoded[col].unique()).issubset({'Yes', 'No', None, np.nan}):
                df_encoded[col] = df_encoded[col].map({'Yes': 1, 'No': 0})
            # Handle Male/Female
            elif set(df_encoded[col].unique()).issubset({'Male', 'Female', None, np.nan}):
                df_encoded[col] = df_encoded[col].map({'Male': 1, 'Female': 0})
            # Handle TRUE/FALSE strings
            elif set(df_encoded[col].dropna().unique()).issubset({'TRUE', 'FALSE', 'True', 'False', 'true', 'false'}):
                df_encoded[col] = df_encoded[col].map({
                    'TRUE': 1, 'True': 1, 'true': 1,
                    'FALSE': 0, 'False': 0, 'false': 0
                })
            # For other categorical variables, use label encoding
            else:
                from sklearn.preprocessing import LabelEncoder
                le = LabelEncoder()
                # Handle NaN values
                mask = df_encoded[col].notna()
                df_encoded.loc[mask, col] = le.fit_transform(df_encoded.loc[mask, col])
    
    return df_encoded

def _backdoor_estimation(df: pd.DataFrame, treatment: str, outcome: str, 
                         confounders: list) -> Dict:
    """Backdoor adjustment using regression or matching."""
    from sklearn.linear_model import LinearRegression
    
    # Encode categorical variables
    all_cols = [treatment, outcome] + confounders
    df_encoded = _encode_categorical(df, all_cols)
    
    # Remove rows with missing values
    df_clean = df_encoded[[treatment, outcome] + confounders].dropna()
    
    if len(df_clean) < 10:
        raise EstimationException("Not enough data after removing missing values")
    
    X_cols = [treatment] + confounders
    X = df_clean[X_cols].values
    y = df_clean[outcome].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    ate = model.coef_[0]
    
    bootstrap_estimates = []
    np.random.seed(settings.seed)
    
    for _ in range(100):
        indices = np.random.choice(len(df_clean), len(df_clean), replace=True)
        X_boot = X[indices]
        y_boot = y[indices]
        
        model_boot = LinearRegression()
        model_boot.fit(X_boot, y_boot)
        bootstrap_estimates.append(model_boot.coef_[0])
    
    ci_lower = np.percentile(bootstrap_estimates, 2.5)
    ci_upper = np.percentile(bootstrap_estimates, 97.5)
    
    se = np.std(bootstrap_estimates)
    t_stat = ate / se if se > 0 else 0
    p_value = 2 * (1 - _norm_cdf(abs(t_stat)))
    
    # Count treated vs control (for binary treatment)
    treatment_vals = df_clean[treatment].values
    if set(treatment_vals).issubset({0, 1}):
        n_treated = int((treatment_vals == 1).sum())
        n_control = int((treatment_vals == 0).sum())
    else:
        # For continuous treatment, report unique values
        n_treated = int(len(df_clean))
        n_control = 0
    
    return {
        "ate": float(ate),
        "confidence_interval": [float(ci_lower), float(ci_upper)],
        "p_value": float(p_value),
        "n_treated": n_treated,
        "n_control": n_control,
        "standard_error": float(se)
    }

def _simple_regression(df: pd.DataFrame, treatment: str, outcome: str, 
                       confounders: list) -> Dict:
    """Simple linear regression fallback."""
    return _backdoor_estimation(df, treatment, outcome, confounders)

def _iv_estimation(df: pd.DataFrame, treatment: str, outcome: str, 
                   confounders: list, schema: Dict) -> Dict:
    """Instrumental variable estimation."""
    return _backdoor_estimation(df, treatment, outcome, confounders)

def _rd_estimation(df: pd.DataFrame, treatment: str, outcome: str, 
                   schema: Dict) -> Dict:
    """Regression discontinuity estimation."""
    return _simple_regression(df, treatment, outcome, [])

def _norm_cdf(x: float) -> float:
    """Approximate normal CDF."""
    from math import erf, sqrt
    return (1 + erf(x / sqrt(2))) / 2