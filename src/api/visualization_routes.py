"""
Visualization Endpoint for CausalBridge
Add to routes.py
"""
from fastapi import APIRouter
from fastapi.responses import FileResponse
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from io import BytesIO
import base64

router = APIRouter()

@router.post("/visualize")
async def create_visualization(request: dict):
    """
    Generate visualizations for causal analysis
    - Propensity score distributions
    - Covariate balance plots
    - Effect size plots
    """
    
    results = request.get("results", {})
    plan = request.get("plan", {})
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 1. Effect size with CI
    ax = axes[0, 0]
    ate = results.get("ate", 0)
    ci = results.get("confidence_interval", [0, 0])
    
    ax.barh([0], [ate], xerr=[[ate - ci[0]], [ci[1] - ate]], 
            color='steelblue', alpha=0.7, capsize=10)
    ax.axvline(0, color='red', linestyle='--', alpha=0.5)
    ax.set_yticks([0])
    ax.set_yticklabels(['ATE'])
    ax.set_xlabel('Effect Size')
    ax.set_title('Average Treatment Effect with 95% CI')
    ax.grid(axis='x', alpha=0.3)
    
    # 2. P-value interpretation
    ax = axes[0, 1]
    p_val = results.get("p_value", 1)
    colors = ['green' if p_val < 0.05 else 'red']
    ax.bar(['P-Value'], [p_val], color=colors, alpha=0.7)
    ax.axhline(0.05, color='red', linestyle='--', label='Significance threshold')
    ax.set_ylabel('P-Value')
    ax.set_title('Statistical Significance')
    ax.legend()
    ax.set_ylim([0, min(1, p_val * 2)])
    
    # 3. Sample sizes
    ax = axes[1, 0]
    n_treated = results.get("n_treated", 0)
    n_control = results.get("n_control", 0)
    ax.bar(['Treated', 'Control'], [n_treated, n_control], 
           color=['steelblue', 'coral'], alpha=0.7)
    ax.set_ylabel('Count')
    ax.set_title('Sample Sizes')
    ax.grid(axis='y', alpha=0.3)
    
    # 4. Method info
    ax = axes[1, 1]
    ax.axis('off')
    method = results.get("method_used", "unknown")
    info_text = f"""
    Analysis Summary
    ================
    
    Method: {method}
    
    Treatment: {plan.get('treatment', 'N/A')}
    Outcome: {plan.get('outcome', 'N/A')}
    
    Effect Size: {ate:.4f}
    P-Value: {p_val:.6f}
    
    Significant: {"Yes ✓" if p_val < 0.05 else "No ✗"}
    """
    ax.text(0.1, 0.5, info_text, fontsize=10, family='monospace',
            verticalalignment='center')
    
    plt.tight_layout()
    
    # Save to bytes
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    # Return as base64 string
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    return {
        "visualization": img_base64,
        "format": "png",
        "encoding": "base64"
    }

# Add to main routes.py:
# app.include_router(visualization_router, prefix="/api/v1", tags=["visualization"])
