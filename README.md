# BrickStein
BrickStein is an LLM that helps with math problems through visualizing concepts. It does so in many ways: 
- Answers any question the user asks
- Takes screenshots
-- Provides guidance with any problem circled or boxed in red.
- Creates videos that includes graphs, drawings, and audio to help explain a given problem.

## Installation 
1. Use the website to install LaTex on your computer https://www.tug.org/texlive/
2. Clone the repo and install the requirements
```python
install requirements.txt
```

3. Navigate to the .env file in the root directory of the project. Set all API_keys to your own keys
```python
TAVILY_API_KEY = "key"
OPENAI_API_KEY = "key"
GOOGLE_API_KEY = "key"
```

4. Go to the servers folder and use the command to run the program
```python
streamlit run chat_agent.py
```

## License
[MIT](https://choosealicense.com/licenses/mit/)