import re
from pathlib import Path

from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


PDF_PATH = Path("documents/Machine_Maintenance_SOP.pdf")


def load_pdf_text(pdf_path):
    reader = PdfReader(str(pdf_path))

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def create_chunks(text):
    # Split text into smaller sections
    sections = re.split(r"\n(?=\d+\.)", text)

    chunks = []

    for section in sections:
        section = section.strip()

        if section:
            chunks.append(section)

    return chunks


def search_document(question, chunks):

    if not chunks:
        return "No information found in the document."

    vectorizer = TfidfVectorizer(stop_words="english")

    documents = chunks + [question]

    vectors = vectorizer.fit_transform(documents)

    similarities = cosine_similarity(
        vectors[-1],
        vectors[:-1]
    )[0]

    best_index = similarities.argmax()
    best_score = similarities[best_index]

    if best_score < 0.10:
        return "Sorry, I could not find relevant information in the SOP."

    return chunks[best_index]


def main():

    if not PDF_PATH.exists():
        print("SOP PDF not found.")
        return

    text = load_pdf_text(PDF_PATH)

    chunks = create_chunks(text)

    print("===================================")
    print("   SMART FACTORY RAG ASSISTANT")
    print("===================================")

    print(f"Loaded document: {PDF_PATH.name}")
    print(f"Document sections: {len(chunks)}")

    while True:

        question = input("\nAsk your question: ")

        if question.lower() in ["exit", "quit"]:
            print("Assistant closed.")
            break

        answer = search_document(
            question,
            chunks
        )

        print("\nAnswer:")
        print(answer)


if __name__ == "__main__":
    main()