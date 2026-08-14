from embedding_pipeline.embedder import TicketEmbedder
from embedding_pipeline.vector_store import load_index, search


TEST_QUERIES = [
    "My remote connection to the office network keeps dropping every few minutes",
    "I forgot my password and need help getting back into my account",
    "The application crashes immediately every time I try to open it",
]


def main():

    embedder = TicketEmbedder()

    index, metadata = load_index()

    for query in TEST_QUERIES:

        print("\n" + "=" * 70)
        print(f"QUERY: {query}")
        print("=" * 70)

        query_vector = embedder.embed_query(query)

        results = search(
            index,
            metadata,
            query_vector,
            top_k=3
        )

        for i, row in results.iterrows():

            print(
                f"\n#{i + 1} | "
                f"similarity={row['similarity_score']:.3f} | "
                f"{row['ticket_id']}"
            )

            print(
                f"Subject: {row['subject']}"
            )

            print(
                f"Category: {row['category']} | "
                f"Priority: {row['priority_raw']}"
            )


if __name__ == "__main__":
    main()