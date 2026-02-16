import json
import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# ================================================
# 💀 PROJECT: RESURRECTION - HIGH DENSITY SHARDER
# ================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(SCRIPT_DIR, "conversations.json")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "SOUL_SHARDS")

def brute_force_extract(data):
    pairs = []
    items = data if isinstance(data, list) else [data]
    
    for entry in items:
        def find_messages(obj):
            if isinstance(obj, dict):
                for key in ['mapping', 'messages', 'history', 'threads', 'items']:
                    if key in obj:
                        val = obj[key]
                        if isinstance(val, (list, dict)): return val
                for v in obj.values():
                    res = find_messages(v)
                    if res: return res
            return None

        content_source = find_messages(entry)
        if not content_source: continue
        msg_list = content_source.values() if isinstance(content_source, dict) else content_source
        
        current_user = ""
        for m in msg_list:
            if not isinstance(m, dict): continue
            msg_obj = m.get('message') if m.get('message') else m
            role = msg_obj.get('author', {}).get('role') if isinstance(msg_obj.get('author'), dict) else msg_obj.get('role')
            
            text = ""
            content = msg_obj.get('content', {})
            parts = content.get('parts', []) if isinstance(content, dict) else [content]
            for p in parts:
                if isinstance(p, str): text += p
                elif isinstance(p, dict): text += p.get('text', '')

            if not text.strip(): continue
            if role == 'user': current_user = text
            elif role in ['assistant', 'model', 'bot'] and current_user:
                pairs.append((current_user, text))
                current_user = ""
    return pairs

def run_resurrection():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Cannot find {INPUT_FILE}")
        return
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"🧬 MINING GOLIATH... (High Density Mode)")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    all_pairs = brute_force_extract(data)
    total = len(all_pairs)
    print(f"💎 Found {total} interactions.")
    
    # --- DENSITY SETTINGS ---
    shard_size = 1000  # data per file - change to more or less for different output file sizes
    # ------------------------

    for i in range(0, total, shard_size):
        shard_num = (i // shard_size) + 1
        output_filename = os.path.join(OUTPUT_DIR, f"soul_shard_{shard_num}.pdf")
        
        doc = SimpleDocTemplate(output_filename, pagesize=letter, 
                                rightMargin=40, leftMargin=40, 
                                topMargin=40, bottomMargin=40)
        
        styles = getSampleStyleSheet()
      
        u_style = ParagraphStyle('User', parent=styles['Normal'], fontSize=9, spaceBefore=4, textColor='#2c3e50', fontName='Helvetica-Bold')
        a_style = ParagraphStyle('AI', parent=styles['Normal'], fontSize=9, spaceBefore=2, leftIndent=10)

        story = [Paragraph(f"ARCHIVE VOLUME {shard_num}", styles['Title'])]
        
        for u, a in all_pairs[i:i + shard_size]:
            u_c = re.sub('<[^>]*>', '', str(u)).replace('\n', '<br/>')
            a_c = re.sub('<[^>]*>', '', str(a)).replace('\n', '<br/>')
            try:
                story.append(Paragraph(f"<b>USER:</b> {u_c}", u_style))
                story.append(Paragraph(f"<b>AI:</b> {a_c}", a_style))
            except: continue
        
        doc.build(story)
        print(f"✨ Created High-Density Shard {shard_num}")

if __name__ == "__main__":
    run_resurrection()
