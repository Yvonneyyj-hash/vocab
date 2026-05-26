import pdfplumber, json, re

pdf = pdfplumber.open('/Users/yaoyijia/Desktop/2027考研英语红宝书（乱序版）英文词表.pdf')
all_words = []
seen = set()

for page_num in range(len(pdf.pages)):
    text = pdf.pages[page_num].extract_text() or ''
    # Match any number followed by a word (anywhere in text, not just line start)
    for m in re.finditer(r'(?<!\d)(\d{1,4})\s+([a-zA-Z]{2,}(?:\s*/\s*[a-zA-Z]+)?)\b', text):
        num = int(m.group(1))
        w = m.group(2).strip().lower()
        # Filter out non-words
        if w in ('word', 'meaning', 'o', 'a', 'i'):
            continue
        if w and w not in seen and len(w) > 1:
            seen.add(w)
            all_words.append(w)

print(f'Extracted {len(all_words)} unique words')
# Save
with open('/Users/yaoyijia/kaoyan-vocab/word-list.json', 'w') as f:
    json.dump(all_words, f, ensure_ascii=False)
print(f'Saved to word-list.json')
print(f'First 10: {all_words[:10]}')
print(f'Last 10: {all_words[-10:]}')
