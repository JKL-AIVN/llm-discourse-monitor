# LLM Discourse Landscape: Automated Semantic Analysis & IP Risk Pipeline

**Author:** Tsz Chun Liu (Jack) | Cultural Studies, CUHK
**Methodology:** Research through Design (RtD) & Digital Ethnography

---

## 📌 Project Overview
This project serves as a socio-technical laboratory to analyze the evolving public discourse surrounding Large Language Models (LLMs) and Generative AI. By deploying an automated data pipeline, this system continuously extracts, semantically analyzes, and visualizes the ideological stances and Intellectual Property (IP) risks embedded in prominent tech commentary channels on YouTube.

The resulting dashboard provides a real-time, ethnographic mapping of the tension between **"Accelerationist Builders"** and **"Safety-focused Observers"** in the contemporary AI landscape.

🔗 **[Live Dashboard (GitHub Pages)](https://YOUR_GITHUB_USERNAME.github.io/llm-discourse-monitor/)** *(Note: Update this link to your actual GitHub Pages URL)*

---

## 🏗️ Deployment Architecture: The Hybrid-Edge Model

Initial deployment attempts utilized a fully cloud-native CI/CD approach via GitHub Actions. However, due to YouTube's aggressive anti-bot infrastructure, requests from cloud Data Center IPs (like Azure/GitHub runners) were consistently blocked (returning `403 Forbidden` or CAPTCHA challenges). 

To ensure 100% data integrity and bypass cloud-level fingerprinting, the architecture was pivoted to a highly resilient **Hybrid-Edge Collection** model:

1. **Edge Node Collection (Local Environment):** A Python-based extraction script (`tracker.py`) runs on a high-performance local edge node. It utilizes `yt-dlp` and `youtube-transcript-api` (with fallback mechanisms) to scrape raw transcripts, bypassing data-center IP bans.
2. **Semantic Processing Engine:** Raw transcripts are piped via standard input into the local **Gemini CLI**. Using highly structured prompt engineering, the LLM acts as a "Digital Ethnographer," parsing 15,000+ character transcripts into strictly formatted JSON, identifying speaker stances, ideological clusters, and copyright risk profiles.
3. **Cloud Presentation Layer:** The parsed, materialized view (`data.json`) is pushed to the repository. The frontend—built with vanilla JavaScript and styled with Tailwind CSS—is statically hosted on GitHub Pages, ensuring a lightweight, decoupled, and highly responsive user interface.

---

## 🔬 Key Ethnographic Findings (Case Study)

Based on the automated comparative analysis of our two primary monitored subjects, distinct ideological clusters have emerged:

### 1. Matthew Berman: The "Developer Accelerationist"
* **Focus:** Infrastructure bottlenecks, hardware limitations (GPU crunches), and open-source vs. proprietary model performance.
* **Tone:** Technically enthusiastic ("Performance Hype").
* **Ideology:** Strongly advocates for developer autonomy and "Zero Switching Cost," frequently critiquing corporate gatekeeping and restrictive Terms of Service (e.g., Anthropic's platform bans).

### 2. AI Explained: The "Socio-Technical Skeptic"
* **Focus:** Existential risks, user-experience friction, and the geopolitical implications of hyper-centralized tech monopolies.
* **Tone:** Analytically skeptical ("Transformational Hype").
* **Ideology:** Aligns with AI Safety and Longtermism. Focuses on the societal implications of "magical powers" and the urgent need for institutional oversight, warning against the loss of human agency.

---

## 🛡️ IP Risk Assessment Matrix
The pipeline utilizes the LLM to assign automated IP Risk levels based on the specific technologies discussed:
* **🔴 HIGH RISK:** Generative visual models (e.g., Midjourney, GPT Image 2). High likelihood of outputting styles or likenesses derived from non-consensual web scraping.
* **🟠 MEDIUM RISK:** Third-party API harnessing and ToS workarounds. Legal gray areas regarding Model-as-a-Service (MaaS) extraction.
* **🟢 LOW RISK:** Administrative automation, meeting summarization, and philosophical/systemic discussions that fall clearly under fair use.

---

## 🛠️ Tech Stack
* **Data Extraction:** `yt-dlp`, `youtube-transcript-api`
* **Analysis Engine:** Google `Gemini CLI` (Native Windows Subprocess Piping)
* **Frontend:** HTML5, modern JavaScript (ES6+), **Tailwind CSS**
* **Deployment:** Git, GitHub Pages

---

## 🚀 Known Limitations & Future Work
* **Proxy Integration:** To transition the Edge Node back to a fully automated cloud CI/CD pipeline, future iterations will implement a rotating Residential Proxy network to natively bypass YouTube's rate-limiting on automated cloud runners.
* **Semantic Chunking:** Current transcript ingestion is capped to preserve context windows. Future updates will introduce recursive text-chunking algorithms to process hour-long podcast transcripts without data loss.
