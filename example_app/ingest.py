"""Build a FAISS vector store from the documents in the data directory."""

from pathlib import Path

from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


def ingest_documents() -> None:
    """Create a FAISS index from every text file in the data folder."""
    load_dotenv()

    data_dir = Path(__file__).parent / "data"
    output_dir = Path(__file__).parent / "stores" / "help_center"
    output_dir.parent.mkdir(parents=True, exist_ok=True)

    files = sorted([p for p in data_dir.glob("**/*") if p.is_file()])
    if not files:
        raise FileNotFoundError(
            "No documents were found in the data directory. Add markdown or text files and try again."
        )

    docs = []
    for path in files:
        loader = TextLoader(str(path), encoding="utf-8")
        loaded = loader.load()
        for doc in loaded:
            # Normalise metadata so downstream evaluation can reference concise sources.
            doc.metadata["source"] = str(path.relative_to(data_dir))
            if "title" not in doc.metadata:
                first_line = doc.page_content.strip().splitlines()[0:1]
                if first_line:
                    title = first_line[0].lstrip("# ").strip()
                    if title:
                        doc.metadata["title"] = title
        docs.extend(loaded)

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    splits = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(splits, embeddings)
    vectorstore.save_local(str(output_dir))

    print(f"Ingested {len(files)} files and created {len(splits)} chunks.")
    print(f"Vector store saved to: {output_dir}")


if __name__ == "__main__":
    ingest_documents()
