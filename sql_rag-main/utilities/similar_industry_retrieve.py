import numpy as np
from sentence_transformers import SentenceTransformer, util
import argparse
import numpy as np

def load_chunks(file_path):
    return np.load(file_path)

def load_embeddings(file_path):
    return np.load(file_path)
def cosine_similarity(a, b):
    # Ensure a and b are 2D arrays
    a = np.atleast_2d(a)
    b = np.atleast_2d(b)
    return np.dot(a, b.T) / (np.linalg.norm(a) * np.linalg.norm(b))
def find_most_similar_chunks(input_text, chunks, embeddings, model,num_chunks=3,similarity_threshold=0.5):
    input_embedding = model.encode(input_text)
    similarities = []
    for i, chunk in enumerate(chunks):
        chunk_embedding = embeddings[i]
        similarity = cosine_similarity([input_embedding], [chunk_embedding])[0][0]
        if similarity >= similarity_threshold:
            similarities.append((similarity, chunk))
    
    # Sort similarities in descending order and get the top num_chunks
    most_similar = sorted(similarities, key=lambda x: x[0], reverse=True)[:num_chunks]
    return [chunk for _, chunk in most_similar]

def main():
    parser = argparse.ArgumentParser(description="Perform similarity-based search on code chunks.")
    parser.add_argument('input_text', type=str, help='The input text to search for similar code chunks.')
    parser.add_argument('--chunks_file', type=str, default='chunks.npy', help='Path to the file containing code chunks.')
    parser.add_argument('--embeddings_file', type=str, default='embeddings.npy', help='Path to the file containing embeddings.')

    args = parser.parse_args()

    model = SentenceTransformer('all-MiniLM-L6-v2')
    chunks = load_chunks(args.chunks_file)
    embeddings = load_embeddings(args.embeddings_file)
    most_similar_chunks = find_most_similar_chunks(args.input_text, chunks, embeddings, model, num_chunks=3,similarity_threshold=0.5)

    for i, chunk in enumerate(most_similar_chunks, 1):
        print(f"Chunk {i}:")
        print(chunk)
        print("---")
if __name__ == "__main__":
        main()
