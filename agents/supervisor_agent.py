from loguru import logger

from llm.phi_model import Phi3Model

from agents.classification_agent import ClassificationAgent
from agents.priority_agent import PriorityAgent
from agents.assignment_agent import AssignmentRecommendationAgent
from agents.resolution_agent import ResolutionAgent
from agents.retrieval_agent import RetrievalAgent


class SupervisorAgent:
    """
    Main orchestrator for the IT Incident Assistant.

    The Supervisor receives a new incident and coordinates:

    1. Retrieval
    2. Classification
    3. Priority
    4. Assignment Recommendation
    5. Resolution

    The default demo pipeline is RAG/rule based and does not
    require slow Phi-3 generation.
    """

    def __init__(self, load_llm=False):

        logger.info("=" * 60)
        logger.info("Initializing Supervisor Agent")
        logger.info("=" * 60)

        # --------------------------------------------------
        # OPTIONAL PHI-3
        # --------------------------------------------------

        self.llm = None

        if load_llm:

            logger.info("Loading optional Phi-3 Mini...")

            self.llm = Phi3Model()

        else:

            logger.info(
                "Phi-3 disabled for fast demo mode."
            )

        # --------------------------------------------------
        # RETRIEVAL
        # --------------------------------------------------

        logger.info("Loading shared Retrieval Agent...")

        self.retrieval_agent = RetrievalAgent(
            top_k=5
        )

        # --------------------------------------------------
        # CLASSIFICATION
        # --------------------------------------------------

        logger.info("Loading Classification Agent...")

        self.classification_agent = ClassificationAgent(
            llm=self.llm
        )

        # --------------------------------------------------
        # PRIORITY
        # --------------------------------------------------

        logger.info("Loading Priority Agent...")

        self.priority_agent = PriorityAgent(
            llm=self.llm
        )

        # --------------------------------------------------
        # ASSIGNMENT
        # --------------------------------------------------

        logger.info(
            "Loading Assignment Recommendation Agent..."
        )

        self.assignment_agent = AssignmentRecommendationAgent()

        # --------------------------------------------------
        # RESOLUTION
        # --------------------------------------------------

        logger.info("Loading Resolution Agent...")

        self.resolution_agent = ResolutionAgent(
            top_k=5,
            llm=self.llm
        )

        logger.info("=" * 60)
        logger.info(
            "Supervisor Agent initialized successfully"
        )
        logger.info("=" * 60)

    def process_ticket(
        self,
        subject: str,
        description: str
    ):

        logger.info("Processing new IT incident...")

        if not subject and not description:
            raise ValueError(
                "Subject and description cannot both be empty."
            )

        ticket_text = f"""
Subject: {subject}

Description:
{description}
"""

        # --------------------------------------------------
        # 1. RETRIEVAL
        # --------------------------------------------------

        logger.info(
            "Running Retrieval Agent..."
        )

        similar_tickets = (
            self.retrieval_agent.retrieve_for_resolution(
                ticket_text
            )
        )

        logger.info(
            f"Retrieved {len(similar_tickets)} "
            f"similar historical tickets."
        )

        # --------------------------------------------------
        # 2. CLASSIFICATION
        # --------------------------------------------------

        logger.info(
            "Running Classification Agent..."
        )

        classification = (
            self.classification_agent.classify(
                subject,
                description,
                retrieved_tickets=similar_tickets
            )
        )

        # --------------------------------------------------
        # 3. PRIORITY
        # --------------------------------------------------

        logger.info(
            "Running Priority Agent..."
        )

        priority = (
            self.priority_agent.determine_priority(
                subject,
                description,
                retrieved_tickets=similar_tickets
            )
        )

        # --------------------------------------------------
        # 4. ASSIGNMENT
        # --------------------------------------------------

        logger.info(
            "Running Assignment Recommendation Agent..."
        )

        assignment = self.assignment_agent.recommend(
            similar_tickets
        )

        # --------------------------------------------------
        # 5. RESOLUTION
        # --------------------------------------------------

        logger.info(
            "Running Resolution Agent..."
        )

        resolution = (
            self.resolution_agent.generate_resolution(
                ticket_text,
                similar_tickets=similar_tickets,
                use_llm=False
            )
        )

        # --------------------------------------------------
        # FINAL RESULT
        # --------------------------------------------------

        result = {

            "ticket": {
                "subject": subject,
                "description": description
            },

            "classification": classification,

            "priority": priority,

            "assignment": assignment,

            "resolution": resolution,

            "similar_tickets": similar_tickets
        }

        logger.info(
            "IT incident processing completed successfully."
        )

        return result