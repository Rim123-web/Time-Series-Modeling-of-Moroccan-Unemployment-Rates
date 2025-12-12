from flask import Flask, render_template, request, jsonify
import pickle
import os
from datetime import datetime
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif
import matplotlib.pyplot as plt
import base64
import io

app = Flask(__name__)

# Noms des trimestres
quarter_names = {1: 'T1', 2: 'T2', 3: 'T3', 4: 'T4'}

# Structure hiérarchique des catégories
CATEGORY_HIERARCHY = {
    'Ensemble': {
        'model': 'sarima_model.pkl',
        'subcategories': None,
        'excel_column': 'Ensemble',
        'color': '#006233'  # Vert marocain
    },
    'Milieu': {
        'model': None,
        'subcategories': {
            'Urbain': {
                'model': 'sarima_urbain.pkl',
                'excel_column': 'Urbain',
                'color': '#0066CC'  # Bleu
            },
            'Rural': {
                'model': 'sarima_rural.pkl',
                'excel_column': 'Rural',
                'color': '#FF6600'  # Orange
            }
        }
    },
    'Genre': {
        'model': None,
        'subcategories': {
            'Féminin': {
                'model': 'sarima_feminin.pkl',
                'excel_column': None,  # Pas dans Excel
                'color': '#FF69B4'  # Rose
            },
            'Masculin': {
                'model': 'sarima_masculin.pkl',
                'excel_column': None,
                'color': '#4169E1'  # Bleu royal
            }
        }
    },
    'Tranche d\'âge': {
        'model': None,
        'subcategories': {
            'Age 15-24': {
                'model': 'sarima_age_15_24.pkl',
                'excel_column': None,
                'color': '#FF4500'  # Orange rouge
            },
            'Age 25-34': {
                'model': 'sarima_age_25_34.pkl',
                'excel_column': None,
                'color': '#FF8C00'  # Orange foncé
            },
            'Age 35-44': {
                'model': 'sarima_age_35_44.pkl',
                'excel_column': None,
                'color': '#FFA500'  # Orange
            },
            'Age 45+': {
                'model': 'sarima_age_45_plus.pkl',
                'excel_column': None,
                'color': '#FF6347'  # Tomate
            }
        }
    },
    'Niveau d\'éducation': {
        'model': None,
        'subcategories': {
            'Sans diplôme': {
                'model': 'sarima_sans_diplome.pkl',
                'excel_column': None,
                'color': '#8B0000'  # Rouge foncé
            },
            'Niveau moyen': {
                'model': 'sarima_niveau_moyen.pkl',
                'excel_column': None,
                'color': '#228B22'  # Vert forêt
            },
            'Niveau supérieur': {
                'model': 'sarima_niveau_superieur.pkl',
                'excel_column': None,
                'color': '#32CD32'  # Vert lime
            }
        }
    }
}

# Mapping plat pour compatibilité (catégorie finale -> modèle)
CATEGORY_MODELS = {}
CATEGORY_COLORS = {}
for main_cat, info in CATEGORY_HIERARCHY.items():
    if info['model']:
        CATEGORY_MODELS[main_cat] = info['model']
        CATEGORY_COLORS[main_cat] = info.get('color', '#C1272D')
    if info['subcategories']:
        for sub_cat, sub_info in info['subcategories'].items():
            CATEGORY_MODELS[sub_cat] = sub_info['model']
            CATEGORY_COLORS[sub_cat] = sub_info.get('color', '#C1272D')

# Cache pour les modèles chargés
loaded_models = {}

# Cache pour les données Excel
df_data = None


def load_model(category):
    """Charge un modèle depuis le cache ou depuis le fichier"""
    if category in loaded_models:
        return loaded_models[category]
    
    if category not in CATEGORY_MODELS:
        raise ValueError(f"Catégorie '{category}' non trouvée")
    
    model_path = CATEGORY_MODELS[category]
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Modèle '{model_path}' non trouvé")
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    loaded_models[category] = model
    return model


def load_data():
    """Charge les données Excel en cache"""
    global df_data
    if df_data is None:
        df_data = pd.read_excel('Taux de chômage_Maroc-Dataset.xlsx')
        # Trier par trimestre
        if 'Trimestre' in df_data.columns:
            df_data = df_data.sort_values('Trimestre')
    return df_data


def get_model_fitted_values(category_name):
    """Récupère les valeurs ajustées du modèle SARIMA pour une catégorie"""
    try:
        model = load_model(category_name)
        fitted = None
        
        # Essayer différentes méthodes pour obtenir les fitted values
        if hasattr(model, 'fittedvalues'):
            fitted = model.fittedvalues
        elif hasattr(model, 'fitted_values'):
            fitted = model.fitted_values
        elif hasattr(model, 'predict'):
            try:
                # Essayer de prédire sur les données d'entraînement
                fitted = model.predict()
            except:
                try:
                    # Essayer avec start et end
                    fitted = model.predict(start=0)
                except:
                    pass
        
        if fitted is None:
            return None
        
        # Convertir en array numpy si nécessaire
        if hasattr(fitted, 'values'):
            fitted_values = fitted.values
        elif hasattr(fitted, 'iloc'):
            fitted_values = fitted.iloc[:].values
        elif isinstance(fitted, (list, tuple)):
            fitted_values = pd.Series(fitted).values
        else:
            try:
                fitted_values = pd.Series(fitted).values
            except:
                return None
        
        # Générer des trimestres pour les fitted values
        # Utiliser les trimestres du fichier Excel comme référence
        df = load_data()
        n_periods = len(fitted_values)
        n_data = len(df)
        
        # Utiliser les trimestres existants ou générer
        if n_periods <= n_data:
            quarters = df['Trimestre'].iloc[:n_periods].tolist()
        else:
            # Générer des trimestres à partir de la dernière date du fichier Excel
            last_quarter = df['Trimestre'].iloc[-1]
            # Extraire l'année et le trimestre
            try:
                year = int(last_quarter[:4])
                quarter = int(last_quarter[-1])
            except:
                year = 2023
                quarter = 4
            
            quarters = []
            for i in range(n_periods):
                q = quarter - (n_periods - i - 1)
                y = year
                while q <= 0:
                    q += 4
                    y -= 1
                while q > 4:
                    q -= 4
                    y += 1
                quarters.append(f"{y}T{q}")
        
        return pd.DataFrame({'Trimestre': quarters, 'Valeur': fitted_values})
    except Exception as e:
        print(f"Erreur pour {category_name}: {str(e)}")
        return None


def generate_trend_plot(category_name, column_name, color):
    """Génère un graphique de tendance avec moyenne mobile centrée depuis Excel"""
    try:
        df = load_data()
        
        if column_name not in df.columns:
            return None
        
        # Calcul de la tendance avec moyenne mobile centrée (fenêtre = 4 trimestres)
        df_copy = df.copy()
        df_copy['Tendance'] = df_copy[column_name].rolling(window=4, center=True).mean()
        
        # Supprimer les NaN
        df_copy = df_copy.dropna()
        
        if len(df_copy) == 0:
            return None
        
        # Créer le graphique avec figure explicite
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(df_copy['Trimestre'], df_copy[column_name], label=category_name, color=color, linewidth=2, marker='o', markersize=3)
        ax.plot(df_copy['Trimestre'], df_copy['Tendance'], linewidth=3, label=f'Tendance {category_name}', color='#003366', linestyle='--')
        ax.tick_params(axis='x', rotation=90, labelsize=9)
        ax.set_title(f"Tendance du chômage – {category_name}", fontsize=16, fontweight='bold', color='#003366', pad=20)
        ax.set_xlabel('Trimestre', fontsize=12, fontweight='bold')
        ax.set_ylabel('Taux de chômage (%)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=11, loc='best')
        fig.tight_layout()
        
        # S'assurer que le canvas est initialisé
        if fig.canvas is None:
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            FigureCanvasAgg(fig)
        
        # Convertir en base64
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return img_base64
    except Exception as e:
        print(f"Erreur dans generate_trend_plot pour {category_name}: {str(e)}")
        if 'fig' in locals():
            plt.close(fig)
        return None


def generate_trend_plot_from_model(category_name, color):
    """Génère un graphique de tendance avec moyenne mobile centrée depuis le modèle SARIMA"""
    try:
        df_fitted = get_model_fitted_values(category_name)
        
        if df_fitted is None or len(df_fitted) == 0:
            return None
        
        # Calcul de la tendance avec moyenne mobile centrée (fenêtre = 4 trimestres)
        df_fitted['Tendance'] = df_fitted['Valeur'].rolling(window=4, center=True).mean()
        
        # Supprimer les NaN
        df_fitted = df_fitted.dropna()
        
        if len(df_fitted) == 0:
            return None
        
        # Créer le graphique avec figure explicite
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(df_fitted['Trimestre'], df_fitted['Valeur'], label=category_name, color=color, linewidth=2, marker='o', markersize=3)
        ax.plot(df_fitted['Trimestre'], df_fitted['Tendance'], linewidth=3, label=f'Tendance {category_name}', color='#003366', linestyle='--')
        ax.tick_params(axis='x', rotation=90, labelsize=9)
        ax.set_title(f"Tendance du chômage – {category_name}", fontsize=16, fontweight='bold', color='#003366', pad=20)
        ax.set_xlabel('Trimestre', fontsize=12, fontweight='bold')
        ax.set_ylabel('Taux de chômage (%)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=11, loc='best')
        fig.tight_layout()
        
        # S'assurer que le canvas est initialisé
        if fig.canvas is None:
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            FigureCanvasAgg(fig)
        
        # Convertir en base64
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return img_base64
    except Exception as e:
        print(f"Erreur dans generate_trend_plot_from_model pour {category_name}: {str(e)}")
        if 'fig' in locals():
            plt.close(fig)
        return None


def generate_simple_plot(category_name, column_name, color):
    """Génère un graphique simple du taux de chômage"""
    try:
        df = load_data()
        
        if column_name not in df.columns:
            return None
        
        # Supprimer les NaN
        df_clean = df[['Trimestre', column_name]].dropna()
        
        if len(df_clean) == 0:
            return None
        
        # Créer le graphique avec figure explicite
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(df_clean['Trimestre'], df_clean[column_name], label=category_name, color=color, linewidth=2, marker='o', markersize=4)
        ax.tick_params(axis='x', rotation=90, labelsize=9)
        ax.set_title(f"Taux de chômage – {category_name}", fontsize=16, fontweight='bold', color='#003366', pad=20)
        ax.set_xlabel('Trimestre', fontsize=12, fontweight='bold')
        ax.set_ylabel('Taux de chômage (%)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=11, loc='best')
        fig.tight_layout()
        
        # S'assurer que le canvas est initialisé
        if fig.canvas is None:
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            FigureCanvasAgg(fig)
        
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return img_base64
    except Exception as e:
        print(f"Erreur dans generate_simple_plot pour {category_name}: {str(e)}")
        if 'fig' in locals():
            plt.close(fig)
        return None


def generate_simple_plot_from_model(category_name, color):
    """Génère un graphique simple depuis le modèle SARIMA"""
    try:
        df_fitted = get_model_fitted_values(category_name)
        
        if df_fitted is None or len(df_fitted) == 0:
            return None
        
        # Supprimer les NaN
        df_clean = df_fitted.dropna()
        
        if len(df_clean) == 0:
            return None
        
        # Créer le graphique avec figure explicite
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(df_clean['Trimestre'], df_clean['Valeur'], label=category_name, color=color, linewidth=2, marker='o', markersize=4)
        ax.tick_params(axis='x', rotation=90, labelsize=9)
        ax.set_title(f"Taux de chômage – {category_name}", fontsize=16, fontweight='bold', color='#003366', pad=20)
        ax.set_xlabel('Trimestre', fontsize=12, fontweight='bold')
        ax.set_ylabel('Taux de chômage (%)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=11, loc='best')
        fig.tight_layout()
        
        # S'assurer que le canvas est initialisé
        if fig.canvas is None:
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            FigureCanvasAgg(fig)
        
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return img_base64
    except Exception as e:
        print(f"Erreur dans generate_simple_plot_from_model pour {category_name}: {str(e)}")
        if 'fig' in locals():
            plt.close(fig)
        return None


def generate_comparison_bar_chart():
    """Génère un graphique en barres comparant toutes les catégories"""
    categories_data = {}
    df = load_data()
    
    # Récupérer les dernières valeurs pour chaque catégorie
    for main_cat, info in CATEGORY_HIERARCHY.items():
        if info.get('excel_column') and info['excel_column'] in df.columns:
            last_value = df[info['excel_column']].iloc[-1]
            categories_data[main_cat] = {
                'value': last_value,
                'color': info.get('color', '#003366')
            }
        
        if info.get('subcategories'):
            for sub_cat, sub_info in info['subcategories'].items():
                if sub_info.get('excel_column') and sub_info['excel_column'] in df.columns:
                    last_value = df[sub_info['excel_column']].iloc[-1]
                    categories_data[sub_cat] = {
                        'value': last_value,
                        'color': sub_info.get('color', '#003366')
                    }
                elif sub_info.get('model'):
                    # Essayer d'obtenir la dernière valeur du modèle
                    try:
                        df_fitted = get_model_fitted_values(sub_cat)
                        if df_fitted is not None and len(df_fitted) > 0:
                            last_value = df_fitted['Valeur'].iloc[-1]
                            categories_data[sub_cat] = {
                                'value': last_value,
                                'color': sub_info.get('color', '#003366')
                            }
                    except:
                        pass
    
    if not categories_data:
        return None
    
    # Trier par valeur
    sorted_data = sorted(categories_data.items(), key=lambda x: x[1]['value'], reverse=True)
    categories = [item[0] for item in sorted_data]
    values = [item[1]['value'] for item in sorted_data]
    colors = [item[1]['color'] for item in sorted_data]
    
    # Créer le graphique avec figure explicite
    fig, ax = plt.subplots(figsize=(16, 8))
    bars = ax.bar(range(len(categories)), values, color=colors, alpha=0.8, edgecolor='#003366', linewidth=1.5)
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=10)
    ax.set_ylabel('Taux de chômage (%)', fontsize=12, fontweight='bold')
    ax.set_title('Comparaison du taux de chômage par catégorie', fontsize=16, fontweight='bold', color='#003366', pad=20)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    # Ajouter les valeurs sur les barres
    for i, (bar, val) in enumerate(zip(bars, values)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{val:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    fig.tight_layout()
    
    # S'assurer que le canvas est initialisé
    if fig.canvas is None:
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        FigureCanvasAgg(fig)
    
    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    plt.close(fig)
    
    return img_base64


def generate_area_plot(category_name, column_name, color):
    """Génère un graphique en aires pour une catégorie"""
    try:
        df = load_data()
        
        if column_name not in df.columns:
            return None
        
        df_clean = df[['Trimestre', column_name]].dropna()
        
        if len(df_clean) == 0:
            return None
        
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.fill_between(df_clean['Trimestre'], df_clean[column_name], alpha=0.4, color=color, label=category_name)
        ax.plot(df_clean['Trimestre'], df_clean[column_name], color=color, linewidth=2, marker='o', markersize=3)
        ax.tick_params(axis='x', rotation=90, labelsize=9)
        ax.set_title(f"Évolution du chômage – {category_name}", fontsize=16, fontweight='bold', color='#003366', pad=20)
        ax.set_xlabel('Trimestre', fontsize=12, fontweight='bold')
        ax.set_ylabel('Taux de chômage (%)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=11, loc='best')
        fig.tight_layout()
        
        if fig.canvas is None:
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            FigureCanvasAgg(fig)
        
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return img_base64
    except Exception as e:
        print(f"Erreur dans generate_area_plot pour {category_name}: {str(e)}")
        if 'fig' in locals():
            plt.close(fig)
        return None


def generate_histogram_plot():
    """Génère un histogramme de la distribution des taux de chômage"""
    try:
        df = load_data()
        
        # Collecter toutes les valeurs de chômage
        all_values = []
        for col in ['Urbain', 'Rural', 'Ensemble']:
            if col in df.columns:
                all_values.extend(df[col].dropna().tolist())
        
        if len(all_values) == 0:
            return None
        
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.hist(all_values, bins=20, color='#003366', alpha=0.7, edgecolor='#002244', linewidth=1.5)
        ax.set_xlabel('Taux de chômage (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Fréquence', fontsize=12, fontweight='bold')
        ax.set_title('Distribution des taux de chômage', fontsize=16, fontweight='bold', color='#003366', pad=20)
        ax.grid(True, alpha=0.3, axis='y', linestyle='--')
        fig.tight_layout()
        
        if fig.canvas is None:
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            FigureCanvasAgg(fig)
        
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return img_base64
    except Exception as e:
        print(f"Erreur dans generate_histogram_plot: {str(e)}")
        if 'fig' in locals():
            plt.close(fig)
        return None


def generate_comparison_line_plot():
    """Génère un graphique comparatif en lignes pour Urbain, Rural et Ensemble"""
    try:
        df = load_data()
        
        if not all(col in df.columns for col in ['Urbain', 'Rural', 'Ensemble']):
            return None
        
        df_clean = df[['Trimestre', 'Urbain', 'Rural', 'Ensemble']].dropna()
        
        if len(df_clean) == 0:
            return None
        
        fig, ax = plt.subplots(figsize=(16, 8))
        ax.plot(df_clean['Trimestre'], df_clean['Urbain'], label='Urbain', color='#0066CC', linewidth=2.5, marker='o', markersize=4)
        ax.plot(df_clean['Trimestre'], df_clean['Rural'], label='Rural', color='#FF6600', linewidth=2.5, marker='s', markersize=4)
        ax.plot(df_clean['Trimestre'], df_clean['Ensemble'], label='Ensemble', color='#006233', linewidth=2.5, marker='^', markersize=4)
        ax.tick_params(axis='x', rotation=90, labelsize=9)
        ax.set_title('Comparaison Urbain, Rural et Ensemble', fontsize=16, fontweight='bold', color='#003366', pad=20)
        ax.set_xlabel('Trimestre', fontsize=12, fontweight='bold')
        ax.set_ylabel('Taux de chômage (%)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=12, loc='best', framealpha=0.9)
        fig.tight_layout()
        
        if fig.canvas is None:
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            FigureCanvasAgg(fig)
        
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return img_base64
    except Exception as e:
        print(f"Erreur dans generate_comparison_line_plot: {str(e)}")
        if 'fig' in locals():
            plt.close(fig)
        return None


def get_forecast_period(year, quarter):
    """
    Calcule le nombre de périodes (trimestres) à prédire.
    On suppose que les données d'entraînement vont jusqu'à T4 2023.
    """
    REFERENCE_YEAR = 2023
    REFERENCE_QUARTER = 4
    
    quarters_ahead = (year - REFERENCE_YEAR) * 4 + (quarter - REFERENCE_QUARTER)
    
    if quarters_ahead <= 0:
        raise ValueError(f"La date demandée ({quarter_names.get(quarter, quarter)} {year}) doit être après {quarter_names[REFERENCE_QUARTER]} {REFERENCE_YEAR}")
    
    return quarters_ahead


@app.route('/')
def home():
    """Page d'accueil principale"""
    return render_template('home.html', category_hierarchy=CATEGORY_HIERARCHY)


@app.route('/prediction')
def index():
    """Page de prédiction avec le formulaire"""
    return render_template('index.html', category_hierarchy=CATEGORY_HIERARCHY)


@app.route('/about')
def about():
    """Page À propos"""
    return render_template('about.html')


@app.route('/dashboard')
def dashboard():
    """Tableau de bord avec visualisations"""
    visualizations = []
    df = load_data()
    
    # Section 1: Graphiques de tendance avec moyenne mobile
    trend_visualizations = []
    
    # Parcourir toutes les catégories et sous-catégories
    for main_cat, info in CATEGORY_HIERARCHY.items():
        # Catégorie principale avec données Excel
        if info.get('excel_column') and info['excel_column'] in df.columns:
            plot = generate_trend_plot(main_cat, info['excel_column'], info.get('color', '#003366'))
            if plot:
                trend_visualizations.append({
                    'name': f'Tendance - {main_cat}',
                    'image': plot,
                    'type': 'tendance'
                })
        
        # Sous-catégories
        if info.get('subcategories'):
            for sub_cat, sub_info in info['subcategories'].items():
                # Si données Excel disponibles
                if sub_info.get('excel_column') and sub_info['excel_column'] in df.columns:
                    plot = generate_trend_plot(sub_cat, sub_info['excel_column'], sub_info.get('color', '#003366'))
                    if plot:
                        trend_visualizations.append({
                            'name': f'Tendance - {sub_cat}',
                            'image': plot,
                            'type': 'tendance'
                        })
                # Sinon, utiliser le modèle SARIMA
                elif sub_info.get('model'):
                    plot = generate_trend_plot_from_model(sub_cat, sub_info.get('color', '#003366'))
                    if plot:
                        trend_visualizations.append({
                            'name': f'Tendance - {sub_cat}',
                            'image': plot,
                            'type': 'tendance'
                        })
    
    # Section 2: Graphiques simples du taux de chômage
    simple_visualizations = []
    
    for main_cat, info in CATEGORY_HIERARCHY.items():
        if info.get('excel_column') and info['excel_column'] in df.columns:
            plot = generate_simple_plot(main_cat, info['excel_column'], info.get('color', '#003366'))
            if plot:
                simple_visualizations.append({
                    'name': f'Taux de chômage - {main_cat}',
                    'image': plot,
                    'type': 'simple'
                })
        
        if info.get('subcategories'):
            for sub_cat, sub_info in info['subcategories'].items():
                if sub_info.get('excel_column') and sub_info['excel_column'] in df.columns:
                    plot = generate_simple_plot(sub_cat, sub_info['excel_column'], sub_info.get('color', '#003366'))
                    if plot:
                        simple_visualizations.append({
                            'name': f'Taux de chômage - {sub_cat}',
                            'image': plot,
                            'type': 'simple'
                        })
                elif sub_info.get('model'):
                    plot = generate_simple_plot_from_model(sub_cat, sub_info.get('color', '#003366'))
                    if plot:
                        simple_visualizations.append({
                            'name': f'Taux de chômage - {sub_cat}',
                            'image': plot,
                            'type': 'simple'
                        })
    
    # Section 3: Graphique comparatif en barres
    comparison_plot = generate_comparison_bar_chart()
    
    # Section 4: Graphiques en aires
    area_visualizations = []
    for main_cat, info in CATEGORY_HIERARCHY.items():
        if info.get('excel_column') and info['excel_column'] in df.columns:
            plot = generate_area_plot(main_cat, info['excel_column'], info.get('color', '#003366'))
            if plot:
                area_visualizations.append({
                    'name': f'Évolution - {main_cat}',
                    'image': plot,
                    'type': 'area'
                })
        if info.get('subcategories'):
            for sub_cat, sub_info in info['subcategories'].items():
                if sub_info.get('excel_column') and sub_info['excel_column'] in df.columns:
                    plot = generate_area_plot(sub_cat, sub_info['excel_column'], sub_info.get('color', '#003366'))
                    if plot:
                        area_visualizations.append({
                            'name': f'Évolution - {sub_cat}',
                            'image': plot,
                            'type': 'area'
                        })
    
    # Section 5: Histogramme de distribution
    histogram_plot = generate_histogram_plot()
    
    # Section 6: Comparaison Urbain/Rural/Ensemble
    comparison_line_plot = generate_comparison_line_plot()
    
    return render_template('dashboard.html', 
                         trend_visualizations=trend_visualizations,
                         simple_visualizations=simple_visualizations,
                         comparison_plot=comparison_plot,
                         area_visualizations=area_visualizations,
                         histogram_plot=histogram_plot,
                         comparison_line_plot=comparison_line_plot)


@app.route('/api/categories')
def get_categories():
    """API pour récupérer la structure hiérarchique des catégories"""
    return jsonify(CATEGORY_HIERARCHY)


@app.route('/api/subcategories/<main_category>')
def get_subcategories(main_category):
    """API pour récupérer les sous-catégories d'une catégorie principale"""
    if main_category in CATEGORY_HIERARCHY:
        info = CATEGORY_HIERARCHY[main_category]
        if info.get('subcategories'):
            subcats = {name: {'model': sub_info['model'], 'color': sub_info.get('color')} 
                      for name, sub_info in info['subcategories'].items()}
            return jsonify(subcats)
        return jsonify({})
    return jsonify({'error': 'Catégorie non trouvée'}), 404


@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint pour faire une prédiction"""
    try:
        data = request.get_json()
        category = data.get('category')
        year = int(data.get('year'))
        quarter = int(data.get('quarter'))
        
        # Validation
        if category not in CATEGORY_MODELS:
            return jsonify({'error': f"Catégorie '{category}' non valide"}), 400
        
        if quarter < 1 or quarter > 4:
            return jsonify({'error': 'Le trimestre doit être entre 1 et 4'}), 400
        
        # Charger le modèle
        model = load_model(category)
        
        # Calculer le nombre de périodes à prédire
        steps = get_forecast_period(year, quarter)
        
        # Obtenir une prédiction selon le type de modèle
        try:
            def extract_prediction_value(result):
                """Extrait la dernière valeur d'une prédiction (pandas Series ou numpy array)"""
                if hasattr(result, 'iloc'):
                    return float(result.iloc[-1])
                elif hasattr(result, '__getitem__'):
                    return float(result[-1])
                else:
                    return float(result)
            
            # Méthode 1: get_forecast() pour statsmodels SARIMAX (recommandé)
            if hasattr(model, 'get_forecast'):
                forecast_result = model.get_forecast(steps=steps)
                predicted_mean = forecast_result.predicted_mean
                prediction = extract_prediction_value(predicted_mean)
            # Méthode 2: forecast() pour statsmodels SARIMAX
            elif hasattr(model, 'forecast'):
                forecast = model.forecast(steps=steps)
                prediction = extract_prediction_value(forecast)
            # Méthode 3: predict() générique
            elif hasattr(model, 'predict'):
                pred = model.predict(steps=steps)
                prediction = extract_prediction_value(pred)
            else:
                raise AttributeError("Le modèle ne possède aucune méthode de prédiction connue")
        except Exception as e:
            return jsonify({
                'error': f'Erreur lors de la prédiction: {str(e)}',
                'hint': 'Vérifiez que le modèle est bien un modèle SARIMA de statsmodels sauvegardé correctement'
            }), 500
        
        return jsonify({
            'success': True,
            'category': category,
            'year': year,
            'quarter': quarter_names[quarter],
            'prediction': round(prediction, 2)
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
