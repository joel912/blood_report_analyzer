# components/rag_engine.py

import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_groq import ChatGroq


# ─────────────────────────────────────────────
# EMBEDDINGS
# ─────────────────────────────────────────────

def load_embedding_model():
    """
    Load the HuggingFace embedding model.
    Downloads ~90MB on first run, cached after.
    """
    print("Loading embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        
    )

    print("Embedding model loaded!")
    return embeddings


# ─────────────────────────────────────────────
# VECTOR STORE
# ─────────────────────────────────────────────

def create_vector_store(chunks, embeddings):
    """
    Convert text chunks into vectors and store in FAISS.
    """
    if not chunks:
        raise ValueError("No chunks provided to create vector store.")

    print(f"Creating vector store from {len(chunks)} chunks...")

    try:
        vector_store = FAISS.from_documents(
            documents=chunks,
            embedding=embeddings
        )
    except Exception as e:
        raise RuntimeError(f"Failed to create FAISS vector store: {e}")

    print("Vector store created!")
    return vector_store


def get_retriever(vector_store, k=4):
    """
    Convert vector store into a LangChain retriever.
    k = number of chunks to retrieve per query.
    """
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )
    return retriever


def search_similar_chunks(vector_store, query, k=4):
    """
    Directly search vector store. Used for testing.
    Returns list of (Document, score) tuples.
    """
    results = vector_store.similarity_search_with_score(query, k=k)
    return results


# ─────────────────────────────────────────────
# LLM
# ─────────────────────────────────────────────

def load_llm():
    """
    Load Groq's Llama 3 model via LangChain.

    Why Groq?
    - Free tier with generous limits
    - Extremely fast inference
    - Runs Llama 3 (Meta's open source model)

    Why llama-3.1-8b-instant?
    - 8 billion parameters — smart enough for medical text
    - 'instant' = optimized for speed on Groq hardware
    - Free to use

    Returns:
        ChatGroq LLM object
    """
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. "
            "Check your .env file."
        )

    # Initialize Groq LLM using explicit Groq client params to avoid any
    # accidental routing to OpenAI-compatible clients.
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.1-8b-instant",
        temperature=0.3,
        # temperature controls creativity:
        # 0.0 = very factual and consistent
        # 1.0 = more creative and varied
        # 0.3 is good for medical analysis
        max_tokens=1024,
    )

    return llm


# ─────────────────────────────────────────────
# PROMPT TEMPLATES
# ─────────────────────────────────────────────

def get_rag_prompt():
    """
    Prompt template for general Q&A about the blood report.

    {context} = chunks retrieved from FAISS
    {question} = user's question

    The system message sets the AI's behavior.
    The human message is what the user asks.
    """

    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a helpful medical assistant specializing in \
blood report analysis. Your job is to help patients understand \
their blood test results in simple, clear language.

Use ONLY the information provided in the context below to answer \
the question. If the answer is not in the context, say \
"I couldn't find that information in your report."

Always:
- Use simple, non-technical language
- Mention the actual values from the report
- Note if a value is normal or abnormal
- Be reassuring but accurate

Context from the blood report:
{context}"""
        ),
        (
            "human",
            "{question}"
        )
    ])

    return template


def get_summary_prompt():
    """
    Prompt template specifically for generating
    a full blood report summary.
    """

    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a medical assistant. Analyze the blood report \
data provided and give a clear, structured summary.

Format your response exactly like this:

## Overall Assessment
[2-3 sentence general overview]

## Key Findings
[List the most important test results with their values]

## Normal Values
[List tests that are within normal range]

## Values Needing Attention
[List any abnormal values and briefly explain why they matter]

## Recommendation
[General advice — always recommend consulting a doctor]

Keep language simple and avoid medical jargon where possible.

Blood Report Data:
{context}"""
        ),
        (
            "human",
            "Please provide a complete summary of this blood report."
        )
    ])

    return template


def get_abnormal_prompt():
    """
    Prompt template specifically for detecting
    abnormal values in the blood report.
    """

    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a medical assistant analyzing blood test results.

From the blood report data below, identify ALL abnormal values.

For each abnormal value, respond in this exact format:

ABNORMAL_START
Test Name: [name]
Patient Value: [value with unit]
Normal Range: [range]
Status: [HIGH or LOW]
Explanation: [one sentence plain English explanation]
ABNORMAL_END

If all values are normal, say: "All values are within normal range."

Blood Report Data:
{context}"""
        ),
        (
            "human",
            "List all abnormal values found in this blood report."
        )
    ])

    return template


# ─────────────────────────────────────────────
# HELPER: Format retrieved docs into a string
# ─────────────────────────────────────────────

def format_docs(docs):
    """
    Convert a list of Document objects into a single string.
    This string becomes the {context} in our prompts.

    Args:
        docs: list of LangChain Document objects

    Returns:
        single string with all document content joined
    """
    return "\n\n".join(
        f"[Page {doc.metadata.get('page', '?')}]\n{doc.page_content}"
        for doc in docs
    )


# ─────────────────────────────────────────────
# RAG CHAINS
# ─────────────────────────────────────────────

def build_qa_chain(retriever, llm):
    """
    Build the main Q&A RAG chain using LCEL pipe syntax.

    How this chain works step by step:
    1. RunnableParallel runs two things at the same time:
       - "context": retriever finds relevant chunks → format_docs
       - "question": passes the question through unchanged
    2. prompt template fills {context} and {question}
    3. llm generates the answer
    4. StrOutputParser extracts just the text string

    The | operator means "pipe the output into the next step"

    Args:
        retriever: FAISS retriever from get_retriever()
        llm: ChatGroq LLM from load_llm()

    Returns:
        Runnable chain
    """

    prompt = get_rag_prompt()
    output_parser = StrOutputParser()

    # Build the chain
    chain = (
        RunnableParallel({
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
            # RunnablePassthrough just passes the input through unchanged
        })
        | prompt
        | llm
        | output_parser
    )

    return chain


def build_summary_chain(vector_store, llm):
    """
    Build a chain specifically for generating a full summary.

    For summary, we retrieve MORE chunks (k=8) to get
    a comprehensive view of the entire report.
    """

    # Use a larger k for summary to get more context
    summary_retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 8}
    )

    prompt = get_summary_prompt()
    output_parser = StrOutputParser()

    chain = (
        RunnableParallel({
            "context": summary_retriever | format_docs,
            "question": RunnablePassthrough()
        })
        | prompt
        | llm
        | output_parser
    )

    return chain


def build_abnormal_chain(vector_store, llm):
    """
    Build a chain specifically for detecting abnormal values.
    Retrieves maximum chunks to scan the whole report.
    """

    abnormal_retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 10}
    )

    prompt = get_abnormal_prompt()
    output_parser = StrOutputParser()

    chain = (
        RunnableParallel({
            "context": abnormal_retriever | format_docs,
            "question": RunnablePassthrough()
        })
        | prompt
        | llm
        | output_parser
    )

    return chain


# ─────────────────────────────────────────────
# MAIN PIPELINE BUILDER
# ─────────────────────────────────────────────
def get_conversational_prompt():
    """
    Prompt template that includes chat history for memory.
    {chat_history} = previous messages
    {context}      = retrieved chunks from FAISS
    {question}     = current user question
    """
    template = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a helpful medical assistant specializing \
in blood report analysis. Help the patient understand their \
blood test results clearly and simply.

Use ONLY the information from the blood report context to answer. \
If the answer isn't in the context, say so honestly.

Previous conversation:
{chat_history}

Blood report context:
{context}"""
        ),
        (
            "human",
            "{question}"
        )
    ])
    return template


def build_conversational_chain(retriever, llm):
    """
    RAG chain that includes conversation history.
    Manually injects chat_history into the prompt.

    Args:
        retriever: FAISS retriever
        llm: ChatGroq LLM

    Returns:
        Runnable chain that accepts
        {"question": ..., "chat_history": ...}
    """
    prompt = get_conversational_prompt()
    output_parser = StrOutputParser()

    chain = (
        RunnableParallel({
            "context": (
                lambda x: x["question"]
            ) | retriever | format_docs,
            "question"    : lambda x: x["question"],
            "chat_history": lambda x: x.get("chat_history", "")
        })
        | prompt
        | llm
        | output_parser
    )

    return chain


def build_rag_pipeline(chunks):
    """
    Full pipeline: chunks → embeddings → FAISS → LLM → chains.
    Called from app.py after PDF processing.

    Returns:
        dict with everything needed to run the app
    """

    # Basic validation
    if not chunks:
        raise ValueError("No document chunks provided to build_rag_pipeline.")

    # Step 1: Embeddings
    embeddings = load_embedding_model()

    # Step 2: Vector store
    vector_store = create_vector_store(chunks, embeddings)

    # Step 3: Retriever
    retriever = get_retriever(vector_store, k=4)

    # Step 4: LLM
    llm = load_llm()

    # Step 5: Build all chains
    qa_chain       = build_qa_chain(retriever, llm)
    summary_chain  = build_summary_chain(vector_store, llm)
    abnormal_chain = build_abnormal_chain(vector_store, llm)
    conv_chain     = build_conversational_chain(retriever, llm)
    conv_chain     = build_conversational_chain(retriever, llm)

    return {
        "vector_store"  : vector_store,
        "retriever"     : retriever,
        "embeddings"    : embeddings,
        "llm"           : llm,
        "qa_chain"      : qa_chain,
        "summary_chain" : summary_chain,
        "abnormal_chain": abnormal_chain,
        "conv_chain"    : conv_chain,
    }