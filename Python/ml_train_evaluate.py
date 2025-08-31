import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve, auc
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import randint

def generate_complex_data(num_samples=2000, n_features=20, random_seed=42):
    """
    복잡한 이진 분류를 위한 가상의 데이터셋을 생성합니다.
    일부 특성은 노이즈가 포함되어 있고, 일부 특성은 타겟 변수와 선형/비선형 관계를 가집니다.
    """
    np.random.seed(random_seed)
    
    X = np.random.randn(num_samples, n_features)
    
    # 타겟 변수 생성 (여러 특성들의 복잡한 조합)
    # feature_0, feature_1, feature_2는 중요한 특성
    # feature_3, feature_4는 비선형 관계를 가짐
    # 나머지는 노이즈
    y_raw = (
        2 * X[:, 0] 
        - 3 * X[:, 1]**2 
        + 1.5 * np.sin(X[:, 2]) 
        + 0.5 * X[:, 3] * X[:, 4] 
        + np.random.randn(num_samples) * 0.5  # 노이즈 추가
    )
    
    # 0과 1로 분류
    y = (y_raw > np.median(y_raw)).astype(int)
    
    column_names = [f'feature_{i}' for i in range(n_features)]
    
    print(f"데이터셋 생성 완료: {num_samples} 샘플, {n_features} 특성")
    return pd.DataFrame(X, columns=column_names), pd.Series(y, name='target')

def train_and_evaluate_models(X_train, X_test, y_train, y_test):
    """
    여러 머신러닝 모델을 학습하고 평가합니다.
    """
    
    classifiers = {
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
        'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=5),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Random Forest': RandomForestClassifier(random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(random_state=42),
        'Support Vector Machine': SVC(random_state=42, probability=True),
        'Naive Bayes': GaussianNB(),
        'Neural Network': MLPClassifier(random_state=42, max_iter=500, hidden_layer_sizes=(100, 50))
    }
    
    results = {}
    
    print("모델 학습 및 평가 시작...")
    
    for name, classifier in classifiers.items():
        print(f"\n--- {name} 모델 학습 중 ---")
        try:
            classifier.fit(X_train, y_train)
            y_pred = classifier.predict(X_test)
            
            metrics = {
                'Accuracy': accuracy_score(y_test, y_pred),
                'Precision': precision_score(y_test, y_pred),
                'Recall': recall_score(y_test, y_pred),
                'F1-Score': f1_score(y_test, y_pred)
            }
            
            if hasattr(classifier, "predict_proba"):
                y_proba = classifier.predict_proba(X_test)[:, 1]
                metrics['ROC AUC'] = roc_auc_score(y_test, y_proba)
                
            results[name] = metrics
            
            print(f"{name} 평가 완료:")
            for metric, value in metrics.items():
                print(f"  - {metric}: {value:.4f}")
            
        except Exception as e:
            print(f"모델 학습 중 오류 발생: {e}")
            results[name] = "오류"
            
    return results

def plot_metrics(results):
    """
    모델별 주요 평가지표를 시각화합니다.
    """
    
    df_results = pd.DataFrame(results).T
    
    plt.style.use('seaborn-v0_8-whitegrid')
    
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    fig.suptitle('머신러닝 모델별 성능 비교', fontsize=20, y=1.02)
    
    metrics_to_plot = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    
    for i, metric in enumerate(metrics_to_plot):
        row = i // 2
        col = i % 2
        ax = axes[row, col]
        
        df_results[metric].sort_values(ascending=False).plot(kind='barh', ax=ax, color=plt.cm.Paired.colors)
        ax.set_title(f'{metric} 비교', fontsize=15)
        ax.set_xlabel(metric, fontsize=12)
        ax.grid(axis='x')
        
        for index, value in enumerate(df_results[metric].sort_values(ascending=False)):
            ax.text(value, index, f'{value:.4f}', ha='left', va='center')
            
    plt.tight_layout()
    plt.show()

def plot_roc_curves(X_test, y_test, models):
    """
    모델별 ROC 곡선을 시각화합니다.
    """
    
    plt.figure(figsize=(10, 8))
    plt.title('모델별 ROC 곡선', fontsize=16)
    plt.plot([0, 1], [0, 1], 'k--', label='랜덤 (AUC = 0.50)')
    
    for name, model in models.items():
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X_test)[:, 1]
            fpr, tpr, _ = roc_curve(y_test, y_proba)
            roc_auc = auc(fpr, tpr)
            plt.plot(fpr, tpr, label=f'{name} (AUC = {roc_auc:.4f})')
            
    plt.xlabel('위양성률 (False Positive Rate)', fontsize=12)
    plt.ylabel('재현율 (True Positive Rate)', fontsize=12)
    plt.legend(loc='lower right')
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    
    # 1. 데이터 생성
    X, y = generate_complex_data(num_samples=2500, n_features=25)
    
    # 2. 데이터 분할
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    print(f"\n데이터 분할 완료. 학습 세트: {len(X_train)}개, 테스트 세트: {len(X_test)}개")
    
    # 3. 데이터 스케일링
    # SVC와 Neural Network는 스케일링이 필수적입니다.
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print("데이터 스케일링 완료.")
    
    # 스케일링된 데이터를 사용하는 모델과 그렇지 않은 모델을 구분
    models = {
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
        'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=5),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Random Forest': RandomForestClassifier(random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(random_state=42),
        'Support Vector Machine': SVC(random_state=42, probability=True),
        'Naive Bayes': GaussianNB(),
        'Neural Network': MLPClassifier(random_state=42, max_iter=500, hidden_layer_sizes=(100, 50))
    }
    
    # 각 모델에 적합한 데이터셋을 사용하여 학습
    trained_models = {}
    results = {}
    
    for name, model in models.items():
        print(f"\n--- {name} 모델 학습 시작 ---")
        
        # 스케일링이 필요한 모델
        if name in ['Logistic Regression', 'Support Vector Machine', 'Neural Network', 'K-Nearest Neighbors']:
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            if hasattr(model, "predict_proba"):
                y_proba = model.predict_proba(X_test_scaled)[:, 1]
        else: # 스케일링이 필요 없는 모델
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            if hasattr(model, "predict_proba"):
                y_proba = model.predict_proba(X_test)[:, 1]

        trained_models[name] = model

        # 평가 지표 계산
        metrics = {
            'Accuracy': accuracy_score(y_test, y_pred),
            'Precision': precision_score(y_test, y_pred),
            'Recall': recall_score(y_test, y_pred),
            'F1-Score': f1_score(y_test, y_pred)
        }
        
        if hasattr(model, "predict_proba"):
            metrics['ROC AUC'] = roc_auc_score(y_test, y_proba)
            
        results[name] = metrics
        
        print(f"{name} 평가 완료:")
        for metric, value in metrics.items():
            print(f"  - {metric}: {value:.4f}")
            
    # 5. 결과 시각화
    print("\n모델 성능 시각화...")
    plot_metrics(results)
    
    # ROC 곡선 시각화
    print("\n모델별 ROC 곡선 시각화...")
    plot_roc_curves(X_test_scaled, y_test, trained_models)
    
    print("\n전체 프로세스 완료.")