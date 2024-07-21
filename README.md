This is a playground to discover RAG.  
I started from a code sample copied from https://medium.com/rahasak/build-rag-application-using-a-llm-running-on-local-computer-with-gpt4all-and-langchain-13b4b8851db8 and I will play with it to understand this stuff.

```bash
python -m venv .venv
source .venv/scripts/activate
pip install -r requirements.txt
export INIT_INDEX=true
python api.py
```
there is currently a bug, the model is not found  
the workaround is to run
```bash
python gpt4all_example.py
```

in another window
```bash
curl -i -XPOST "http://localhost:7654/api/question" \
--header "Content-Type: application/json" \
--data '
{
  "question": "How open5gs work?",
  "user_id": "zio"
}
'
```
