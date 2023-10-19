import tkinter as tk
from tkinter import filedialog, messagebox
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
from tabulate import tabulate
from gensim import corpora, models
import PyPDF2
import matplotlib.pyplot as plt
from PyPDF2 import PdfReader
from wordcloud import WordCloud
import re

# Téléchargez les données nécessaires de NLTK (si ce n'est pas déjà fait)
nltk.download('punkt')
nltk.download('stopwords')

# Définissez common_words et text en dehors des fonctions pour les rendre accessibles aux fonctions lambda
common_words = []
text = ""

# Fonction pour extraire le texte d'un fichier PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Fonction pour prétraiter le texte
def preprocess(text):
    tokens = word_tokenize(text)
    tokens = [word.lower() for word in tokens if word.isalpha()]
    tokens = [word for word in tokens if not word in stopwords.words('english')]
    return tokens

# Fonction pour créer le diagramme de fréquence
def create_frequency_plot(common_words):
       words, frequencies = zip(*common_words)
       plt.figure(figsize=(10, 6))
       plt.barh(words, frequencies)
       plt.xlabel('Fréquence')
       plt.ylabel('Mot')
       plt.title('Diagramme de Fréquence des Mots les Plus Fréquents')
       plt.tight_layout()
       plt.show()

def calculate_word_frequency_diagramme(pdf_file_paths, num_common_words):
    tokenized_documents = []

    for file_path in pdf_file_paths:
        text = extract_text_from_pdf(file_path)
        tokenized_documents.append(preprocess(text))

    # Calcul de la fréquence
    word_frequency = Counter()
    for doc_tokens in tokenized_documents:
        word_frequency.update(doc_tokens)

    # Mots les plus fréquents
    common_words = word_frequency.most_common(num_common_words)

    # Appeler la fonction pour créer le diagramme de fréquence
    create_frequency_plot(common_words)

# Fonction pour calculer la fréquence des mots
def calculate_word_frequency(pdf_file_paths, num_common_words):
    tokenized_documents = []

    for file_path in pdf_file_paths:
        text = extract_text_from_pdf(file_path)
        tokenized_documents.append(preprocess(text))

    # Calcul de la fréquence
    word_frequency = Counter()
    for doc_tokens in tokenized_documents:
        word_frequency.update(doc_tokens)

    # Mots les plus fréquents
    common_words = word_frequency.most_common(num_common_words)

    # Affichage des résultats
    results_text = "Mots les plus fréquents:\n"
    results_text += tabulate(common_words, headers=['Mot','Fréquence'], tablefmt='grid') + "\n\n"

     # Afficher les résultats dans une boîte de dialogue
    messagebox.showinfo("Résultats de l'Analyse de Texte", results_text)


# Fonction pour modéliser les sujets
def model_topics(pdf_file_paths, num_topics):
    tokenized_documents = []

    for file_path in pdf_file_paths:
        text = extract_text_from_pdf(file_path)
        tokenized_documents.append(preprocess(text))

    # Modélisation de sujets
    dictionary = corpora.Dictionary(tokenized_documents)
    corpus = [dictionary.doc2bow(tokens) for tokens in tokenized_documents]
    lda_model = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary)

    # Affichage des résultatsL
    results_text = "Sujets modélisés:\n"
    topics = []
    for topic in lda_model.print_topics():
        topics.append([topic[0], topic[1]])
    results_text += tabulate(topics, headers=['Sujet', 'Mots Clés'], tablefmt='grid')

    # Afficher les résultats dans une boîte de dialogue
    messagebox.showinfo("Résultats de l'Analyse de Texte", results_text)


# Fonction pour créer le nuage de mots
def create_word_cloud(text):
    # Créez un objet WordCloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    # Affichez le nuage de mots à l'aide de matplotlib
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')  # Masque les axes
    plt.show()

def calculate_word_frequency_nuage(pdf_file_paths, num_common_words):
    global common_words
    global text
    tokenized_documents = []

    for file_path in pdf_file_paths:
        text = extract_text_from_pdf(file_path)
        tokenized_documents.append(preprocess(text))

    # Calcul de la fréquence
    word_frequency = Counter()
    for doc_tokens in tokenized_documents:
        word_frequency.update(doc_tokens)

    # Mots les plus fréquents
    common_words = word_frequency.most_common(num_common_words)

    # Convertir la liste de mots en texte pour le nuage de mots
    text = ' '.join([word for word, _ in common_words])

    # Appeler la fonction pour créer le nuage des mots
    create_word_cloud(text)


def display_paragraphs():
    # Récupérez les mots entrés par l'utilisateur et convertissez-les en minuscules
    search_words = search_entry.get().lower().split()
    
    # Initialisez une variable pour stocker les paragraphes correspondants
    matching_paragraphs = []

    # Parcourez les fichiers PDF chargés
    for pdf_file_path in pdf_file_paths:
        text = extract_text_from_pdf(pdf_file_path)
        
        # Utilisez une expression régulière pour diviser le texte en paragraphes
        paragraphs = re.split(r'\n\s*\n', text)  # Cette expression régulière tient compte de différents formats de saut de ligne
        
        # Recherchez et stockez les paragraphes qui contiennent tous les mots clés
        for paragraph in paragraphs:
            # Convertissez le paragraphe en minuscules pour une recherche insensible à la casse
            paragraph_lower = paragraph.lower()
            # Vérifiez si tous les mots clés sont présents dans le paragraphe
            if all(word in paragraph_lower for word in search_words):
                matching_paragraphs.append(paragraph)

    # Créez une nouvelle fenêtre pour afficher les paragraphes correspondants
    result_window = tk.Toplevel()
    result_window.title("Résultats de la Recherche")
    
    result_text = tk.Text(result_window, wrap=tk.WORD)
    result_text.pack()

    if matching_paragraphs:
        for paragraph in matching_paragraphs:
            # Surlignez les mots recherchés dans le paragraphe
            highlighted_paragraph = highlight_text(paragraph, search_words)
            result_text.insert(tk.END, highlighted_paragraph + "\n\n")
    else:
        result_text.insert(tk.END, "Aucun paragraphe trouvé contenant ces mots.")
    
    # Ajoutez une barre de défilement si nécessaire
    scrollbar = tk.Scrollbar(result_window, command=result_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    result_text.config(yscrollcommand=scrollbar.set)

    # Bloquez la fenêtre résultante pour que l'utilisateur la ferme avant de continuer
    result_window.mainloop()

def highlight_text(paragraph, search_words):
    for word in search_words:
        paragraph = paragraph.replace(word, f'<span style="background-color: yellow;">{word}</span>')
    return paragraph

# Créez une fenêtre Tkinter
window = tk.Tk()
window.title("Analyse de Texte depuis PDF")
window.geometry("900x900+500+100")
# Changer la couleur d'arrière-plan en noir
window.configure(bg="AliceBlue")
# Ajoutez un titre avec un widget Label
title_label = tk.Label(window, text="Analyseur des Mots ", font=("times new roman", 30, "bold"), bg="AliceBlue", fg="black")
title_label.place(x=50, y=30)

paragraphe_label = tk.Label(window, text="Découvrez les mots clés et tendances dans vos documents ",font=("times new roman", 15) , bg="AliceBlue", fg="black")
paragraphe_label.place(x=70, y=100)


# Créez des variables pour stocker les informations de l'utilisateur
pdf_file_paths = []
num_common_words = tk.StringVar()
num_topics = tk.StringVar()

# Fonction pour charger des documents PDF
def load_pdf_documents():
    selected_files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    pdf_file_paths.extend(selected_files)
    print("Documents PDF chargés:", pdf_file_paths)

# Créez des étiquettes et des champs de saisie pour les informations de l'utilisateur

fram1=tk.Frame(window,bg="white")
fram1.place(x=150, y=200,width=600,height=600)

pdf_label = tk.Label(fram1, text="Télécharger des Documents:",bg="white",fg="black", font=("times new roman", 15))
pdf_label.place(x=50, y=50)

load_button = tk.Button(fram1, text="Charger ",font=("times new roman", 15), command=load_pdf_documents)
load_button.place(x=350, y=50)

common_words_label = tk.Label(fram1, text="Nombre de mots les plus fréquents :",bg="white",fg="black", font=("times new roman", 15))
common_words_label.place(x=50, y=100)

common_words_entry = tk.Entry(fram1,bg="white", font=("times new roman", 15), textvariable=num_common_words)
common_words_entry.place(x=350, y=100)

topics_label = tk.Label(fram1, text="Nombre de sujets à modéliser:",bg="white",fg="black", font=("times new roman", 15))
topics_label.place(x=50, y=150)

topics_entry = tk.Entry(fram1,bg="white", font=("times new roman", 15), textvariable=num_topics)
topics_entry.place(x=350, y=150)

# Boutons pour chaque fonction

calculate_frequency = tk.Label(fram1, text="la Fréquence des Mots:",bg="white",fg="black", font=("times new roman", 15))
calculate_frequency.place(x=50, y=200)
calculate_frequency_button = tk.Button(fram1, text="Afficher",bg="white", font=("times new roman", 15), command=lambda: calculate_word_frequency(pdf_file_paths, int(num_common_words.get()))) 

model_topic = tk.Label(fram1, text="Modélisation des Sujets:",bg="white",fg="black", font=("times new roman", 15))
model_topic.place(x=50, y=250)
model_topic_button = tk.Button(fram1, text="Afficher" ,bg="white", font=("times new roman", 15), command=lambda: model_topics(pdf_file_paths, int(num_topics.get())))

create_diagram = tk.Label(fram1, text="Diagramme des Fréquences:",bg="white",fg="black", font=("times new roman", 15))
create_diagram.place(x=50, y=300)
create_diagram_button = tk.Button(fram1, text="Afficher",bg="white", font=("times new roman", 15), command=lambda: calculate_word_frequency_diagramme(pdf_file_paths, int(num_common_words.get()))) 

reate_word_cloud = tk.Label(fram1, text="Nuage de Mots:",bg="white",fg="black", font=("times new roman", 15))
reate_word_cloud.place(x=50, y=350)
create_word_cloud_button = tk.Button(fram1, text="Afficher",bg="white", font=("times new roman", 15), command=lambda: calculate_word_frequency_nuage(pdf_file_paths, int(num_common_words.get()))) 

# Ajoutez un widget Entry pour entrer les mots
serch_label= tk.Label(fram1, text="les paragraphe des mots :",bg="white",fg="black", font=("times new roman", 15))
serch_label.place(x=50, y=400)

search_entry = tk.Entry(fram1, bg="white", font=("times new roman", 15))
search_entry.place(x=350, y=400)

# Ajoutez un bouton pour rechercher et afficher les paragraphes
search_button = tk.Button(fram1, text="Afficher", bg="white", font=("times new roman", 15), command=display_paragraphs)
search_button.place(x=350, y=450)

# Organisez les boutons dans la fenêtre Tkinter
calculate_frequency_button.place(x=350, y=200)
model_topic_button.place(x=350, y=250)
create_diagram_button.place(x=350, y=300)
create_word_cloud_button.place(x=350, y=350)

# Lancez la boucle principale de l'interface utilisateur
window.mainloop()
