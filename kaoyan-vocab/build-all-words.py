import csv, json, re, html as htmllib

# Load word list
with open('/Users/yaoyijia/kaoyan-vocab/word-list.json') as f:
    word_list = json.load(f)
print(f'Loaded {len(word_list)} words')

# Build dictionary index from ECDICT
ecdict = {}
with open('/tmp/ecdict.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    # columns: word,phonetic,definition,translation,pos,collins,oxford,tag,bnc,frq,exchange,detail,audio
    for row in reader:
        if len(row) >= 4:
            word = row[0].strip().lower()
            phonetic = row[1].strip() if len(row) > 1 else ''
            definition = row[2].strip() if len(row) > 2 else ''
            translation = row[3].strip() if len(row) > 3 else ''
            pos = row[4].strip() if len(row) > 4 else ''
            if word and (translation or definition):
                ecdict[word] = {
                    'p': phonetic,
                    'd': definition,
                    't': translation,
                    'pos': pos
                }

print(f'Dictionary loaded: {len(ecdict)} entries')

# Match words
matched = 0
unmatched = []
entries = []

for w in word_list:
    w_lower = w.lower()
    info = ecdict.get(w_lower)
    if info:
        matched += 1
        phonetic = info['p'] if info['p'] else ''
        meaning = info['t'] if info['t'] else info['d']
        pos = info['pos'] if info['pos'] else ''
        if not phonetic:
            phonetic = ''
        if not meaning:
            meaning = ''
        # Clean up phonetic
        phonetic = phonetic.replace('&nbsp;',' ').strip()
        meaning = meaning.replace('&nbsp;',' ').replace('\\n','；').strip()
        # Escape for JS string
        meaning_js = meaning.replace('\\','\\\\').replace('"','\\"').replace('\n','；')
        phonetic_js = phonetic.replace('\\','\\\\').replace('"','\\"')
        # Build a simple example
        ex = f'{w} is an important word to master for the exam.'
        exc = f'掌握{w}这个词对考试很重要。'
        entries.append(f'{{w:"{w}",p:"{phonetic_js}",pos:"{pos}",m:"{meaning_js[:200]}",ex:"{ex}",exc:"{exc}",ph:[],xp:[],mu:[]}}')
    else:
        unmatched.append(w)

print(f'Matched: {matched}, Unmatched: {len(unmatched)}')

# Build new WORD_BANK
new_bank = 'const WORD_BANK = [\n  ' + ',\n  '.join(entries) + '\n];'

# Replace in index.html
with open('/Users/yaoyijia/kaoyan-vocab/index.html', 'r') as f:
    html = f.read()

bank_start = html.find('const WORD_BANK = [')
bank_end = html.find('];\n', bank_start) + 2

if bank_start > 0 and bank_end > bank_start:
    html = html[:bank_start] + new_bank + html[bank_end:]
    with open('/Users/yaoyijia/kaoyan-vocab/index.html', 'w') as f:
        f.write(html)
    print(f'index.html updated with {len(entries)} words')
else:
    print('Could not find WORD_BANK')

# Show unmatched words
if unmatched:
    print(f'Unmatched words (first 30): {unmatched[:30]}')
