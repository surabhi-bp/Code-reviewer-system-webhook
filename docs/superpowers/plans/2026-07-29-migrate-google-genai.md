# Migrate to google-genai SDK Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate `GeminiProvider` and package dependencies from deprecated `google-generativeai` to the new `google-genai` SDK.

**Architecture:** Update `requirements.txt`, update `app/services/ai/gemini_provider.py` to use `from google import genai` and `genai.Client()`, and update `tests/test_gemini_provider.py`.

**Tech Stack:** Python 3, `google-genai`, Flask, `pytest`.

## Global Constraints
- `google-generativeai` removed, `google-genai` added in `requirements.txt`.
- Provider file: `app/services/ai/gemini_provider.py`.
- Must import `from google import genai` and `from google.genai import types`.
- Must use `client.models.generate_content(model=self.model_name, contents=prompt)`.
- Unit tests in `tests/test_gemini_provider.py` updated and green.

---

### Task 1: Update requirements.txt and migrate GeminiProvider & unit tests to google-genai

**Files:**
- Modify: `requirements.txt`
- Modify: `app/services/ai/gemini_provider.py`
- Modify: `tests/test_gemini_provider.py`

**Interfaces:**
- Consumes: `google.genai` Client & `models.generate_content`
- Produces: Updated `GeminiProvider` using `google-genai`

- [ ] **Step 1: Update requirements.txt**
Replace `google-generativeai` with `google-genai`.

- [ ] **Step 2: Update GeminiProvider implementation**
In `app/services/ai/gemini_provider.py`, update imports and use `genai.Client(api_key=api_key)`.

- [ ] **Step 3: Update unit tests in test_gemini_provider.py**
Update mock patches in `tests/test_gemini_provider.py` to target `google.genai.Client`.

- [ ] **Step 4: Run pytest**
Run `pytest` to verify test suite passes.

- [ ] **Step 5: Commit changes**
Commit changes to git.
