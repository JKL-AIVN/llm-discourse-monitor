# LLM Discourse Landscape: Automated Semantic Analysis & IP Risk Pipeline

**Author:** Tsz Chun Liu (qwerty) | Cultural Studies, CUHK
**Methodology:** Research through Design (RtD) & Digital Ethnography

---

## 1. Problem Statement
The rapid evolution of Large Language Models (LLMs) makes manual tracking of public discourse impossible for individual researchers. Furthermore, traditional cloud-native automated watchers (e.g., GitHub Actions) are increasingly obstructed by aggressive anti-bot infrastructure (403 Forbidden errors), which prevents data-center IPs from accessing critical transcript data. This project addresses the need for a resilient, automated monitoring system that captures the "actual" technical and ideological claims made by discourse leaders, rather than just relying on metadata.

---

## 2. Methodology: The Hybrid-Edge Collection Model
To ensure 100% data integrity and bypass cloud-level fingerprinting, the architecture utilizes a **Hybrid-Edge** approach:

* **Data Extraction (Edge Node):** A Python script (`tracker.py`) executes on a high-performance local node. It utilizes `yt-dlp` and `youtube-transcript-api` to fetch raw transcripts, effectively bypassing YouTube's data-center IP blocks.
* **Semantic Processing Engine:** Raw transcripts are piped into the local **Gemini CLI**. Using structured prompt engineering, the LLM acts as a "Digital Ethnographer," parsing transcripts into strictly formatted JSON to identify speaker stances, key technologies, and ideological clusters.
* **Cloud Presentation Layer:** The materialized data (`data.json`) is pushed to the repository, where a vanilla JavaScript/Tailwind CSS frontend is statically hosted on **GitHub Pages** for public review.

---

## 3. Evaluation Dataset
The current evaluation dataset consists of **14+ analyzed video records** dynamically captured from two primary LLM discourse leaders:
* **Matthew Berman:** Focuses on "Accelerationism" and developer-centric infrastructure.
* **AI Explained:** Focuses on "AI Safety," systemic risk, and the sociotechnical impact of LLMs.
* The dataset includes raw `.jsonl` logs for auditing and a processed `.json` array for frontend rendering.

---

## 4. Evaluation Methods
The system's accuracy and stability are evaluated through three primary mechanisms:
* **Qualitative Semantic Validation:** Periodic manual audits comparing Gemini-generated summaries (`speaker_stance`) against original transcripts to ensure core theses are preserved.
* **Prompt Robustness & JSON Integrity:** The pipeline uses regex-based extraction and JSON validation to handle model output variance and ensure the stateful registry remains uncorrupted.
* **IP Risk Labeling:** An automated risk matrix categorizes content based on the technologies discussed (e.g., Generative Image models vs. Administrative Agents) to quantify legal and ethical exposure.

---

## 5. Experimental Results: Ideological Mapping
The pipeline successfully identified a fundamental tension in the LLM landscape:
* **The "Builder" Stance (Matthew Berman):** Strongly advocates for developer autonomy and critiques "corporate gatekeeping" (e.g., Anthropic's ban on OpenClaw).
* **The "Observer" Stance (AI Explained):** Frames AI as an existential risk comparable to nuclear weapons, advocating for urgent democratization and government regulation.
* **Live Dashboard:** All findings are visualized in the [Live Dashboard](https://jkl-aivn.github.io/llm-discourse-monitor/), providing a real-time ethnographic map of these conflicting narratives.

---

## 🛡️ IP Risk Assessment Matrix
* **🔴 HIGH RISK:** Generative visual models (e.g., Midjourney, GPT Image 2) due to non-consensual web scraping.
* **🟠 MEDIUM RISK:** Third-party API harnesses and Terms of Service workarounds (e.g., OpenClaw controversy).
* **🟢 LOW RISK:** Administrative automation and high-level philosophical safety discussions.

---

## 🛠️ Tech Stack
* **Data Extraction:** `yt-dlp`, `youtube-transcript-api`
* **Analysis Engine:** Google `Gemini CLI`
* **Frontend:** HTML5, modern JavaScript (ES6+), **Tailwind CSS**
* **Deployment:** Git, GitHub Pages

---

## 🚀 Future Work
* **Proxy Integration:** Implementing rotating residential proxies to return the Edge Node to a fully cloud-native CI/CD pipeline.
* **Semantic Chunking:** Introducing recursive text-chunking to process long-form podcast transcripts without context loss.
