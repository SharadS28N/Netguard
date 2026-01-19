#!/usr/bin/env python3
"""
NetGuard Nepal - Comprehensive Visualization Generator
Generates all benchmarks and visualizations for presentation
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import glob

from sklearn.metrics import (
    confusion_matrix, classification_report, roc_curve, auc,
    precision_recall_curve, average_precision_score
)
from sklearn.model_selection import cross_val_score
import joblib

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Create output directory
OUTPUT_DIR = "./visualizations"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 80)
print("NetGuard Nepal - Visualization Generator")
print("=" * 80)
print()


def load_latest_models():
    """Load the most recent trained models"""
    print("Loading latest models...")
    
    model_dir = "./models"
    
    # Find latest models
    rf_models = sorted(glob.glob(f"{model_dir}/rf_model_*.pkl"))
    gb_models = sorted(glob.glob(f"{model_dir}/gb_model_*.pkl"))
    ensemble_rf_models = sorted(glob.glob(f"{model_dir}/ensemble_rf_*.pkl"))
    ensemble_gb_models = sorted(glob.glob(f"{model_dir}/ensemble_gb_*.pkl"))
    scalers = sorted(glob.glob(f"{model_dir}/scaler_*.pkl"))
    
    if not rf_models or not gb_models or not scalers:
        print("❌ No trained models found. Please run train_models.py first.")
        return None
    
    models = {
        'rf': joblib.load(rf_models[-1]),
        'gb': joblib.load(gb_models[-1]),
        'scaler': joblib.load(scalers[-1])
    }
    
    if ensemble_rf_models and ensemble_gb_models:
        models['ensemble_rf'] = joblib.load(ensemble_rf_models[-1])
        models['ensemble_gb'] = joblib.load(ensemble_gb_models[-1])
    
    print(f"✓ Loaded models from {model_dir}")
    return models


def generate_synthetic_data(n_samples=2000):
    """Generate synthetic test data"""
    print(f"Generating {n_samples} synthetic samples...")
    
    np.random.seed(42)
    
    # Generate features
    legitimate_samples = n_samples // 2
    evil_twin_samples = n_samples - legitimate_samples
    
    # Legitimate networks
    legitimate_features = np.column_stack([
        np.random.normal(-60, 10, legitimate_samples),  # signal_strength
        np.random.uniform(0, 0.1, legitimate_samples),  # channel_variance
        np.random.choice([0.8, 0.9, 1.0], legitimate_samples),  # encryption (WPA2/WPA3)
        np.random.uniform(0.8, 1.0, legitimate_samples),  # vendor_consistency
        np.random.uniform(0, 0.2, legitimate_samples),  # behavior_anomaly
        np.random.uniform(0, 0.2, legitimate_samples),  # traffic_anomaly
        np.random.uniform(0.3, 0.8, legitimate_samples),  # client_count_ratio
        np.random.uniform(0, 0.3, legitimate_samples),  # ssid_similarity
    ])
    
    # Evil twin networks
    evil_twin_features = np.column_stack([
        np.random.normal(-50, 15, evil_twin_samples),  # signal_strength (stronger)
        np.random.uniform(0.3, 0.8, evil_twin_samples),  # channel_variance (unstable)
        np.random.choice([0.0, 0.3, 0.5], evil_twin_samples),  # encryption (Open/WEP)
        np.random.uniform(0, 0.5, evil_twin_samples),  # vendor_consistency (low)
        np.random.uniform(0.5, 1.0, evil_twin_samples),  # behavior_anomaly (high)
        np.random.uniform(0.5, 1.0, evil_twin_samples),  # traffic_anomaly (high)
        np.random.uniform(0, 0.3, evil_twin_samples),  # client_count_ratio (low)
        np.random.uniform(0.6, 1.0, evil_twin_samples),  # ssid_similarity (high)
    ])
    
    # Combine
    X = np.vstack([legitimate_features, evil_twin_features])
    y = np.hstack([np.zeros(legitimate_samples), np.ones(evil_twin_samples)])
    
    # Shuffle
    indices = np.random.permutation(len(X))
    X = X[indices]
    y = y[indices]
    
    print(f"✓ Generated {len(X)} samples")
    return X, y


def plot_model_accuracy_comparison(models, X_test, y_test):
    """Compare accuracy of all models"""
    print("\n📊 Generating Model Accuracy Comparison...")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    model_names = []
    accuracies = []
    precisions = []
    recalls = []
    f1_scores = []
    
    for name, model in models.items():
        if name == 'scaler':
            continue
            
        y_pred = model.predict(X_test)
        
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        model_names.append(name.upper())
        accuracies.append(acc)
        precisions.append(prec)
        recalls.append(rec)
        f1_scores.append(f1)
    
    x = np.arange(len(model_names))
    width = 0.2
    
    ax.bar(x - 1.5*width, accuracies, width, label='Accuracy', alpha=0.8)
    ax.bar(x - 0.5*width, precisions, width, label='Precision', alpha=0.8)
    ax.bar(x + 0.5*width, recalls, width, label='Recall', alpha=0.8)
    ax.bar(x + 1.5*width, f1_scores, width, label='F1-Score', alpha=0.8)
    
    ax.set_xlabel('Model', fontsize=12, fontweight='bold')
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Model Performance Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(model_names)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 1.1])
    
    # Add value labels on bars
    for i, (acc, prec, rec, f1) in enumerate(zip(accuracies, precisions, recalls, f1_scores)):
        ax.text(i - 1.5*width, acc + 0.02, f'{acc:.3f}', ha='center', va='bottom', fontsize=8)
        ax.text(i - 0.5*width, prec + 0.02, f'{prec:.3f}', ha='center', va='bottom', fontsize=8)
        ax.text(i + 0.5*width, rec + 0.02, f'{rec:.3f}', ha='center', va='bottom', fontsize=8)
        ax.text(i + 1.5*width, f1 + 0.02, f'{f1:.3f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/01_model_accuracy_comparison.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: 01_model_accuracy_comparison.png")


def plot_confusion_matrices(models, X_test, y_test):
    """Generate confusion matrices for all models"""
    print("\n📊 Generating Confusion Matrices...")
    
    model_list = [(name, model) for name, model in models.items() if name != 'scaler']
    
    fig, axes = plt.subplots(1, len(model_list), figsize=(6*len(model_list), 5))
    
    if len(model_list) == 1:
        axes = [axes]
    
    for idx, (name, model) in enumerate(model_list):
        y_pred = model.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx],
                    xticklabels=['Legitimate', 'Evil Twin'],
                    yticklabels=['Legitimate', 'Evil Twin'])
        
        axes[idx].set_title(f'{name.upper()} Model', fontsize=12, fontweight='bold')
        axes[idx].set_ylabel('True Label', fontsize=10)
        axes[idx].set_xlabel('Predicted Label', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/02_confusion_matrices.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: 02_confusion_matrices.png")


def plot_roc_curves(models, X_test, y_test):
    """Generate ROC curves with AUC scores"""
    print("\n📊 Generating ROC Curves...")
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    
    for idx, (name, model) in enumerate(models.items()):
        if name == 'scaler':
            continue
        
        # Get probability predictions
        if hasattr(model, 'predict_proba'):
            y_proba = model.predict_proba(X_test)[:, 1]
        else:
            y_proba = model.decision_function(X_test)
        
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc = auc(fpr, tpr)
        
        ax.plot(fpr, tpr, color=colors[idx % len(colors)], lw=2,
                label=f'{name.upper()} (AUC = {roc_auc:.3f})')
    
    ax.plot([0, 1], [0, 1], 'k--', lw=2, label='Random Classifier')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate', fontsize=12, fontweight='bold')
    ax.set_ylabel('True Positive Rate', fontsize=12, fontweight='bold')
    ax.set_title('ROC Curves - Model Comparison', fontsize=14, fontweight='bold')
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/03_roc_curves.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: 03_roc_curves.png")


def plot_precision_recall_curves(models, X_test, y_test):
    """Generate Precision-Recall curves"""
    print("\n📊 Generating Precision-Recall Curves...")
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    
    for idx, (name, model) in enumerate(models.items()):
        if name == 'scaler':
            continue
        
        if hasattr(model, 'predict_proba'):
            y_proba = model.predict_proba(X_test)[:, 1]
        else:
            y_proba = model.decision_function(X_test)
        
        precision, recall, _ = precision_recall_curve(y_test, y_proba)
        avg_precision = average_precision_score(y_test, y_proba)
        
        ax.plot(recall, precision, color=colors[idx % len(colors)], lw=2,
                label=f'{name.upper()} (AP = {avg_precision:.3f})')
    
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('Recall', fontsize=12, fontweight='bold')
    ax.set_ylabel('Precision', fontsize=12, fontweight='bold')
    ax.set_title('Precision-Recall Curves', fontsize=14, fontweight='bold')
    ax.legend(loc="lower left", fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/04_precision_recall_curves.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: 04_precision_recall_curves.png")


def plot_feature_importance(models, X_test):
    """Plot feature importance for tree-based models"""
    print("\n📊 Generating Feature Importance Charts...")
    
    feature_names = [
        'Signal Strength',
        'Channel Variance',
        'Encryption Type',
        'Vendor Consistency',
        'Behavior Anomaly',
        'Traffic Anomaly',
        'Client Count Ratio',
        'SSID Similarity'
    ]
    
    # Filter tree-based models
    tree_models = {name: model for name, model in models.items() 
                   if name in ['rf', 'gb'] and hasattr(model, 'feature_importances_')}
    
    if not tree_models:
        print("⚠ No tree-based models with feature_importances_ found")
        return
    
    fig, axes = plt.subplots(1, len(tree_models), figsize=(8*len(tree_models), 6))
    
    if len(tree_models) == 1:
        axes = [axes]
    
    for idx, (name, model) in enumerate(tree_models.items()):
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        axes[idx].barh(range(len(importances)), importances[indices], alpha=0.8)
        axes[idx].set_yticks(range(len(importances)))
        axes[idx].set_yticklabels([feature_names[i] for i in indices])
        axes[idx].set_xlabel('Importance', fontsize=10, fontweight='bold')
        axes[idx].set_title(f'{name.upper()} Feature Importance', fontsize=12, fontweight='bold')
        axes[idx].grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, v in enumerate(importances[indices]):
            axes[idx].text(v + 0.01, i, f'{v:.3f}', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/05_feature_importance.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: 05_feature_importance.png")


def plot_cross_validation_scores(models, X, y):
    """Plot cross-validation scores"""
    print("\n📊 Generating Cross-Validation Scores...")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    model_names = []
    cv_means = []
    cv_stds = []
    
    for name, model in models.items():
        if name == 'scaler':
            continue
        
        print(f"  Running 5-fold CV for {name.upper()}...")
        scores = cross_val_score(model, X, y, cv=5, scoring='accuracy', n_jobs=-1)
        
        model_names.append(name.upper())
        cv_means.append(scores.mean())
        cv_stds.append(scores.std())
    
    x = np.arange(len(model_names))
    
    ax.bar(x, cv_means, yerr=cv_stds, alpha=0.8, capsize=10, color='skyblue', edgecolor='navy')
    ax.set_xlabel('Model', fontsize=12, fontweight='bold')
    ax.set_ylabel('Accuracy', fontsize=12, fontweight='bold')
    ax.set_title('5-Fold Cross-Validation Scores', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(model_names)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim([0, 1.1])
    
    # Add value labels
    for i, (mean, std) in enumerate(zip(cv_means, cv_stds)):
        ax.text(i, mean + std + 0.02, f'{mean:.3f} ± {std:.3f}', 
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/06_cross_validation_scores.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: 06_cross_validation_scores.png")


def plot_confidence_distribution(models, X_test):
    """Plot confidence score distribution"""
    print("\n📊 Generating Confidence Distribution...")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for idx, (name, model) in enumerate(models.items()):
        if name == 'scaler' or idx >= 4:
            continue
        
        if hasattr(model, 'predict_proba'):
            y_proba = model.predict_proba(X_test)
            confidence = np.max(y_proba, axis=1)
        else:
            continue
        
        axes[idx].hist(confidence, bins=50, alpha=0.7, color='steelblue', edgecolor='black')
        axes[idx].set_xlabel('Confidence Score', fontsize=10, fontweight='bold')
        axes[idx].set_ylabel('Frequency', fontsize=10, fontweight='bold')
        axes[idx].set_title(f'{name.upper()} Confidence Distribution', fontsize=12, fontweight='bold')
        axes[idx].grid(True, alpha=0.3)
        
        # Add statistics
        mean_conf = np.mean(confidence)
        median_conf = np.median(confidence)
        axes[idx].axvline(mean_conf, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_conf:.3f}')
        axes[idx].axvline(median_conf, color='green', linestyle='--', linewidth=2, label=f'Median: {median_conf:.3f}')
        axes[idx].legend()
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/07_confidence_distribution.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: 07_confidence_distribution.png")


def plot_detection_pipeline_metrics():
    """Plot detection pipeline performance metrics"""
    print("\n📊 Generating Detection Pipeline Metrics...")
    
    # Simulated pipeline metrics
    phases = ['Phase 1\nScanning', 'Phase 2\nFeatures', 'Phase 3\nAnomaly', 'Phase 4\nDecision']
    avg_time = [2.5, 0.8, 1.2, 0.5]  # seconds
    throughput = [400, 1250, 833, 2000]  # items/sec
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Processing time
    bars1 = ax1.bar(phases, avg_time, alpha=0.8, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    ax1.set_ylabel('Average Time (seconds)', fontsize=12, fontweight='bold')
    ax1.set_title('Pipeline Phase Processing Time', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    for bar, time in zip(bars1, avg_time):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{time}s', ha='center', va='bottom', fontweight='bold')
    
    # Throughput
    bars2 = ax2.bar(phases, throughput, alpha=0.8, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    ax2.set_ylabel('Throughput (items/sec)', fontsize=12, fontweight='bold')
    ax2.set_title('Pipeline Phase Throughput', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    for bar, tp in zip(bars2, throughput):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 50,
                f'{tp}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/08_pipeline_metrics.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: 08_pipeline_metrics.png")


def plot_threat_level_distribution():
    """Plot threat level distribution"""
    print("\n📊 Generating Threat Level Distribution...")
    
    # Simulated threat data
    threat_levels = ['Benign', 'Suspicious', 'Likely\nEvil Twin', 'Confirmed\nEvil Twin']
    counts = [750, 180, 50, 20]
    colors = ['#2ECC71', '#F39C12', '#E74C3C', '#C0392B']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Bar chart
    bars = ax1.bar(threat_levels, counts, alpha=0.8, color=colors)
    ax1.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax1.set_title('Threat Level Distribution', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 10,
                f'{count}', ha='center', va='bottom', fontweight='bold')
    
    # Pie chart
    ax2.pie(counts, labels=threat_levels, autopct='%1.1f%%', colors=colors,
            startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
    ax2.set_title('Threat Level Percentage', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/09_threat_distribution.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: 09_threat_distribution.png")


def generate_summary_report(models, X_test, y_test):
    """Generate comprehensive summary report"""
    print("\n📊 Generating Summary Report...")
    
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'models': {}
    }
    
    for name, model in models.items():
        if name == 'scaler':
            continue
        
        y_pred = model.predict(X_test)
        
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        report_data['models'][name] = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred)),
            'recall': float(recall_score(y_test, y_pred)),
            'f1_score': float(f1_score(y_test, y_pred)),
            'classification_report': classification_report(y_test, y_pred, 
                                                          target_names=['Legitimate', 'Evil Twin'],
                                                          output_dict=True)
        }
    
    # Save as JSON
    with open(f"{OUTPUT_DIR}/model_performance_report.json", 'w') as f:
        json.dump(report_data, f, indent=2)
    
    # Create markdown report
    md_report = f"""# NetGuard Nepal - Model Performance Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Model Performance Summary

"""
    
    for name, metrics in report_data['models'].items():
        md_report += f"""### {name.upper()} Model

- **Accuracy**: {metrics['accuracy']:.4f}
- **Precision**: {metrics['precision']:.4f}
- **Recall**: {metrics['recall']:.4f}
- **F1-Score**: {metrics['f1_score']:.4f}

"""
    
    with open(f"{OUTPUT_DIR}/PERFORMANCE_REPORT.md", 'w') as f:
        f.write(md_report)
    
    print(f"✓ Saved: model_performance_report.json")
    print(f"✓ Saved: PERFORMANCE_REPORT.md")


def main():
    """Main execution"""
    print("\n🚀 Starting visualization generation...\n")
    
    # Load models
    models = load_latest_models()
    if not models:
        return
    
    # Generate test data
    X, y = generate_synthetic_data(n_samples=2000)
    
    # Scale features
    X_scaled = models['scaler'].transform(X)
    
    # Split for testing
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    
    print(f"\nTest set size: {len(X_test)} samples")
    print(f"Class distribution: {np.bincount(y_test.astype(int))}")
    
    # Generate all visualizations
    plot_model_accuracy_comparison(models, X_test, y_test)
    plot_confusion_matrices(models, X_test, y_test)
    plot_roc_curves(models, X_test, y_test)
    plot_precision_recall_curves(models, X_test, y_test)
    plot_feature_importance(models, X_test)
    plot_cross_validation_scores(models, X_scaled, y)
    plot_confidence_distribution(models, X_test)
    plot_detection_pipeline_metrics()
    plot_threat_level_distribution()
    generate_summary_report(models, X_test, y_test)
    
    print("\n" + "=" * 80)
    print("✅ ALL VISUALIZATIONS GENERATED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\n📁 Output directory: {os.path.abspath(OUTPUT_DIR)}")
    print(f"\n📊 Generated {len(os.listdir(OUTPUT_DIR))} files:")
    for file in sorted(os.listdir(OUTPUT_DIR)):
        print(f"   - {file}")
    print()


if __name__ == "__main__":
    main()
