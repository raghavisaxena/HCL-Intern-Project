from embedding_pipeline.embedder import TicketEmbedder
from embedding_pipeline.vector_store import load_index, search


class RetrievalAgent:
    """
    Finds historically similar IT tickets using semantic search.
    """

    def __init__(self, top_k: int = 5):
        self.top_k = top_k

        self.embedder = TicketEmbedder()

        self.index, self.metadata = load_index()

    def retrieve(self, ticket_text: str):

        if not ticket_text or not ticket_text.strip():
            raise ValueError("Ticket text cannot be empty.")

        query_vector = self.embedder.embed_query(ticket_text)

        results = search(
            self.index,
            self.metadata,
            query_vector,
            top_k=self.top_k
        )

        return results

    def retrieve_for_resolution(self, ticket_text: str):

        results = self.retrieve(ticket_text)

        retrieved_tickets = []

        for _, row in results.iterrows():
            retrieved_tickets.append({
                "ticket_id": row["ticket_id"],
                "subject": row["subject"],
                "description": row["description"],
                "category": row["category"],
                "subcategory": row["subcategory"],
                "priority": row["priority_raw"],
                "resolution": row["resolution"],
                "similarity_score": float(row["similarity_score"])
            })

        return retrieved_tickets