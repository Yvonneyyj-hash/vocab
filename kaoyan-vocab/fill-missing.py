import json, requests, re, time

API_KEY = "sk-3daf8762609145dc88c11a3ed2553d89"
API_URL = "https://api.deepseek.com/v1/chat/completions"

with open('/Users/yaoyijia/kaoyan-vocab/missing-examples.json') as f:
    missing = json.load(f)
print(f"Processing {len(missing)} words")

results = {}
BATCH = 30
batches = [missing[i:i+BATCH] for i in range(0, len(missing), BATCH)]

for bi, batch in enumerate(batches):
    words = ", ".join(batch)
    try:
        resp = requests.post(API_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": f"For these English words, provide Chinese meaning, example sentence, Chinese translation, phrases and expressions. Return ONLY a JSON array:\n[{'{'}\"w\":\"word\",\"m\":\"Chinese meaning\",\"ex\":\"example sentence\",\"exc\":\"Chinese translation\",\"ph\":[\"phrase1 meaning1\"],\"xp\":[\"expression1 meaning1\"]{'}'}]\n\nWords: {words}"}],
                "temperature": 0.7, "max_tokens": 4000
            }, timeout=120)
        if resp.status_code == 200:
            content = resp.json()["choices"][0]["message"]["content"]
            m = re.search(r'\[[\s\S]*\]', content)
            if m:
                for r in json.loads(m.group()):
                    results[r["w"]] = r
        print(f"Batch {bi+1}/{len(batches)}: {len(batch)} words, total {len(results)}/{len(missing)}")
    except Exception as e:
        print(f"Batch {bi+1} error: {e}")
    time.sleep(0.5)

with open('/Users/yaoyijia/kaoyan-vocab/filled-examples.json', 'w') as f:
    json.dump(results, f, ensure_ascii=False)
print(f"\nDone: {len(results)} words enriched")
