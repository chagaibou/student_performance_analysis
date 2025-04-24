from shiny import App, render, ui
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Charger le DataFrame
df = pd.read_csv('./StudentPerformanceFactors.csv')

# Variables qualitatives et numériques pour les sélections
variables_categories = df.select_dtypes(include='object').columns.tolist()
categories = {var: var for var in variables_categories}
variables_numeriques = df.select_dtypes(exclude='object').columns.tolist()
numeriques = {var: var for var in variables_numeriques[0:-2]}

app_ui = ui.page_sidebar(
    ui.sidebar(
       ui.input_slider(
           "exam_score_range",
           "Plage de Score d'Examen",
           min = 0,
           max = 100,
           value=(50, 100)
       ),
       ui.input_select(
            "school_type_filter",
            "Type d'École",
            ["Tous", "Public", "Private"]  
        )
    
   ),
    ui.panel_title("Tableau de Bord sur les Facteurs de Performances des Étudiants"),  # Titre principal
  
   ui.layout_columns(
        ui.card(
               ui.card_header("Dataset des facteurs de performances des étudiants"),
               ui.output_data_frame('dataset'),
               style="height: 250px; overflow-y: auto;" 
              
           ),
       ui.card(
               ui.card_header("Moyenne de l'Exam_Score par Genre"),
               ui.input_select(
                   'gender_filter',
                   'choisir le genre',
                   ['Male','Female']
                   
               ),
               ui.output_text('exam_score_by_gender'),
              
               
           ),
          
       
   ),
   ui.layout_columns(
          
            ui.card(
               ui.card_header("Distribution de l'Exam Score"),
               ui.output_plot('exam_score_dist'),
            
               
               
           ),
             ui.card(
        ui.card_header("Correlation entre l'Exam Score et les variables numeriques"),
            ui.input_select(
                'variable_correlation',
                'choisir une variable',
                numeriques,
            ),
            ui.output_plot('correlation_plot'),
                
        
          
           
       ),

    ),
   ui.layout_columns(
       ui.card(
           ui.card_header("Répartition des étudiants par Catégorie"),
           ui.input_select(
               'variable_categorie',
               'choisir une variable',
               categories
               
           ),
           ui.output_plot('countplots')
       ),
    ui.card(
        ui.card_header("Matrice de correleation des variables numeriques"),
        ui.output_plot('correlation_matrix')
    )
   ))


# Fonction utilitaire pour appliquer les filtres
def get_filtered_data(input):
    """Filtrer les données selon le type d'école et la plage de scores."""
    school_type = input.school_type_filter()
    score_min, score_max = input.exam_score_range()
    
    filtered_df = df
    if school_type != "Tous":
        filtered_df = filtered_df[filtered_df["School_Type"] == school_type]
    filtered_df = filtered_df[
        (filtered_df['Exam_Score'] >= score_min) & (filtered_df['Exam_Score'] <= score_max)
    ]
    return filtered_df

# Définir la logique du serveur
def server(input, output, session):
    @output
    @render.data_frame
    def dataset():
        return get_filtered_data(input)

    @output
    @render.text
    def exam_score_by_gender():
        filtered_df = get_filtered_data(input)
        selected_gender = input.gender_filter()
        avg_score = filtered_df[filtered_df['Gender'] == selected_gender]['Exam_Score'].mean()
        if pd.isna(avg_score):
            return "Pas de données pour le genre sélectionné."
        return f"La moyenne de l'exam_score pour les {'hommes' if selected_gender == 'Male' else 'femmes'} est {avg_score:.2f}"

    @output
    @render.plot
    def exam_score_dist():
        filtered_df = get_filtered_data(input)
        plt.figure()
        sns.histplot(filtered_df['Exam_Score'], kde=True)
        plt.title("Distribution de l'Exam Score")
        plt.xlabel("Exam Score")
        return plt.gcf()

    @output
    @render.plot
    def correlation_plot():
        selected_variable = input.variable_correlation()
        filtered_df = get_filtered_data(input)
        plt.figure()
        sns.scatterplot(data=filtered_df, x=selected_variable, y='Exam_Score', alpha=0.7)
        plt.title(f"Corrélation entre Exam Score et {selected_variable}")
        plt.xlabel(selected_variable)
        plt.ylabel("Exam Score")
        return plt.gcf()

    @output
    @render.plot
    def countplots():
        selected_category = input.variable_categorie()
        filtered_df = get_filtered_data(input)
        plt.figure()
        sns.countplot(data=filtered_df, x=selected_category, palette="Set2",hue=selected_category)
        plt.title(f"Répartition des étudiants par {selected_category}")
        plt.xlabel(selected_category)
        return plt.gcf()

    @output
    @render.plot
    def correlation_matrix():
        filtered_df = get_filtered_data(input)
        correlation_matrix = filtered_df.select_dtypes(exclude='object').corr()
        plt.figure(figsize=(12, 10))
        sns.heatmap(correlation_matrix, cmap='coolwarm', vmin=-1, vmax=1, annot=True)
        plt.title("Matrice de corrélation des variables numériques")
        return plt.gcf()

# Créer et exécuter l'application
app = App(app_ui, server)