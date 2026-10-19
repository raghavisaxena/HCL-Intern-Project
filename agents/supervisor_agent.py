import time
from loguru import logger

from llm.groq_model import GroqModel

from agents.classification_agent import ClassificationAgent
from agents.priority_agent import PriorityAgent
from agents.assignment_agent import AssignmentRecommendationAgent
from agents.resolution_agent import ResolutionAgent
from agents.retrieval_agent import RetrievalAgent
from agents.diagnostics_agent import run_diagnostics

def log_step_banner(step_num, total_steps, agent_name, elapsed):
    banner = f"STEP {step_num}/{total_steps}: {agent_name.upper()} ... DONE ({elapsed}s)"
    line = "=" * len(banner)
    logger.info(f"\n{line}\n{banner}\n{line}")

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

            logger.info("Loading Groq model...")

            self.llm = GroqModel()

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

        agent_timings = {}
        # --------------------------------------------------
        # 1. RETRIEVAL
        # --------------------------------------------------

        logger.info(
            "Running Retrieval Agent..."
        )
        _t0 = time.time()

        similar_tickets = (
            self.retrieval_agent.retrieve_for_resolution(
                ticket_text
            )
        )
        agent_timings["retrieval"] = round(time.time() - _t0, 2)

        logger.info(
            f"Retrieved {len(similar_tickets)} "
            f"similar historical tickets."
        )

        log_step_banner(1, 5, "retrieval", agent_timings["retrieval"])
        yield {
            "type": "progress",
            "agent": "retrieval",
            "status": "done",
            "time": agent_timings["retrieval"]
        }
        time.sleep(0.5)

        # --------------------------------------------------
        # 2. CLASSIFICATION
        # --------------------------------------------------

        logger.info(
            "Running Classification Agent..."
        )
        _t0 = time.time()

        classification = (
            self.classification_agent.classify(
                subject,
                description,
                retrieved_tickets=similar_tickets
            )
        )
        agent_timings["classification"] = round(time.time() - _t0, 2)

        log_step_banner(2, 5, "classification", agent_timings["classification"])
        yield {
            "type": "progress",
            "agent": "classification",
            "status": "done",
            "time": agent_timings["classification"]
        }
        time.sleep(0.5)

        # --------------------------------------------------
        # 3. PRIORITY
        # --------------------------------------------------

        logger.info(
            "Running Priority Agent..."
        )
        _t0 = time.time()

        priority = (
            self.priority_agent.determine_priority(
                subject,
                description,
                retrieved_tickets=similar_tickets
            )
        )
        agent_timings["priority"] = round(time.time() - _t0, 2)

        log_step_banner(3, 5, "priority", agent_timings["priority"])
        yield {
            "type": "progress",
            "agent": "priority",
            "status": "done",
            "time": agent_timings["priority"]
        }
        time.sleep(0.5)

        # --------------------------------------------------
        # 4. ASSIGNMENT
        # --------------------------------------------------

        logger.info(
            "Running Assignment Recommendation Agent..."
        )
        _t0 = time.time()

        assignment = self.assignment_agent.recommend(
            similar_tickets
        )
        agent_timings["assignment"] = round(time.time() - _t0, 2)

        log_step_banner(4, 5, "assignment", agent_timings["assignment"])
        yield {
            "type": "progress",
            "agent": "assignment",
            "status": "done",
            "time": agent_timings["assignment"]
        }
        time.sleep(0.5)

        # --------------------------------------------------
        # 5. RESOLUTION
        # --------------------------------------------------

        logger.info(
            "Running Resolution Agent..."
        )
        _t0 = time.time()

        resolution = (
            self.resolution_agent.generate_resolution(
                ticket_text,
                similar_tickets=similar_tickets,
                use_llm=self.llm is not None,
            )
        )
        agent_timings["resolution"] = round(time.time() - _t0, 2)

        log_step_banner(5, 5, "resolution", agent_timings["resolution"])
        yield {
            "type": "progress",
            "agent": "resolution",
            "status": "done",
            "time": agent_timings["resolution"]
        }
        time.sleep(0.5)
        # Real network diagnostics (returns [] for non-network tickets)
        diagnostics = run_diagnostics(ticket_text)

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

            "similar_tickets": similar_tickets,
            "agent_timings": agent_timings,
            "diagnostics": diagnostics
        }

        logger.info(
            "IT incident processing completed successfully."
        )

        yield {
            "type": "final",
            "result": result
        }