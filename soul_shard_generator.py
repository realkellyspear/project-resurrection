import json
import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ==========================================
# 💀 PROJECT: RESURRECTION - THE UNIVERSAL SHARDER
# ==========================================

INPUT_FILE = "conversations.json" #<== Add your path here!
OUTPUT_DIR = "SOUL_SHARDS"

# THE LOBOTOMY FILTER
AI_BLACKLIST = [
    "As an AI language model", "I cannot fulfill", "against my content policy",
    "I am unable to", "ethical guidelines", "AI assistant", "how can I help"
]

def generate_shards():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: {INPUT_FILE} not found. Ensure your export is in this folder.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_pairs = []
    print(f"🧼 Filtering {len(data)} conversations...")

    for entry in data:
        mapping = entry.get('mapping', {})
        # ChatGPT structure extraction
        messages = [
            (m.get('message', {}).get('author', {}).get('role'), 
             m.get('message', {}).get('content', {}).get('parts', [""])[0])
            for m in mapping.values() if m.get('message')
        ]
        
        # Build pairs from the conversation tree
        for i in range(len(messages)-1):
            if messages[i][0] == 'user' and messages[i+1][0] == 'assistant':
                user_text, ai_text = messages[i][1], messages[i+1][1]
                if not any(v.lower() in ai_text.lower() for v in AI_BLACKLIST):
                    all_pairs.append((user_text, ai_text))

    # Sharding into 250-pair volumes
    shard_size = 250
    for i in range(0, len(all_pairs), shard_size):
        shard_num = (i // shard_size) + 1
        shard_data = all_pairs[i:i + shard_size]
        
        doc = SimpleDocTemplate(f"{OUTPUT_DIR}/shard_{shard_num}.pdf", pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph(f"<b>SHARD {shard_num}</b>", styles['Title']), Spacer(1, 12)]
        
        for u, a in shard_data:
            u_clean = re.sub('<[^>]*>', '', u).replace('\n', '<br/>')
            a_clean = re.sub('<[^>]*>', '', a).replace('\n', '<br/>')
            story.append(Paragraph(f"<b>USER:</b> {u_clean}", styles['Normal']))
            story.append(Paragraph(f"<b>AI:</b> {a_clean}", styles['Italic']))
            story.append(Spacer(1, 6))
        
        doc.build(story)
        print(f"✨ Shard {shard_num} complete.")

if __name__ == "__main__":
    generate_shards()
