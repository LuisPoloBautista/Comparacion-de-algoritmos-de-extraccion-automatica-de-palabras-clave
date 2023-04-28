# -*- coding: utf-8 -*-
"""Comparación de algoritmos de extracción automática de palabras clave para resúmenes de artículos .ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZS8ffCi-dlBS5tlMKMBZVv-iTZxmQarM

*Luis Roberto Polo Bautista, Raquel Casique Vasquez*

**Se compararon tres algoritmos de aprendizaje automático para la extracción de palabras claves utilizando un corpus de resúmenes de artículos obtenidos de Scopus. En este artículo se describe el estado del arte de los algoritmos KeyBERT, YAKE y GPT-3, así como su arquitectura. A través de Google Colaboratory se implementaron los algoritmos y se efectuó un análisis comparativo basado en similitud del coseno entre las palabras claves identificadas automáticamente y las indexadas manualmente en los resúmenes de artículos. El objetivo es analizar la semejanza entre las palabras clave extraídas automáticamente y las asignadas manualmente. Los resultados muestran que las palabras clave obtenidas de GPT-3 fueron las más similares a las asignadas manualmente. Se muestran los beneficios de utilizar estas herramientas para automatizar los procesos de análisis documental e indización de documentos, con la finalidad de facilitar la gestión de la información digital y electrónica.**
"""

# Vincular con Drive
from google.colab import drive
drive.mount('/content/drive')

#Descargar bibliotecas
import nltk
nltk.download('stopwords')

nltk.download('wordnet')

# Importar bibliotecas
import csv
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

df=pd.read_csv('/content/drive/MyDrive/Comparación de algoritmos de extracción de palabras clave/scopus.csv', encoding='utf-8')
df.head(3)

abstracts= df['Abstract']
#AuthorKeywords= df['Author Keywords']

# Definir expresiones regulares y configurar lematizador y lista de palabras vacías
regex = r'\b\w+\b'
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Definir la función para limpiar el texto
def clean_text(text):
    # Eliminar signos de puntuación y normalizar a minúsculas
    words = re.findall(regex, text.lower())
    # Eliminar palabras vacías o irrelevantes
    words = [w for w in words if not w in stop_words]
    # Lematizar o stemmizar las palabras para reducir la variabilidad lingüística
    words = [lemmatizer.lemmatize(w) for w in words]
    # Unir las palabras limpias en una sola cadena y devolver el resultado
    return ' '.join(words)

# Aplicar la función a la columna 'Abstract'
df['Cleaned_Abstract'] = df['Abstract'].apply(clean_text)
df['Cleaned_Abstract']

"""**YAKE**"""

!pip install yake

#extraer la columna que contiene el texto que deseamos analizar.
abs=df['Cleaned_Abstract']

# Instalar y importar la biblioteca Yake.
import yake
kw_extractor = yake.KeywordExtractor()

# Definir los parámetros de Yake, como el idioma y el número de palabras clave que deseamos extraer.
language = "en"
max_ngram_size = 1
deduplication_threshold = 0.9
num_of_keywords = 10

# Definir función para aplicar Yake a cada texto de la columna
def extract_keywords(abs):
    # Extraer las palabras clave del texto utilizando Yake
    kw = kw_extractor.extract_keywords(abs)
    # Devolver solo las palabras clave sin sus valores de relevancia
    return [k[0] for k in kw]

# Aplicar la función a la columna y guardar el resultado en una nueva columna llamada "keywords"
df["Yake"] = abs.apply(extract_keywords)

def clean_text(CONTENIDO):
  CONTENIDO = re.sub(r'\[[^]]*\]', '', CONTENIDO)
  CONTENIDO = re.sub(r"\'", "", CONTENIDO)
  return CONTENIDO

df['Yake'] = df['Yake'].apply(clean_text)
df['Yake']

"""**KEYBERT**"""

!pip install keybert

from keybert import KeyBERT

# Inicializar modelo KeyBERT
model = KeyBERT('distilbert-base-nli-mean-tokens')

# Definir función para extraer palabras clave de un texto
def extract_keywords(text):
    keywords = model.extract_keywords(text, keyphrase_ngram_range=(1, 3), stop_words='english')
    return [keyword[0] for keyword in keywords]

# Aplicar la función para extraer palabras clave de la columna "resumen"
df['KeyBERT'] = df['Cleaned_Abstract'].apply(extract_keywords)

"""**ChatGPT**"""

!pip install pandas openai

!pip install --upgrade openai_secret_manager

import openai

openai.api_key = "...KEY_OPENAI..."

# Utiliza ChatGPT para extraer palabras clave de cada resumen y agrega las palabras clave a una nueva columna del DataFrame
keywords_list = []
for summary in df['Cleaned_Abstract']:
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Extract keywords from the following text: {summary}",
        temperature=0.3,
        max_tokens=60,
        n=1,
        stop=None,
        frequency_penalty=0,
        presence_penalty=0
    )
    keywords = []
    for choice in response.choices:
        keywords.append(choice.text.strip())
    keywords_list.append(keywords)
df['GPT'] = keywords_list

df

df.to_csv( "/content/drive/MyDrive/Comparación de algoritmos de extracción de palabras clave/scopus2.csv", encoding='utf-8')