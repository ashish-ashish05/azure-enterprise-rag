import os

import requests
import streamlit as st


API_URL = os.getenv(
    "RAG_API_URL",
    "http://127.0.0.1:8000",
)


st.set_page_config(
    page_title="Enterprise RAG",
    page_icon="📚",
    layout="wide",
)


st.title("Enterprise RAG")
st.caption(
    "Ask questions about your enterprise documents."
)


with st.sidebar:
    st.header("Search options")

    document_family_id = st.text_input(
        "Document family",
        placeholder="Optional, e.g. ExpensePolicy",
    )

    top_k = st.slider(
        "Number of sources",
        min_value=1,
        max_value=10,
        value=5,
    )


question = st.text_area(
    "Ask a question",
    placeholder="What is the expense policy?",
    height=120,
)


ask = st.button(
    "Ask",
    type="primary",
    use_container_width=True,
)


if ask:
    if not question.strip():
        st.warning("Please enter a question.")
        st.stop()

    payload = {
        "question": question,
        "top_k": top_k,
    }

    if document_family_id.strip():
        payload["document_family_id"] = (
            document_family_id.strip()
        )

    try:
        with st.spinner("Searching enterprise documents..."):
            response = requests.post(
                f"{API_URL}/api/v1/query",
                json=payload,
                timeout=120,
            )

        if response.status_code != 200:
            st.error(
                f"API error ({response.status_code}): "
                f"{response.text}"
            )
            st.stop()

        data = response.json()

    except requests.RequestException as exc:
        st.error(
            "Could not connect to the RAG API. "
            "Make sure FastAPI is running."
        )
        st.exception(exc)
        st.stop()

    st.subheader("Answer")

    st.write(data["answer"])

    sources = data.get("sources", [])

    st.divider()
    st.subheader(
        f"Sources ({len(sources)})"
    )

    if not sources:
        st.info(
            "No source documents were returned."
        )
    else:
        for index, source in enumerate(
            sources,
            start=1,
        ):
            with st.expander(
                f"Source {index}: "
                f"{source['source']}"
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(
                        f"**Family:** "
                        f"{source['document_family_id']}"
                    )
                    st.write(
                        f"**Version:** "
                        f"{source.get('document_version') or 'N/A'}"
                    )

                with col2:
                    st.write(
                        f"**Page:** "
                        f"{source.get('page') or 'N/A'}"
                    )
                    st.write(
                        f"**Chunk:** "
                        f"{source['chunk_index']}"
                    )

                effective_date = source.get(
                    "effective_date"
                )

                if effective_date:
                    st.write(
                        f"**Effective:** "
                        f"{effective_date}"
                    )