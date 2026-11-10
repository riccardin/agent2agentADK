# Google Cloud Vertex AI & Model Integration Guide

This document covers the mandatory configuration, architecture, and pricing structures required to deploy and consume **Google Gemini models** and **Anthropic Claude models** using Google Cloud's unified AI platform.

---

## 1. Required APIs & Services to Enable

To use both native Google models and third-party partner models (like Anthropic), you must enable the following specific APIs in your Google Cloud Project:

1. **`aiplatform.googleapis.com` (Vertex AI API):** The foundational core service that manages model access, orchestration, and deployments.
2. **`cloudaicomputing.googleapis.com` (Model Garden Service / Third-Party Models API):** Required specifically for enabling third-party, partner-managed marketplace models like **Anthropic Claude** within the platform framework.

---

## 2. Conceptual Architecture Diagram Flow

```
+---------------------------------------------------------------------------------+
|                               YOUR APPLICATION                                  |
|          (Python / Node.js SDK, REST API Client, or LangChain/LlamaIndex)       |
+---------------------------------------------------------------------------------+
                                         |
                                         |  Authenticates via IAM Service Account
                                         |  (Role: Vertex AI User / Administrator)
                                         v
+---------------------------------------------------------------------------------+
|                     GOOGLE CLOUD IDENTITY & ACCESS MANAGEMENT                  |
|                 Verifies Credentials & Evaluates IAM Permissions                |
+---------------------------------------------------------------------------------+
                                         |
                                         |  Routes Request
                                         v
+---------------------------------------------------------------------------------+
|                     GEMINI ENTERPRISE PLATFORM (VERTEX AI HUB)                  |
|                     Enabled Core API: aiplatform.googleapis.com                 |
+---------------------------------------------------------------------------------+
                      |                                   |
       [ Native Google Models ]              [ Partner Marketplace Models ]
                      |                                   |
                      v                                   v
+-------------------------------------------+   +---------------------------------+
|          VERTEX AI MODEL GARDEN           |   |     THIRD-PARTY EXTENSION       |
|    Hosts Google DeepMind Frameworks       |   | API: cloudaicomputing.googleapis.com
+-------------------------------------------+   +---------------------------------+
                      |                                   |
         +------------+------------+                      |  Routes Securely via
         |                         |                      |  Private Service Connect
         v                         v                      v
+------------------+     +------------------+   +---------------------------------+
| Gemini 1.5/2.0   |     | Gemini 3.1       |   |        ANTHROPIC CLAUDE         |
| Flash / Pro      |     | Argon / Omni     |   |     (Claude 3.5 Sonnet /        |
| (Speed & Volume) |     | (Advanced Agent) |   |      Claude 4.6 Opus)           |
+------------------+     +------------------+   +---------------------------------+
```

---

## 3. Step-by-Step Enablement & Billing Rules

* **Active Google Cloud Billing Account Required:** Free Trial projects or unbilled sandboxes cannot consume third-party models. Anthropic models have zero free allocations and will reject requests if an active billing account is missing.
* **No Anthropic API Key Needed:** Authentication is handled natively through standard Google Cloud IAM service accounts (`roles/aiplatform.user`).

| Step | Component / Action | Service Name / Command | Key Role / Requirement |
| :--- | :--- | :--- | :--- |
| **1** | Core Platform API | `aiplatform.googleapis.com` | Enables native Google Gemini models. |
| **2** | Partner Models API | `cloudaicomputing.googleapis.com` | Enables the third-party framework for Anthropic models. |
| **3** | Model Agreement | **Model Garden Console** | Navigate to **Claude** in Model Garden and click **"Enable/Agree to Terms"**. |
| **4** | Client Auth | **IAM Service Account** | Grant role: `roles/aiplatform.user` (Vertex AI User). |

---

## 4. Financial Matrix: Gemini vs. Anthropic Claude (Per 1 Million Tokens)

Google Cloud uses strict pay-as-you-go consumption billing. All token consumption is calculated per 1 million tokens and aggregated onto your standard monthly Google Cloud invoice.

### Anthropic Claude Family Rates
*Rates match Anthropic direct developer endpoints.*

| Model Family | Active Model Generation | Input Cost (Per 1M Tokens) | Output Cost (Per 1M Tokens) | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Claude Fable** | Claude Fable 5.1 | **$10.00** | **$50.00** | Advanced frontier reasoning, long-horizon agents |
| **Claude Opus** | Claude Opus 5.5 | **$4.00** | **$20.00** | Deep complex coding, knowledge workflows |
| **Claude Sonnet** | Claude Sonnet 5.5 | **$2.00** | **$10.00** | Production default, balanced speed/intelligence |
| **Claude Haiku** | Claude Haiku 5.5 | **$0.10** | **$0.50** | Ultra-low latency, high-volume agents |

### Native Google Gemini Family Rates
*Optimized for high-volume orchestration and native multimodal datasets.*

| Model Family | Active Model Generation | Input Cost (Per 1M Tokens) | Output Cost (Per 1M Tokens) | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Gemini Pro** | Gemini 4 Argon / 3.1 Pro | **$2.00** | **$10.00** | Complex analytical math, deep system coding, high reasoning |
| **Gemini Flash** | Gemini 3.8 Flash | **$0.75** | **$3.75** | Fast conversational agents, general automation |
| **Gemini Flash-Lite**| Gemini 3.5 Flash-Lite | **$0.30** | **$2.50** | High-frequency basic tasks, routing, data classification |

---

## 5. Architectural & Billing Distinctions

* **Prompt Caching:** Anthropic supports prompt caching for long documents, dropping read hits to a low fraction of the baseline cost. Gemini natively provides context caching on Google Cloud infrastructure.
* **Context Windows:** Anthropic prices tokens flatly across the entire window. Gemini utilizes structured pricing tiers where rates scale upward for extremely large prompts exceeding 200,000 tokens.
* **Batch Predictions:** Vertex AI allows you to submit asynchronous batch jobs for both providers, cutting standard pay-as-you-go token costs cleanly by **50%**.