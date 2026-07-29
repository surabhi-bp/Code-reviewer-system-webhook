# Gemini AI Provider Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate `google-generativeai` via a new `GeminiProvider` class and update the application default provider and configuration to use Gemini (`gemini-1.5-flash`).

**Architecture:** Create `GeminiProvider` implementing `AIProvider` strategy interface (`app/services/ai/base.py`). Update `ReviewOrchestratorService` default provider from `OllamaProvider` to `GeminiProvider`.

**Tech Stack:** Python 3, Flask, `google-generativeai`, `pytest`.

## Global Constraints
- `google-generativeai` added to `requirements.txt`.
- Provider file: `app/services/ai/gemini_provider.py`.
- Must configure `google.generativeai.configure(api_key=os.getenv("GEMINI_API_KEY"))`.
- Must use model `gemini-1.5-flash`.
- Class `GeminiProvider` must implement `analyze(self, prompt: str) -> str` (with `generate(self, prompt: str) -> str` alias).
- No webhooks, database models, or parsing logic modified.

---

### Task 1: Add dependency and implement GeminiProvider

**Files:**
- Modify: `requirements.txt`
- Create: `app/services/ai/gemini_provider.py`
- Modify: `app/services/ai/__init__.py`
- Create: `tests/test_gemini_provider.py`

**Interfaces:**
- Consumes: `AIProvider` (`app/services/ai/base.py`)
- Produces: `GeminiProvider` (`app/services/ai/gemini_provider.py`)

- [ ] **Step 1: Update requirements.txt**
Add `google-generativeai` to `requirements.txt`.

- [ ] **Step 2: Create failing test for GeminiProvider**
Create `tests/test_gemini_provider.py` with mock tests verifying initialization and `analyze` / `generate` methods.

- [ ] **Step 3: Implement GeminiProvider**
Create `app/services/ai/gemini_provider.py` and export in `app/services/ai/__init__.py`.

- [ ] **Step 4: Run tests to verify GeminiProvider passes**
Run pytest for `tests/test_gemini_provider.py`.

- [ ] **Step 5: Commit changes**
Commit dependency and `GeminiProvider` implementation.

---

### Task 2: Integrate GeminiProvider into ReviewOrchestrator and configuration

**Files:**
- Modify: `app/services/review_orchestrator.py`
- Modify: `tests/test_review_orchestrator.py` (if existing, or verify integration tests)

**Interfaces:**
- Consumes: `GeminiProvider` from `app.services.ai.gemini_provider`
- Produces: Updated `ReviewOrchestratorService` defaulting to `GeminiProvider`

- [ ] **Step 1: Write test verifying default provider is GeminiProvider**
Write test checking default `ai_provider` in `ReviewOrchestratorService`.

- [ ] **Step 2: Update ReviewOrchestratorService**
In `app/services/review_orchestrator.py`, import `GeminiProvider` and set `self.ai_provider = ai_provider or GeminiProvider()`. Also default `model_name` fallback to `gemini-1.5-flash`.

- [ ] **Step 3: Run pytest across full suite**
Run `pytest` to confirm all tests pass cleanly.

- [ ] **Step 4: Commit changes**
Commit `ReviewOrchestratorService` integration.
