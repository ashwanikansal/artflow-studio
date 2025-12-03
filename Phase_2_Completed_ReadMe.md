### **📌 Project Title**

**ArtFlow Studio – AI Assistant for Instagram Artists**

### **🧾 Overview**

ArtFlow Studio is an AI-powered assistant built for digital artists who post on Instagram. It helps with:

*   Generating **new art ideas** based on your own style and past posts (RAG).
    
*   Creating **captions + hashtags** tailored to each idea.
    
*   Generating **engagement replies** for comments on your posts.
    
*   Logging everything to **SQLite** and exposing it through a **Streamlit UI**.
    

Phase 1 & 2 focus on:

*   Local, personal use (no auto-posting, no bot spam).
    
*   Learning **RAG, structured outputs, and clean service abstractions**.
    
*   Designing the system so it can later plug into the **Instagram Graph API** and other real-world services.
    

### **✨ Features (current)**

1.  **Personal Art Knowledge Base (RAG)**
    
    *   Ingests your:
        
        *   Past Instagram-style posts (posts.json).
            
        *   Style notes (style\_notes.md).
            
    *   Uses a vector database (**Chroma**) + embeddings to let the model “know” your style and content history.
        
2.  **Trend-aware Content Ideation**
    
    *   Generates **art ideas** (ArtIdeaSet) with:
        
        *   Title
            
        *   Drawing prompt
            
        *   Style direction
            
        *   Why it fits your style
            
        *   Recommended format (reel/image)
            
        *   Difficulty
            
    *   Enriches generation using local **trend data** (trends.json), including:
        
        *   Trending songs / audios (with mood + tags)
            
        *   Visual art challenges / themes
            
3.  **Analytics-aware Ideas**
    
    *   Reads your historical posts.json.
        
    *   Computes basic stats:
        
        *   Average likes & comments
            
        *   Average likes per content type (reel/image)
            
        *   Most-used hashtags
            
    *   Feeds a **summary** of this analytics into the idea generation prompt, so suggestions lean toward what has historically worked better for you.
        
4.  **Caption & Hashtag Generator**
    
    *   For a selected idea, generates:
        
        *   2–3 caption options
            
        *   12–15 hashtags (mix of niche & broad)
            
        *   Optional timelapse tips (since you post timelapse reels)
            
5.  **Engagement Assistant**
    
    *   You paste real comments from your IG post.
        
    *   For each comment, the system generates 2–3 **warm, human-like reply options**.
        
    *   All replies are **human-in-the-loop** – you review & post manually.
        
6.  **SQLite Logging + History**
    
    *   Logs:
        
        *   All generated ideas (IdeaRecord)
            
        *   Captions & hashtags (CaptionRecord)
            
        *   Comments (CommentRecord)
            
        *   Reply suggestions (ReplySuggestionRecord)
            
    *   Includes a **History Viewer**:
        
        *   Recent ideas
            
        *   Captions for a given idea
            
        *   Recent reply suggestions
            
7.  **Streamlit UI**
    
    *   Tab 1: **Ideas & Captions**
        
    *   Tab 2: **Engagement Assistant**
        
    *   Tab 3: **History Viewer** (plus analytics summary)
        

### **🏗 Tech Stack**

*   **Language**

    *   Python

*   **RAG**:    

    *   LangChain
    
    *   Chroma (local vector DB)
    
*   **Database**:
    
    *   SQLite with sqlmodel
        
*   **Frontend**:
    
    *   Streamlit
        
*   **Other**:
    
    *   Pydantic for schemas
        
    *   dotenv for config
        
    *   Custom modules for trends and “Instagram service”


### **🧬 High-Level Architecture**

```

                        ┌──────────────────────────┐
                        │        Streamlit UI      │
                        │  - Ideas & Captions      │
                        │  - Engagement Assistant  │
                        │  - History Viewer        │
                        └────────────┬─────────────┘
                                     │
                                     v
                        ┌──────────────────────────┐
                        │        Application       │
                        │  (FastAPI-like logic in  │
                        │   plain Python modules)  │
                        └────────────┬─────────────┘
       ┌─────────────────────────────┼────────────────────────────────┐
       │                             │                                │
       v                             v                                v
┌────────────────┐        ┌───────────────────────┐        ┌─────────────────────┐
│ RAG Engine     │        │ Trend Service         │        │ Analytics Engine    │
│ - Chroma       │        │ - Local trends.json   │        │ - posts.json        │
│ - Embeddings   │        │   (songs, challenges) │        │ - basic stats:      │
│ - Style notes  │        │                       │        │   likes, hashtags   │
└──────┬─────────┘        └────────────┬──────────┘        └──────────┬──────────┘
       │                               │                              │
       v                               v                              v
┌──────────────────────────┐   ┌──────────────────────────┐   ┌──────────────────────┐
│ Content Ideation Module  │   │ Caption Generator        │   │ Engagement Assistant │
│ - generate_art_ideas()   │   │ - generate captions      │   │ - generate replies   │
│ - uses: RAG + trends +   │   │   + hashtags + tips      │   │   to comments        │
│         analytics        │   └──────────────────────────┘   └──────────────────────┘
└─────────┬────────────────┘
          │
          v
 ┌────────────────────┐
 │ SQLite Database    │
 │ - ideas            │
 │ - captions         │
 │ - comments         │
 │ - reply suggestions│
 └────────────────────┘

```

There’s also an instagram.service module that currently works with local data (posts.json + DB comments) but is designed to be swapped to the real Instagram Graph API later without changing the rest of the code.

### 🚧 Future Work (Phase 3+)

You can list these in the README:

*   Replace local “Instagram service” with **Instagram Graph API**:
    
    *   get\_my\_posts()
        
    *   get\_post\_comments(post\_id)
        
    *   get\_post\_insights(post\_id)
        
*   Replace local trends.json with:
    
    *   **Spotify API** playlists for trending/lo-fi songs.
        
*   Introduce **LangGraph** for:
    
    *   Multi-step workflows:
        
        *   RAG → Trends → Analytics → Ideas → User selection → Captions.
            
    *   Human-in-the-loop nodes (pause after ideas for user choice).
        
*   Add more advanced analytics:
    
    *   Content-type performance (timelapse vs static)
        
    *   Hashtag performance, not just frequency.
        
*   Add scheduling logic (just suggestions, not auto-post):
    
    *   “Best time windows” to post based on your past data.