# Simple RAG Test without API tokens
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
import os
from dotenv import load_dotenv

load_dotenv()

# Load web content
loader = WebBaseLoader(
    web_paths=["https://abhay-nautiyal.github.io/"]
)
docs = loader.load()

# Split documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

# Create vector store
vectorstore = FAISS.from_documents(documents=splits, embedding=OpenAIEmbeddings())

# Create prompt
prompt = hub.pull("rlm/rag-prompt")

# Create LLM (using OpenAI instead of HuggingFace)
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model_name="gpt-3.5-turbo")

# Create RAG chain
rag_chain = (
    {"context": vectorstore.as_retriever(), "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Test function
def test_rag_query(query):
    """Test a query with RAG system"""
    print(f"\n🎯 Query: '{query}'")
    
    try:
        result = rag_chain.invoke({"question": query})
        print(f"📝 Answer: {result}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

# Test queries
test_queries = [
    "What is this about?",
    "What projects are mentioned?", 
    "How can I contact?",
    "What skills are shown?"
]

print("🧪 Testing RAG System")
print("="*60)

for query in test_queries:
    test_rag_query(query)
