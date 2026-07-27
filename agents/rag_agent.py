import os
from groq import Groq
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vectorstore = None
retriever = None


def build_rag_pipeline(filing_text: str, company: str) -> bool:
    """Build RAG pipeline from filing text"""
    global vectorstore, retriever

    print(f"📄 Building RAG pipeline for {company}...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    doc = Document(
        page_content=filing_text,
        metadata={"company": company, "source": "SEC 10-K"}
    )
    chunks = splitter.split_documents([doc])

    try:
        import chromadb
        client = chromadb.Client()
        client.delete_collection("finsight")
    except:
        pass

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="finsight"
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    print(f"✅ RAG pipeline ready — {len(chunks)} chunks indexed!")
    return True


def rag_agent(question: str, company: str) -> str:
    """Answer a question using the RAG pipeline"""
    if retriever is None:
        return "RAG pipeline not initialized — filing not loaded."

    print(f"🔍 RAG Agent searching for: {question}")

    docs = retriever.invoke(question)
    context = "\n\n".join(doc.page_content for doc in docs)

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