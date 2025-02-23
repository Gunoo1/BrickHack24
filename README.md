# BrickStein
BrickStein is an LLM that helps with math problems through visualizing concepts. It does so in many ways: 
- Answers any question the user asks
- Takes screenshots
- Creates videos that includes graphs, drawings, and audio to help explain a given problem.

# Instructions for running projects:
- install latex https://www.tug.org/texlive/
- install requirements.txt
- in .env file in root directory of project:
   - TAVILY_API_KEY = "key"
   - OPENAI_API_KEY = "key"
   - GOOGLE_API_KEY = "key" 
- cd to servers folder
- run streamlit run chat_agent.py
