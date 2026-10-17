"""Streamlit UI for Production RAG System"""
import streamlit as st
import httpx
import json
from datetime import datetime
from typing import Optional
import pandas as pd

# Configuration
API_BASE_URL = "http://nginx/api/v1"
UPLOAD_API = f"{API_BASE_URL}/documents/upload"
TEXT_API = f"{API_BASE_URL}/documents/text"
QUERY_API = f"{API_BASE_URL}/query"
LIST_API = f"{API_BASE_URL}/documents"
DELETE_API = f"{API_BASE_URL}/documents"
HEALTH_API = "http://nginx/api/v1/health"

st.set_page_config(
    page_title="Production RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


def check_health() -> dict:
    """Check API health"""
    try:
        response = httpx.get(HEALTH_API, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Cannot connect to API: {e}")
    return None


def upload_file(file, metadata: Optional[dict] = None) -> dict:
    """Upload file to API"""
    try:
        files = {"file": (file.name, file, file.type)}
        data = {}
        if metadata:
            data["metadata"] = json.dumps(metadata)

        response = httpx.post(UPLOAD_API, files=files, data=data, timeout=120)
        return response.json()
    except Exception as e:
        st.error(f"Upload error: {e}")
        return None


def add_text_document(content: str, filename: str, metadata: Optional[dict] = None) -> dict:
    """Add text document via API"""
    try:
        payload = {
            "content": content,
            "filename": filename,
        }
        if metadata:
            payload["metadata"] = metadata

        response = httpx.post(TEXT_API, json=payload, timeout=60)
        return response.json()
    except Exception as e:
        st.error(f"Error adding text: {e}")
        return None


def query_rag(query: str, session_id: str, top_k: int = 5, temperature: float = 0.7) -> dict:
    """Query RAG system"""
    try:
        payload = {
            "query": query,
            "session_id": session_id,
            "top_k": top_k,
            "temperature": temperature,
        }
        response = httpx.post(QUERY_API, json=payload, timeout=120)
        return response.json()
    except Exception as e:
        st.error(f"Query error: {e}")
        return None


def list_documents() -> dict:
    """List all documents"""
    try:
        response = httpx.get(LIST_API, timeout=10)
        return response.json()
    except Exception as e:
        st.error(f"Error listing documents: {e}")
        return None


def delete_document(document_id: str) -> dict:
    """Delete document"""
    try:
        response = httpx.delete(f"{DELETE_API}/{document_id}", timeout=10)
        return response.json()
    except Exception as e:
        st.error(f"Delete error: {e}")
        return None


# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
if "messages" not in st.session_state:
    st.session_state.messages = []


# Main UI
st.title("🤖 Production RAG System")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    # Health check
    if st.button("🔍 Check System Health"):
        with st.spinner("Checking..."):
            health = check_health()
            if health:
                st.success(f"Status: {health['status']}")
                with st.expander("Service Details"):
                    for service, status in health['services'].items():
                        icon = "✅" if status == "healthy" else "❌"
                        st.write(f"{icon} {service}: {status}")

    st.markdown("---")

    # Query parameters
    st.subheader("Query Settings")
    top_k = st.slider("Number of Results", 1, 20, 5)
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)

    st.markdown("---")
    st.caption(f"Session ID: {st.session_state.session_id}")

    if st.button("🔄 New Session"):
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.messages = []
        st.rerun()


# Tabs
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📄 Documents", "📊 Document Library"])

# Tab 1: Chat Interface
with tab1:
    st.header("Chat with your documents")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show sources if available
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📚 Sources"):
                    for idx, source in enumerate(message["sources"], 1):
                        st.markdown(f"**Source {idx}**: {source['filename']} (chunk {source['chunk_index']})")
                        st.caption(f"Score: {source.get('score', 0):.3f}")
                        st.text(source['content'][:200] + "...")

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = query_rag(
                    query=prompt,
                    session_id=st.session_state.session_id,
                    top_k=top_k,
                    temperature=temperature
                )

                if result:
                    st.markdown(result["answer"])

                    # Show metadata
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption(f"⏱️ Response time: {result['response_time']:.2f}s")
                    with col2:
                        st.caption(f"🤖 Model: {result['model_used']}")

                    # Store assistant message with sources
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result.get("sources", [])
                    })

                    # Show sources
                    if result.get("sources"):
                        with st.expander("📚 Sources"):
                            for idx, source in enumerate(result["sources"], 1):
                                st.markdown(f"**Source {idx}**: {source['filename']} (chunk {source['chunk_index']})")
                                st.caption(f"Score: {source.get('score', 0):.3f}")
                                st.text(source['content'][:200] + "...")

# Tab 2: Document Upload
with tab2:
    st.header("Upload Documents")

    upload_method = st.radio("Upload Method", ["File Upload", "Text Input"])

    if upload_method == "File Upload":
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "txt"],
            help="Upload PDF or text files"
        )

        if uploaded_file:
            st.info(f"Selected: {uploaded_file.name} ({uploaded_file.size} bytes)")

            # Optional metadata
            with st.expander("Add Metadata (Optional)"):
                col1, col2 = st.columns(2)
                with col1:
                    author = st.text_input("Author")
                    source = st.text_input("Source")
                with col2:
                    tags = st.text_input("Tags (comma-separated)")

            if st.button("📤 Upload Document"):
                metadata = {}
                if author:
                    metadata["author"] = author
                if source:
                    metadata["source"] = source
                if tags:
                    metadata["tags"] = [t.strip() for t in tags.split(",")]

                with st.spinner("Uploading and processing..."):
                    result = upload_file(uploaded_file, metadata if metadata else None)

                    if result and result.get("status") == "success":
                        st.success(f"✅ {result['message']}")
                        st.info(f"Document ID: {result['document_id']}")
                        st.info(f"Chunks created: {result['chunk_count']}")
                    else:
                        st.error("Upload failed")

    else:  # Text Input
        st.subheader("Add Text Document")

        filename = st.text_input("Document Name", placeholder="my_document.txt")
        content = st.text_area("Content", height=300, placeholder="Enter your text here...")

        # Optional metadata
        with st.expander("Add Metadata (Optional)"):
            col1, col2 = st.columns(2)
            with col1:
                author = st.text_input("Author", key="text_author")
                source = st.text_input("Source", key="text_source")
            with col2:
                tags = st.text_input("Tags (comma-separated)", key="text_tags")

        if st.button("📝 Add Text Document"):
            if not filename or not content:
                st.error("Please provide both filename and content")
            else:
                metadata = {}
                if author:
                    metadata["author"] = author
                if source:
                    metadata["source"] = source
                if tags:
                    metadata["tags"] = [t.strip() for t in tags.split(",")]

                with st.spinner("Processing..."):
                    result = add_text_document(content, filename, metadata if metadata else None)

                    if result and result.get("status") == "success":
                        st.success(f"✅ {result['message']}")
                        st.info(f"Document ID: {result['document_id']}")
                        st.info(f"Chunks created: {result['chunk_count']}")
                    else:
                        st.error("Failed to add document")

# Tab 3: Document Library
with tab3:
    st.header("Document Library")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh"):
            st.rerun()

    # List documents
    docs_data = list_documents()

    if docs_data and docs_data.get("documents"):
        st.info(f"Total documents: {docs_data['total']}")

        # Create dataframe
        df = pd.DataFrame(docs_data["documents"])
        df["created_at"] = pd.to_datetime(df["created_at"])

        # Display table
        for idx, doc in df.iterrows():
            with st.expander(f"📄 {doc['filename']} ({doc['file_type'].upper()})"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Size**: {doc['file_size']} bytes")
                    st.write(f"**Chunks**: {doc['chunk_count']}")
                with col2:
                    st.write(f"**Created**: {doc['created_at'].strftime('%Y-%m-%d %H:%M')}")
                with col3:
                    if st.button("🗑️ Delete", key=f"del_{doc['document_id']}"):
                        with st.spinner("Deleting..."):
                            result = delete_document(doc['document_id'])
                            if result and result.get("status") == "success":
                                st.success("Document deleted!")
                                st.rerun()
                            else:
                                st.error("Delete failed")

                st.caption(f"Document ID: {doc['document_id']}")
    else:
        st.info("No documents uploaded yet. Go to the Documents tab to upload some!")

# Footer
st.markdown("---")
st.caption("Production RAG System v1.0.0")
