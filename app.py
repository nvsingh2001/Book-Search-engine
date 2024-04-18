import csv
import re
import string
from collections import defaultdict
import math
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from flask import Flask, render_template, request

app = Flask(__name__)

def preprocess_data(csv_file):
    """
    Preprocesses the book data from a CSV file for indexing.
    
    Args:
        csv_file (str): The path to the CSV file containing book data.
        
    Returns:
        list: A list of preprocessed book records, where each record is a dictionary
              containing the book's title, author, and description fields.
    """
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    preprocessed_data = []
    
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            title = preprocess_text(row['title'], stop_words, stemmer)
            author = preprocess_text(row['authors'], stop_words, stemmer)
            description = preprocess_text(row['text_reviews_count'], stop_words, stemmer)
            
            preprocessed_data.append({
                'title': title,
                'author': author,
                'description': description
            })
            
    return preprocessed_data

def preprocess_text(text, stop_words, stemmer):
    """
    Preprocesses a given text by removing punctuation, converting to lowercase,
    removing stop words, and stemming the remaining words.
    
    Args:
        text (str): The input text to be preprocessed.
        stop_words (set): A set of stop words to be removed.
        stemmer (PorterStemmer): A PorterStemmer object for stemming words.
        
    Returns:
        str: The preprocessed text.
    """
    # Remove punctuation and convert to lowercase
    text = re.sub(r'[{}]'.format(string.punctuation), '', text.lower())
    
    # Tokenize the text into words
    words = text.split()
    
    # Remove stop words and stem the remaining words
    preprocessed_words = [stemmer.stem(word) for word in words if word not in stop_words]
    
    # Join the preprocessed words back into a single string
    preprocessed_text = ' '.join(preprocessed_words)
    
    return preprocessed_text



class InvertedIndex:
    def __init__(self):
        self.index = defaultdict(list)
        
    def index_data(self, documents):
        """
        Builds an inverted index from the document objects.
    
        Args:
            documents (list): A list of Document objects.
        """
        for doc in documents:
            title_tokens = doc.title.split()
            author_tokens = doc.author.split()
            description_tokens = doc.description.split()
    
            self.add_tokens_to_index(doc.doc_id, title_tokens, 'title')
            self.add_tokens_to_index(doc.doc_id, author_tokens, 'author')
            self.add_tokens_to_index(doc.doc_id, description_tokens, 'description')
            
    def add_tokens_to_index(self, book_id, tokens, field):
        """
        Adds tokens from a specific field of a book to the inverted index.
        
        Args:
            book_id (int): The ID of the book.
            tokens (list): A list of tokens (words) to be indexed.
            field (str): The field from which the tokens were extracted (e.g., 'title', 'author', 'description').
        """
        for token in tokens:
            self.index[(token, field)].append(book_id)
            
    def search(self, query):
        """
        Searches the inverted index for the given query and returns the matching book IDs.
        
        Args:
            query (str): The search query.
            
        Returns:
            list: A list of book IDs that match the search query.
        """
        query_tokens = query.split()
        matching_book_ids = []
        
        for token in query_tokens:
            book_ids_for_token = self.index.get((token, 'title'), []) + \
                                 self.index.get((token, 'author'), []) + \
                                 self.index.get((token, 'description'), [])
            matching_book_ids.extend(book_ids_for_token)
            
        return list(set(matching_book_ids))
    
class Document:
    def __init__(self, doc_id, title, author, description):
        self.doc_id = doc_id
        self.title = title
        self.author = author
        self.description = description
        self.text = ' '.join([title, author, description])
        self.term_frequencies = {}
        self.length = len(self.text.split())

    def compute_term_frequencies(self, index):
        for term in set(self.text.split()):
            self.term_frequencies[term] = self.text.count(term) / self.length

class SearchEngine:
    def __init__(self, documents):
        self.documents = documents
        self.index = InvertedIndex()
        self.index.index_data(documents)
        self.idf_scores = self.compute_idf_scores()

    def compute_idf_scores(self):
        idf_scores = {}
        num_docs = len(self.documents)
        for term_field, doc_list in self.index.index.items():
            term, _ = term_field  # Extract the term from the tuple
            idf_scores[term.lower()] = math.log(num_docs / (1 + len(doc_list)))
        return idf_scores


    def search(self, query):
        query_terms = query.lower().split()
        query_vector = {}
        for term in query_terms:
            query_vector[term] = query_terms.count(term)

        ranking = []
        for doc in self.documents:
            score = 0
            for term in query_vector:
                if term in doc.term_frequencies:
                    tf = doc.term_frequencies[term]
                    idf = self.idf_scores[term]
                    score += tf * idf * (1 + query_vector[term])
            ranking.append((doc.doc_id, score))

        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking

    def display_results(self, ranking, threshold=0.5, page_size=10):
        if not ranking:
            print("No matching books found.")
            return
        
        # Filter results based on threshold
        filtered_ranking = [(doc_id, score) for doc_id, score in ranking if score >= threshold]
        
        if not filtered_ranking:
            print(f"No matching books found above threshold {threshold}.")
            return
        
        # Sort results by score
        filtered_ranking.sort(key=lambda x: x[1], reverse=True)
        
        # Paginate results
        num_pages = math.ceil(len(filtered_ranking) / page_size)
        
        for page_num in range(num_pages):
            print(f"Page {page_num + 1}:")
            start_index = page_num * page_size
            end_index = min(start_index + page_size, len(filtered_ranking))
            
            for idx in range(start_index, end_index):
                doc_id, score = filtered_ranking[idx]
                doc = search_engine.documents[doc_id]
                original_book_info = preprocessed_books[doc.doc_id]  # Fetch original book info
                print(f"Book ID: {doc.doc_id}, Title: {original_book_info['title']}, Author: {original_book_info['author']}, Score: {score:.2f}")


preprocessed_books = preprocess_data('books.csv')
documents = []
for book_id, book in enumerate(preprocessed_books):
    title = book['title']
    author = book['author']
    description = book['description']
    doc = Document(book_id, title, author, description)
    doc.compute_term_frequencies(InvertedIndex())
    documents.append(doc)
search_engine = SearchEngine(documents)


def display_results(ranking):
    if not ranking:
        return "No matching books found."
    else:
        results = []
        filtered_ranking = [(doc_id, score) for doc_id, score in ranking if score >= 1.0]
        if not filtered_ranking:
            return f"No matching books found above threshold 1.0."
        else:
            filtered_ranking.sort(key=lambda x: x[1], reverse=True)
            num_pages = min(len(filtered_ranking) // 5 + 1, 10)

            for page_num in range(num_pages):
                results.append(f"Page {page_num + 1}:<br>")
                start_index = page_num * 5
                end_index = min(start_index + 5, len(filtered_ranking))

                for idx in range(start_index, end_index):
                    doc_id, score = filtered_ranking[idx]
                    doc = search_engine.documents[doc_id]
                    original_book_info = preprocessed_books[doc.doc_id]
                    results.append(f"Book ID: {doc.doc_id}, Title: {original_book_info['title']}, Author: {original_book_info['author']}, Score: {score:.2f}<br>")
                results.append("<br>")
        return ''.join(results)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        ranking = search_engine.search(query)
        results = display_results(ranking)  # Call the display_results function here
        return render_template('index.html', results=results)
    return render_template('index.html', results=None)

if __name__ == '__main__':
    app.run(debug=True)