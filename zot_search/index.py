import sqlite3
from collections import Counter
import re

def create_inverted_index(db_path, documents, wikipedia_url_dict):
    """
    Creates an SQLite database with an inverted index.
    documents: List of tuples (doc_id, text)
    """
    # Connect to SQLite (creates file if not exists)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Create the schema
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS Documents (
            doc_id INTEGER PRIMARY KEY,
            doc_title TEXT NOT NULL,
            doc_url TEXT NOT NULL,
            content TEXT
            
        
        );
        
        CREATE TABLE IF NOT EXISTS InvertedIndex (
            term TEXT,
            doc_title TEXT,
            frequency INTEGER,
            PRIMARY KEY (term, doc_title),
            FOREIGN KEY (doc_title) REFERENCES Documents(doc_title)
        );
        
        CREATE INDEX IF NOT EXISTS idx_term ON InvertedIndex(term);
    ''')

    for title in documents:
        if title not in wikipedia_url_dict:
            continue

        doc_id = title
        url = wikipedia_url_dict[title]
        text = documents[title]

        # Save document content
        cursor.execute("INSERT OR IGNORE INTO Documents (doc_title, doc_url, content) VALUES ( ?, ?, ?)", (title, url, text))
        
        # Tokenize (lowercase and remove non-alphanumeric)
        tokens = re.findall(r'\w+', text.lower())
        
        # Count term frequency in current document
        counts = Counter(tokens)
        
        # 2. Insert into Inverted Index
        data = [(term, title, freq) for term, freq in counts.items()]
        cursor.executemany(
            "INSERT OR REPLACE INTO InvertedIndex (term, doc_title, frequency) VALUES (?, ?, ?)", 
            data
        )

    conn.commit()
    return conn

def search_index(db_path, term):
    term = term.lower()

    # Connect to SQLite (creates file if not exists)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT doc_title, frequency FROM InvertedIndex WHERE term = ? ORDER BY frequency DESC"
    results = cursor.execute(query, (term,)).fetchall()

    return results

def union_documents_with_term(db_path: str, query: str) -> set[str]:
    the_union = set()

    terms = query.strip().lower().split(" ")

    for term in terms:
        results = search_index(db_path, term)
        for result in results:
            the_union.add(result[0])

    return the_union

def get_document_text(db_path, title):
    # Connect to SQLite (creates file if not exists)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT content FROM Documents WHERE doc_title = ?"
    results = cursor.execute(query, (title,)).fetchall()

    if len(results) == 0 or len(results[0]) == 0:
        return ""

    return results[0][0]

def get_len_of_document(db_path, title):
    # Connect to SQLite (creates file if not exists)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT content FROM Documents WHERE doc_title = ?"
    results = cursor.execute(query, (title,)).fetchall()

    if len(results) == 0 or len(results[0]) == 0:
        return 0

    return len(results[0][0])

def get_number_of_documents_in_index(db_path):
    # Connect to SQLite (creates file if not exists)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT COUNT(*) FROM Documents"
    results = cursor.execute(query).fetchall()

    if len(results) == 0:
        return 0
    
    return results[0][0]

def get_doc_url_from_title(db_path, title):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT doc_url FROM Documents WHERE doc_title = ?"
    results = cursor.execute(query, (title,)).fetchall()

    if len(results) == 0 or len(results[0]) == 0:
        return ""

    return results[0][0]


def display_top_results(db_path, results, display_score = False, max_results = 10):
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    count = 0

    for title, score in sorted_results:
        if display_score:
            print(f"{title}: {score}")
        else:
            print(title)
        print(get_doc_url_from_title(db_path, title))
        print("\n")

        count += 1
        if count >= max_results:
            break
