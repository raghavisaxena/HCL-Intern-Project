from embedding_pipeline.embedder import TicketEmbedder


def main():

    embedder = TicketEmbedder()

    texts = [
        "My VPN connection keeps disconnecting",
        "I forgot my password and cannot login",
        "The application crashes when I open it",
    ]

    embeddings = embedder.embed_documents(texts)

    print("\nEmbedding shape:")
    print(embeddings.shape)

    query = embedder.embed_query(
        "My remote office connection keeps dropping"
    )

    print("\nQuery shape:")
    print(query.shape)


if __name__ == "__main__":
    main()