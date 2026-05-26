import json, csv, re

# Load enriched data
with open('/Users/yaoyijia/kaoyan-vocab/deepseek-progress.json') as f:
    enriched = json.load(f)

# Load ECDICT for fallback
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

# Load full word list
with open('/Users/yaoyijia/kaoyan-vocab/word-list.json') as f:
    all_words = json.load(f)

# Build entries
entries = []
for w in all_words:
    w_lower = w.lower()
    info = enriched.get(w_lower)
    ec = ecdict.get(w_lower, {})

    if info:
        p = info.get('p', ec.get('p', '')).replace('\\','\\\\').replace('"','\\"')[:100]
        pos = info.get('pos', ec.get('pos', '')).replace('\\','\\\\').replace('"','\\"')[:50]
        m = info.get('m', ec.get('t', '')).replace('\\','\\\\').replace('"','\\"')[:200]
        ex = info.get('ex', '').replace('\\','\\\\').replace('"','\\"')[:300]
        exc = info.get('exc', '').replace('\\','\\\\').replace('"','\\"')[:300]
        ph = json.dumps(info.get('ph', [])[:3], ensure_ascii=False)
        xp = json.dumps(info.get('xp', [])[:2], ensure_ascii=False)
    else:
        # Fallback from ECDICT
        p = ec.get('p', '').replace('\\','\\\\').replace('"','\\"')[:100]
        pos = ec.get('pos', '').replace('\\','\\\\').replace('"','\\"')[:50]
        m = ec.get('t', '').replace('\\','\\\\').replace('"','\\"')[:200]
        ex = f'{w} is a key vocabulary word for the exam.'
        exc = f'{w} 是考试的关键词汇。'
        ph = '[]'
        xp = '[]'

    entries.append(f'{{w:"{w}",p:"{p}",pos:"{pos}",m:"{m}",ex:"{ex}",exc:"{exc}",ph:{ph},xp:{xp},mu:[]}}')

# Build WORD_BANK
new_bank = 'const WORD_BANK = [\n  ' + ',\n  '.join(entries) + '\n];'

# Update index.html
with open('/Users/yaoyijia/kaoyan-vocab/index.html', 'r') as f:
    html = f.read()

bank_start = html.find('const WORD_BANK = [')
bank_end = html.find('];\n', bank_start) + 2

html = html[:bank_start] + new_bank + html[bank_end:]
with open('/Users/yaoyijia/kaoyan-vocab/index.html', 'w') as f:
    f.write(html)

print(f'Written {len(entries)} words to index.html')
print(f'  DeepSeek enriched: {len(enriched)}')
print(f'  ECDICT fallback: {len(entries) - len(enriched)}')
