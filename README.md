

***

# Project Report: LLM Discourse Landscape Tracker

**Author:** Tsz Chun Liu (qwerty) | Cultural Studies, CUHK  
**Status:** Phase 1 Prototype (Hybrid-Edge Implementation)  
**Methodology:** Research through Design (RtD) & Digital Ethnography  

---

## 1. Problem Statement
The Large Language Model (LLM) ecosystem evolves at a pace that outstrips manual monitoring. Existing trackers often rely on metadata such as titles and thumbnails, which fail to capture the nuanced ideological stances and technical critiques shared by creators within actual video content. 

Furthermore, automated cloud-based collection (e.g., GitHub Actions) faces significant infrastructure barriers, as platforms like YouTube aggressively block Data Center IPs. There is a critical need for a resilient monitoring system that can bypass these restrictions to provide deep semantic insights into the "builder" vs. "observer" divide in AI discourse.

## 2. Methodology
To ensure high data integrity and engineering reliability, this project utilizes a **Hybrid-Edge Collection** architecture:

* **Data Extraction (Edge Node):** A Python-based engine (`tracker.py`) executes on a local edge node to bypass cloud-native IP bans. It utilizes `yt-dlp` and `youtube-transcript-api` to scrape raw transcripts directly from creators' outputs.
* **Semantic Analysis Engine:** Transcripts are piped into the **Gemini CLI**. Using structured prompt engineering, the LLM acts as a "Digital Ethnographer" to parse long-form text (15,000+ characters) into structured JSON, identifying speaker stances and ideological clusters.
* **Presentation Layer:** The system exports a materialized view (`data.json`) to a public **GitHub Pages** dashboard. The frontend uses vanilla JavaScript and Tailwind CSS to dynamically render findings in a browser-accessible format.

## 3. Evaluation Dataset
The evaluation dataset consists of a dynamic registry of 14+ analyzed video records from two primary channels representing opposite ends of the LLM discourse spectrum:

* **Matthew Berman:** Focuses on "Capability" and "Developer Utility." Key technologies analyzed include GPT Image 2, Claude 4.7, and the OpenClaw ban.
* **AI Explained:** Focuses on "Systemic Impact" and "AI Safety." Key technologies analyzed include Zoom AI Companion, AI Agents, and the societal implications of AGI.

## 4. Evaluation Methods
The system's performance is evaluated through a qualitative and ethical framework:
* **Semantic Integrity Check:** Manual verification of the `speaker_stance` and `core_thesis` against original transcripts to ensure the LLM accurately captures the creator’s intent.
* **Automated IP Risk Matrix:** A custom-built risk assessment logic that categorizes content into **High**, **Medium**, or **Low** risk based on the legal and ethical implications of the technologies discussed (e.g., generative visual models vs. administrative automation).
* **Prototype Limitations:** As a first-phase prototype, the system currently prioritizes semantic depth over automated benchmarking. Future iterations will include "LLM-as-a-Judge" scoring to quantify hallucination rates during summarization.

## 5. Experimental Results
The automated pipeline successfully mapped a clear ideological divide between the monitored subjects:

* **The Accelerationist Builder (Berman):** Discourse focuses on raw performance (ELO scores), infrastructure (GPU crunches), and a rejection of corporate "safety" narratives that limit developer autonomy.
* **The Safety-Focused Observer (AI Explained):** Discourse positions AI as an existential risk comparable to nuclear weapons, emphasizing the need for democratization and urgent government regulation.
* **Infrastructure Validation:** The Hybrid-Edge model successfully maintained a consistent data flow despite YouTube’s 403 Forbidden blocks on cloud runners, proving the viability of edge-based collection for sensitive scraping tasks.

---

### 🛠️ Tech Stack
* **Backend:** Python 3.10+, `yt-dlp`, `youtube-transcript-api`
* **AI Engine:** Google Gemini CLI (Native Windows Subprocess Piping)
* **Frontend:** HTML5, JavaScript (ES6), **Tailwind CSS**
* **Deployment:** Git, GitHub Pages

---

🔗 **[View Live Dashboard](https://jkl-aivn.github.io/llm-discourse-monitor/)**
