# -*- coding: utf-8 -*-
"""rag_project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Bl1Mo5gNWbttm_7h4ojOPtuPYIH9v1l0
"""

from openai import OpenAI
import numpy as np

class MessiRAG:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.embedded_chunks = {}

    def chunk_text(self, text, chunk_size=200, overlap=50):
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            if len(chunk) < 50:
                continue
            chunks.append(chunk)
        return chunks

    def create_embeddings(self, text_list):
        response = self.client.embeddings.create(
            input=text_list,
            model="text-embedding-3-small"
        )
        return [item.embedding for item in response.data]

    def load_document(self, filepath):
        """Load and embed the document"""
        with open(filepath, 'r', encoding='utf-8') as file:
            text = file.read()

        chunks = self.chunk_text(text)

        embeddings = self.create_embeddings(chunks)

        for chunk, embedding in zip(chunks, embeddings):
            self.embedded_chunks[chunk] = embedding

    def cosine_similarity(self, a, b):
        """Calculate cosine similarity between two vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def get_relevant_chunks(self, query, top_k=5):
        """Get the most relevant chunks for a query"""
        query_embedding = self.create_embeddings([query])[0]

        similarities = {
            chunk: self.cosine_similarity(query_embedding, chunk_embedding)
            for chunk, chunk_embedding in self.embedded_chunks.items()
        }

        sorted_chunks = sorted(similarities.items(), key=lambda x: x[1], reverse=True)

        return [chunk for chunk, _ in sorted_chunks[:top_k]]

    def answer_question(self, question):
        """Answer a question using RAG"""
        relevant_chunks = self.get_relevant_chunks(question)

        context = "\n".join(relevant_chunks)
        prompt = f"""Based on the following context about Lionel Messi, please answer the question.

Context:
{context}

Question: {question}

Answer:"""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

if __name__ == "__main__":
    API_KEY = "sk-svcacct-oD2ywALJLsVNQwU3GZ-Lvl-6d53TV1hwjr7DKEfvT07SSYDzFHvmTo3Fx9gp-5KT3BlbkFJsc-MOn7QvehX14nXoONvR0tKAQ8_XBfDFywvS3CVLyL4QaCm9Pklco6v0i3hhAA"

    messi_rag = MessiRAG(API_KEY)

    messi_rag.load_document("messi.txt")

    question = "What are Messi's greatest achievements?"
    answer = messi_rag.answer_question(question)
    print(f"Question: {question}\n")
    print(f"Answer: {answer}")