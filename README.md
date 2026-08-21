# IT Incident Assistant

An AI-powered multi-agent system for automating IT incident ticket analysis, classification, prioritization, assignment recommendation, and resolution assistance using Retrieval-Augmented Generation (RAG).

---

## 📌 Project Overview

IT support teams handle a large number of incident tickets every day. Manually analyzing each ticket, assigning its category and priority, finding similar historical incidents, and identifying possible resolutions can be time-consuming.

The **IT Incident Assistant** automates this process using a multi-agent architecture.

The system takes a new IT incident as input and:

- Finds historically similar incidents using semantic search
- Classifies the incident into a category and subcategory
- Determines its priority
- Recommends the appropriate support category
- Suggests a resolution based on historical incidents
- Coordinates all agents through a central Supervisor Agent

---

## 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │      New Ticket      │
                         │ Subject + Description│
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Supervisor Agent   │
                         │    Orchestrator      │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
      ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
      │   Retrieval   │     │ Classification│     │    Priority   │
      │     Agent     │     │     Agent     │     │     Agent     │
      └───────┬───────┘     └───────────────┘     └───────────────┘
              │
              ▼
      ┌───────────────┐
      │   Assignment  │
      │ Recommendation│
      │     Agent     │
      └───────┬───────┘
              │
              ▼
      ┌───────────────┐
      │   Resolution  │
      │     Agent     │
      └───────┬───────┘
              │
              ▼
       ┌────────────────┐
       │   Final Result │
       │ Classification │
       │ Priority       │
       │ Assignment     │
       │ Resolution     │
       └────────────────┘
