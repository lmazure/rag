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
