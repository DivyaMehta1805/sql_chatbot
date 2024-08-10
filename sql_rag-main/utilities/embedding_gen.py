import numpy as np
from sentence_transformers import SentenceTransformer
import argparse
import csv

def load_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def load_embeddings(file_path):
    return np.load(file_path, allow_pickle=True)

def cosine_similarity(a, b):
    return np.dot(a, b.T) / (np.linalg.norm(a) * np.linalg.norm(b, axis=1))

def find_similar_terms(row_embedding, embeddings, terms, relative_threshold=0.8, top_n=5):
    similarities = cosine_similarity(row_embedding, embeddings)
    max_similarity = np.max(similarities)
    threshold = max_similarity * relative_threshold
    
    similar_indices = np.argsort(similarities)[-top_n:][::-1]
    return [(terms[i], similarities[i]) for i in similar_indices if similarities[i] >= threshold]

def main():
    parser = argparse.ArgumentParser(description="Compare CSV rows with embeddings and store similar terms.")
    parser.add_argument('--company_info_csv', type=str, default='event_info.csv', help='Path to the input CSV file.')
    parser.add_argument('--embeddings_file', type=str, default='embeddings.npy', help='Path to the embeddings.npy file.')
    parser.add_argument('--terms_file', type=str, default='industries_list_dedup.txt', help='Path to the file containing terms.')
    parser.add_argument('--output_csv', type=str, default='event_info_updated.csv', help='Path to the output CSV file.')
    parser.add_argument('--relative_threshold', type=float, default=0.8, help='Relative threshold for similarity (0-1).')
    parser.add_argument('--top_n', type=int, default=5, help='Number of top similar terms to consider.')
    parser.add_argument('--delimiter', type=str, default='|', help='Delimiter for similar terms.')
    args = parser.parse_args()

    model = SentenceTransformer('all-MiniLM-L6-v2')
    csv_data = load_csv(args.company_info_csv)
    embeddings = load_embeddings(args.embeddings_file)
    
    with open(args.terms_file, 'r') as f:
        terms = [line.strip() for line in f]

    # Write results to the output CSV
    with open(args.output_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = list(csv_data[0].keys()) + ['similar_terms']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in csv_data:
            row_text = ' '.join(row.values())
            row_embedding = model.encode(row_text)
            similar_terms = find_similar_terms(row_embedding, embeddings, terms, args.relative_threshold, args.top_n)
            
            new_row = row.copy()
            new_row['similar_terms'] = args.delimiter.join([f"{term} ({score:.2f})" for term, score in similar_terms])
            writer.writerow(new_row)

    print(f"Results written to {args.output_csv}")

if __name__ == "__main__":
    main()