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
```
---

## 👥 **Project Architecture**

The project follows a modular multi-agent architecture where each agent has a specific responsibility.

This makes the system:

- Modular
- Maintainable
- Extensible
- Easier to test
- Easier to integrate with APIs and user interfaces
---
## ⚙️ Current Workflow

The current end-to-end workflow is:
```
1. User provides incident
          ↓
2. Supervisor receives incident
          ↓
3. Retrieval Agent finds similar tickets
          ↓
4. Classification Agent determines category
          ↓
5. Priority Agent determines urgency
          ↓
6. Assignment Agent recommends support category
          ↓
7. Resolution Agent retrieves relevant historical resolution
          ↓
8. Supervisor combines all results
          ↓
9. Final incident analysis is returned
```
---
## 🛠️ Technology Stack
| Component            | Technology                       |
| -------------------- | -------------------------------- |
| Programming Language | Python                           |
| LLM                  | Microsoft Phi-3 Mini 4K Instruct |
| Embedding Model      | BAAI/bge-small-en-v1.5           |
| Vector Database      | FAISS                            |
| RAG                  | Retrieval-Augmented Generation   |
| API                  | FastAPI                          |
| Agent Architecture   | Multi-Agent Architecture         |
| Logging              | Loguru                           |
| Version Control      | Git / GitHub                     |
---

## 📜 License

This project is developed as part of an internship project.

## 👩‍💻 Author

Raghavi Saxena  
Akanksha  
B.Tech Computer Science & Engineering
