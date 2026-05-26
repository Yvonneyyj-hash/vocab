import json, time, requests, csv, re, os

API_KEY = "sk-3daf8762609145dc88c11a3ed2553d89"
API_URL = "https://api.deepseek.com/v1/chat/completions"

# Load word list
with open('/Users/yaoyijia/kaoyan-vocab/word-list.json') as f:
    all_words = json.load(f)

# Load ECDICT for existing phonetics/meanings
ecdict = {}
with open('/tmp/ecdict.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) >= 4:
            w = row[0].strip().lower()
            ecdict[w] = {
                'p': row[1].strip() if len(row) > 1 else '',
                't': row[3].strip() if len(row) > 3 else '',
                'pos': row[4].strip() if len(row) > 4 else ''
            }

# Check progress
PROGRESS_FILE = '/Users/yaoyijia/kaoyan-vocab/deepseek-progress.json'
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE) as f:
        enriched = json.load(f)
    print(f"Resuming from progress: {len(enriched)} words done")
else:
    enriched = {}

BATCH_SIZE = 25
words_to_process = [w for w in all_words if w not in enriched]
batches = [words_to_process[i:i+BATCH_SIZE] for i in range(0, len(words_to_process), BATCH_SIZE)]
print(f"Total: {len(all_words)} words, {len(enriched)} done, {len(words_to_process)} remaining, {len(batches)} batches")

def build_prompt(words_batch):
    word_list = ", ".join(words_batch)
    return f"""For each of the following English words, provide:
1. Chinese meaning (concise, suitable for Chinese graduate exam 考研)
2. One natural English example sentence (academic/professional tone)
3. Chinese translation of the example
4. 1-3 common phrases/collocations (English + Chinese)
5. 0-2 idiomatic expressions (English + Chinese)

Return ONLY valid JSON array. Format:
[{{"w":"word","m":"中文释义","ex":"English example","exc":"Chinese translation of example","ph":["phrase1 中文1","phrase2 中文2"],"xp":["expression1 中文1"]}}]

Words: {word_list}"""

processed = 0
for bi, batch in enumerate(batches):
    try:
        resp = requests.post(API_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": build_prompt(batch)}],
                "temperature": 0.7,
                "max_tokens": 4000
            },
            timeout=120
        )
        if resp.status_code != 200:
            print(f"Batch {bi+1}/{len(batches)} error {resp.status_code}: {resp.text[:200]}")
            time.sleep(5)
            continue

        content = resp.json()["choices"][0]["message"]["content"]
        # Extract JSON from response
        json_match = re.search(r'\[[\s\S]*\]', content)
        if not json_match:
            print(f"Batch {bi+1}: No JSON found in response")
            continue

        results = json.loads(json_match.group())
        for r in results:
            w = r["w"].lower()
            info = ecdict.get(w, {})
            enriched[w] = {
                "p": info.get("p", ""),
                "pos": r.get("pos", info.get("pos", "")),
                "m": r.get("m", info.get("t", "")),
                "ex": r.get("ex", ""),
                "exc": r.get("exc", ""),
                "ph": r.get("ph", []),
                "xp": r.get("xp", [])
            }

        processed += len(results)
        print(f"Batch {bi+1}/{len(batches)}: {len(results)} words, total {len(enriched)}/{len(all_words)}")

        # Save progress every 5 batches
        if (bi + 1) % 5 == 0:
            with open(PROGRESS_FILE, 'w') as f:
                json.dump(enriched, f, ensure_ascii=False)
            print(f"  Progress saved")

        time.sleep(1)  # Rate limit buffer

    except Exception as e:
        print(f"Batch {bi+1} failed: {e}")
        time.sleep(5)

# Final save
with open(PROGRESS_FILE, 'w') as f:
    json.dump(enriched, f, ensure_ascii=False)
print(f"\nDone! {len(enriched)} words enriched. Saved to {PROGRESS_FILE}")
