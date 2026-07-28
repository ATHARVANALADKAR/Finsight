import os
from groq import Groq

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# store chunks in memory instead of chromadb
document_chunks = []


def build_rag_pipeline(filing_text: str, company: str) -> bool:
    """Split filing into chunks and store in memory"""
    global document_chunks

    print(f"📄 Building RAG pipeline for {company}...")

    # simple chunking — split by paragraphs
    chunks = []
    paragraphs = filing_text.split("\n\n")

    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) < 1000:
            current_chunk += para + "\n\n"
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    document_chunks = chunks
    print(f"✅ RAG pipeline ready — {len(chunks)} chunks stored!")
    return True


def simple_search(question: str, top_k: int = 3) -> list[str]:
    """
    Simple keyword-based search over chunks
    No embeddings needed — works within memory limits
    """
    if not document_chunks:
        return []

    question_words = set(question.lower().split())

    # score each chunk by keyword overlap
    scored = []
    for chunk in document_chunks:
        chunk_words = set(chunk.lower().split())
        overlap = len(question_words & chunk_words)
        scored.append((overlap, chunk))

    # return top k chunks by overlap score
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored[:top_k] if score > 0]


def rag_agent(question: str, company: str) -> str:
    """Answer a question using keyword search + LLM"""
    if not document_chunks:
        return "RAG pipeline not initialized — filing not loaded."

    print(f"🔍 RAG Agent searching for: {question}")

    # retrieve relevant chunks
    relevant_chunks = simple_search(question, top_k=3)

    if not relevant_chunks:
        return "Not found in filing."

    context = "\n\n".join(relevant_chunks)

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": f"""You are a financial research assistant analyzing {company}'s SEC 10-K filing.
Answer using ONLY the context provided.
Be specific and factual. Include numbers when available.
If the answer is not in the context say 'Not found in filing.'"""
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}"
            }
        ]
    )

    result = response.choices[0].message.content
    print("✅ RAG Agent done!")
    return result