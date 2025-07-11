# 🤖 Personal Profile Extractor AI Agent

## ✨ Overview

The **Personal Profile Extractor AI Agent** is a cutting-edge LangGraph-powered solution designed to intelligently extract structured personal information from a wide range of unstructured and semi-structured dialogue sources. Leveraging the advanced capabilities of **GPT-4o**, this agent streamlines the process of building and updating personal profiles, making it ideal for recruitment, HR, market research, and personal knowledge management.

This versatile tool can ingest various input formats, including raw text, PDF documents, audio files (MP3, WAV), and web links (YouTube, Wikipedia). It offers users the flexibility to create new profiles or seamlessly update existing ones in a database via an intuitive **Streamlit web interface**. The extracted information is then meticulously validated using Pydantic, ensuring data integrity and consistency. Finally, the extracted profiles are presented in both a clean, resume-like format and a raw JSON format for easy viewing and export.

The agent's extraction capabilities are highly generalized, designed to identify and categorize a comprehensive set of personal information fields from any conversational context.

## 🚀 Features

  * **Interactive Streamlit UI**: A user-friendly web interface for seamless interaction with the AI agent.
  * **Multimodal Input Support**:
      * **Text**: Raw text input.
      * **Documents**: PDF files.
      * **Audio**: MP3 and WAV files (automatic transcription).
      * **Web Links**: YouTube video transcripts, Wikipedia page content.
  * **Intelligent Information Extraction**: Utilizes **GPT-4o** for highly accurate and context-aware extraction of diverse personal information fields.
  * **Dynamic Profile Management**:
      * **New Profile Creation**: Generate a complete new personal profile.
      * **Profile Updates**: Incrementally update existing profiles with new information.
  * **Robust Data Validation**: Employs **Pydantic** for rigorous schema validation of all extracted data, ensuring accuracy and consistency.
  * **ChromaDB Integration**: Stores extracted and updated profiles (or their embeddings for retrieval) securely in a **ChromaDB vector database**.
  * **Flexible Output Formats**:
      * **Organized Resume View**: Presents extracted information in a human-readable, resume-like layout within the Streamlit app.
      * **Raw JSON Export**: Provides a clean JSON output for programmatic access and integration, also downloadable from the UI.
  * **LangGraph Orchestration**: Built on LangGraph for robust, stateful, and modular AI agent workflow management.
  * **Generalized Extraction Fields**: Designed to extract a wide array of personal information, adaptable to various dialogue styles and content.

-----

## ⚙️ How It Works

The AI agent operates through a sophisticated LangGraph-orchestrated workflow, exposed via a Streamlit interface:

1.  **Input Ingestion (Streamlit UI)**: The user provides input via Streamlit widgets (text areas, file uploaders, URL inputs) in one of the supported formats.
2.  **Preprocessing**:
      * Text inputs are tokenized and cleaned.
      * PDF files are converted to text.
      * MP3/WAV files are transcribed into text using a robust speech-to-text model (`pydub` helps with audio handling).
      * YouTube links are processed to extract video transcripts (`yt-dlp`); Wikipedia and other web links fetch page content (`beautifulsoup4`).
3.  **User Choice (Streamlit UI)**: The user selects whether to create a new profile or update an existing one using Streamlit radio buttons or select boxes, potentially providing a profile ID for updates.
4.  **GPT-4o Extraction**: The preprocessed text is fed to **GPT-4o**, which is prompted to extract structured personal information based on a predefined, comprehensive schema.
5.  **Pydantic Validation**: The raw JSON output from GPT-4o is then validated against a Pydantic model. This step ensures that all extracted fields conform to the expected data types and structures, flagging any inconsistencies.
6.  **Database Management (ChromaDB)**: The validated data is stored or updated in **ChromaDB**. This could involve storing the raw extracted data directly or creating vector embeddings of the data for efficient similarity search and retrieval.
      * If creating a new profile, the validated data is inserted as a new entry.
      * If updating, the validated data is merged with the existing profile, intelligently handling conflicts and appending new information.
7.  **Output Generation (Streamlit UI)**:
      * The consolidated profile data is formatted into an aesthetically pleasing, resume-like display using Streamlit's `st.markdown` or `st.write`.
      * The complete profile data is also provided in a raw JSON format for easy export and integration with other systems, displayed using `st.json`.

-----

## 🛠️ Installation

Let's get your project set up\! You'll primarily use `pip`, Python's standard package installer.

### Prerequisites

  * **Python**: You'll need Python installed on your computer. Aim for Python 3.9 or newer.
      * [Image of Python logo]
      * **How to check**: Open your terminal or command prompt and type `python --version` or `python3 --version`. If it's not installed or is an older version, download it from [python.org](https://www.python.org/downloads/).
  * **FFmpeg**: This is crucial for handling audio files (MP3, WAV).
    \*
      * **How to get it**: Download FFmpeg from [ffmpeg.org/download.html](https://ffmpeg.org/download.html). Follow their instructions to install it and make sure it's added to your system's PATH. (This means your computer can find and run `ffmpeg` commands from anywhere in the terminal).
  * **OpenAI API Key**: You'll need an API key from OpenAI to use GPT-4o. Get one from your [OpenAI dashboard](https://platform.openai.com/account/api-keys).

### Steps to Get Started

1.  **Download the Project Files**:

      * If you have a `.zip` file of the project, simply **unzip it** to a folder on your computer (e.g., `personal-profile-extractor`).
      * If you're getting the code directly from a source like GitHub, you'd typically "clone" it, which means downloading a copy. For now, just ensure you have all the project's files in a dedicated folder.

2.  **Open Your Terminal/Command Prompt**:

      * Navigate to the folder where you unzipped/downloaded your project files. For example, if your folder is `personal_info_extractor` on your desktop:
        ```bash
        cd Desktop/personal_info_extractor
        ```
      * This step is important because it tells your computer where to look for the project files when you run commands.

3.  **Install Required Libraries**:

      * You'll install all the necessary Python libraries using `pip`.
      * You can install them manually one by one (or all at once):
        ```bash
        pip install streamlit langchain langgraph pydantic openai beautifulsoup4 yt-dlp pydub chromadb
        ```
      * These libraries are:
          * **`streamlit`**: For the interactive web interface.
          * **`langchain`**: Foundational tools for LLM applications.
          * **`langgraph`**: For orchestrating the AI agent's workflow.
          * **`pydantic`**: For validating the extracted information.
          * **`openai`**: To interact with the GPT-4o model.
          * **`beautifulsoup4`**: For parsing web page content (like Wikipedia).
          * **`yt-dlp`**: For downloading YouTube video transcripts.
          * **`pydub`**: For handling and processing audio files.
          * **`chromadb`**: Your chosen database for storing profiles.

4.  **Set Up Your Environment Variables**:

      * You'll need to tell the application your OpenAI API key and where to store your ChromaDB data.
      * Create a file named `.env` in the main project folder (the same folder where your `app.py` or `main.py` is).
      * Add the following lines to this `.env` file:
        ```env
        OPENAI_API_KEY="your_openai_api_key_here"
        # ChromaDB will typically store data in a local folder by default.
        # If you want to specify a particular path, you might add:
        # CHROMA_DB_PATH="./chroma_data"
        ```
      * **Replace `"your_openai_api_key_here"` with your actual OpenAI API Key.**
      * **Important**: Do not share your `.env` file or API keys publicly\!

5.  **ChromaDB Setup**:

      * Since ChromaDB is a local vector database by default, you typically don't need a separate "database initialization" step like with traditional SQL databases.
      * When your application runs and tries to connect to ChromaDB, it will automatically create the necessary files and structures in the specified `CHROMA_DB_PATH` (or a default location if not specified) if they don't already exist.

-----

## 🚀 Usage

To start the interactive web application, open your terminal or command prompt, navigate to your project folder (as you did in step 2 of installation), and run:

```bash
streamlit run Main_Page.py
```

This command will open a new tab in your web browser with the Streamlit interface, allowing you to interact with the Personal Profile Extractor AI Agent.

**Key UI Elements you can expect:**

  * **Input Section**: File upload widgets for PDFs/audio, and input fields for YouTube/Wikipedia links.
  * **Action Selector**: Dropdown to choose between "Create New Profile" and "Update Existing Profile."
  * **Processing Status**: Indicators (spinners, messages) to show when the agent is processing input.
  * **Output Display**: Dedicated sections for the resume-style formatted output and the raw JSON output.

-----

## 📊 Sample Extracted Personal Profile

To illustrate the powerful capabilities of the AI Agent, here's a sample of a personal profile that has been extracted and validated based on the comprehensive schema defined in the project.

```json
{
  "name": "Jane Miller",
  "age": 32,
  "location": "London, UK",
  "gender": "Female",
  "nationality": "British",
  "ethnicity": "Caucasian",
  "marital_status": "Single",
  "visa_or_work_permit_status": "Citizen",
  "education": [
    {
      "degree": "Master of Science",
      "major": "Artificial Intelligence",
      "institution": "University College London (UCL)",
      "start_date": "2015-09",
      "end_date": "2016-09",
      "details": "Specialized in Natural Language Processing."
    },
    {
      "degree": "Bachelor of Engineering",
      "major": "Computer Science",
      "institution": "University of Bristol",
      "start_date": "2012-09",
      "end_date": "2015-06",
      "details": "Graduated with First Class Honours."
    }
  ],
  "work_experience": [
    {
      "title": "Senior AI Research Scientist",
      "company": "DeepMind",
      "location": "London, UK",
      "start_date": "2020-03",
      "end_date": "Present",
      "responsibilities": [
        "Led a team of 5 researchers in developing novel LLM architectures.",
        "Published research papers in top-tier AI conferences (NeurIPS, ICML).",
        "Mentored junior scientists and interns."
      ],
      "achievements_in_role": [
        "Developed a new attention mechanism improving model efficiency by 15%.",
        "Secured a patent for novel neural network design."
      ],
      "projects_involved": [
        "Project Alpha (Large Language Model R&D)",
        "Neural Search Optimization"
      ]
    },
    {
      "title": "AI Engineer",
      "company": "Google AI",
      "location": "Mountain View, CA, USA",
      "start_date": "2016-10",
      "end_date": "2020-02",
      "responsibilities": [
        "Designed and implemented machine learning pipelines for product features.",
        "Collaborated with cross-functional teams to deploy AI solutions.",
        "Conducted A/B testing and performance analysis."
      ],
      "achievements_in_role": [
        "Optimized recommendation engine, increasing user engagement by 10%.",
        "Received 'Spotlight Award' for innovative solution to data sparsity."
      ],
      "projects_involved": [
        "Personalized Content Recommendation System",
        "Internal Data Annotation Platform"
      ]
    }
  ],
  "personal_projects": [
    {
      "name": "Sentiment Analyzer for Social Media",
      "description": "A Python-based tool using pre-trained NLP models to analyze sentiment from Twitter feeds.",
      "technologies_used": ["Python", "NLTK", "Flask", "Tweepy"],
      "link": "https://github.com/janemiller/sentiment-analyzer"
    }
  ],
  "publications_or_research": [
    {
      "title": "Adaptive Attention for Transformer Models in Low-Resource Settings",
      "journal_or_conference": "NeurIPS 2023 Workshop on Efficient AI",
      "publication_date": "2023-12",
      "authors": ["Jane Miller", "Alex Chen"],
      "abstract_summary": "Explores a novel attention mechanism to improve performance of Transformer models on datasets with limited training data.",
      "link": "https://arxiv.org/abs/2312.XXXXX"
    }
  ],
  "certifications": [
    {
      "name": "Deep Learning Specialization",
      "issuing_organization": "Coursera (DeepLearning.AI)",
      "date_obtained": "2017-08",
      "link": "https://www.coursera.org/verify/XYZABCDEF"
    }
  ],
  "achievements": [
    {
      "description": "Awarded 'Innovator of the Year' at DeepMind for contributions to model interpretability.",
      "date": "2023",
      "awarding_organization": "DeepMind",
      "type": "Award",
      "is_major_achievement": true
    }
  ],
  "past_challenges": [
    {
      "description": "Faced significant data imbalance in a real-world NLP project.",
      "how_overcome": "Implemented advanced sampling techniques and custom loss functions, collaborating with data engineering team.",
      "lessons_learned": ["Importance of data preprocessing for skewed datasets", "Value of cross-team collaboration"]
    }
  ],
  "strengths": [
    {
      "description": "Strong analytical and problem-solving skills.",
      "examples": ["Successfully debugged complex neural network architectures.", "Developed efficient algorithms to handle large datasets."]
    },
    {
      "description": "Effective technical communication.",
      "examples": ["Presented complex research findings to non-technical stakeholders.", "Authored clear and concise documentation for internal tools."]
    }
  ],
  "weaknesses": [
    {
      "description": "Sometimes over-focus on technical details, delaying broader strategic planning.",
      "steps_to_address": ["Actively practice delegating technical tasks.", "Allocate dedicated time for high-level project visioning."]
    }
  ],
  "goals": [
    {
      "description": "Lead an end-to-end AI product development from conception to deployment.",
      "timeframe": "Next 3-5 years",
      "relevance": "Aspirations for greater leadership and impact."
    }
  ],
  "motivations": [
    {
      "description": "Driven by the desire to solve complex problems and build impactful AI systems.",
      "source": "Intellectual curiosity and passion for innovation."
    }
  ],
  "values": [
    {
      "name": "Innovation",
      "significance": "Believes in pushing boundaries and continuous improvement."
    },
    {
      "name": "Collaboration",
      "significance": "Thrives in team environments and believes in collective problem-solving."
    }
  ],
  "contact_info": [
    {
      "type": "email",
      "value": "jane.miller@example.com"
    },
    {
      "type": "LinkedIn URL",
      "value": "https://www.linkedin.com/in/janemillerai"
    }
  ],
  "interests": ["Hiking", "Photography", "Reading Sci-Fi"],
  "skills": [
    {
      "name": "Python",
      "proficiency": "Expert",
      "category": "Programming Language"
    },
    {
      "name": "PyTorch",
      "proficiency": "Advanced",
      "category": "Deep Learning Framework"
    },
    {
      "name": "Natural Language Processing (NLP)",
      "proficiency": "Expert",
      "category": "AI/ML Discipline"
    },
    {
      "name": "Team Leadership",
      "proficiency": "Advanced",
      "category": "Soft Skill"
    }
  ],
  "tools_or_technologies_used": ["Jira", "Git", "Docker", "AWS Sagemaker"],
  "languages_spoken": ["English - Fluent", "French - Conversational"],
  "professional_background_summary": "Jane Miller is a highly accomplished AI Research Scientist with over 8 years of experience in developing and deploying cutting-edge machine learning and natural language processing solutions. Her career spans influential roles at leading tech companies, where she has focused on large language models, recommendation systems, and innovative AI research, consistently delivering impactful results and driving technological advancements.",
  "current_occupation": "Senior AI Research Scientist at DeepMind",
  "communication_style": "Clear, data-driven, and collaborative.",
  "preferred_learning_style": "Hands-on practical learner, prefers learning by doing and experimenting.",
  "personality_traits": ["Analytical", "Innovative", "Collaborative", "Detail-oriented", "Proactive"],
  "work_preferences": {
    "team_vs_individual": "Prefers collaborative team environment but can work independently.",
    "remote_vs_onsite": "Open to hybrid model, prefers 2-3 days in office.",
    "preferred_industry": "AI Research, Tech, Autonomous Systems",
    "ideal_role": "Lead AI Scientist or Head of Research, focusing on novel AI applications.",
    "company_size_preference": "Mid to large enterprise, strong R&D focus.",
    "work_life_balance_importance": "Values work-life integration, believes in sustainable productivity.",
    "learning_growth_opportunities": "High importance on continuous learning and staying at the forefront of AI research."
  },
  "social_engagement": {
    "volunteering_experience": ["Mentored young women in STEM through 'Girls Who Code' program (2021-Present)"],
    "community_involvement": ["Participated in local hackathons focused on civic tech solutions (2022)"]
  },
  "dialogue_type": ["Technical Interview", "Behavioral Interview"]
}
```

-----

## 💻 Project Structure

```
personal-profile-extractor/
├── .env                       # Environment variables (OpenAI API key, ChromaDB path)
├── README.md                  # This file
├── Main_Page.py               # Main Streamlit application script
├── app.py                     # LangGraph workflow script
├── agents/
│   ├── extractor_agent.py     # Extraction agent node
│   ├── preprocess_agent.py    # Preprocess agent node
│   ├── validator_agent.py     # Validation agent node
│   └── vectorDB_agent.py      # VectorDB storage agent node
├── prompts/
│   ├── extractor_prompt.txt   # Prompt to be used for extraction
│   └── older_prompts.txt      # Previously used prompts
├── schema/
│   └── personal_profile.py    # Pydantic schemas of personal profile and state
├── pages/
│   └── View_Profiles.py       # Additional page to view all profiles currently stored in ChromaDB
├── chroma_db/                 # ChromaDB storage
└── utils/                     
    ├── chroma_utils.py        # ChromaDB functions
    ├── profile_merger.py      # Merging profile information for updating of profiles
    └── profile_to_text.py     # Converting profile to text form

```