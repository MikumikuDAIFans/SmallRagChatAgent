import os
import glob
import json
import pickle
import requests
import numpy as np
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SILICONFLOW_API_KEY")
BASE_URL = os.getenv("SILICONFLOW_BASE_URL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-0.6B")

if not API_KEY:
    raise ValueError("Please set SILICONFLOW_API_KEY in .env file")

class MarkdownSplitter:
    def __init__(self):
        pass

    def split_text(self, text: str) -> List[Dict[str, Any]]:
        lines = text.split('\n')
        chunks = []
        current_headers = {} # level -> title
        current_lines = []
        
        def flush_chunk():
            if not current_lines:
                return
            
            # Construct context from headers
            # Sort headers by level
            sorted_levels = sorted(current_headers.keys())
            header_path = " > ".join([current_headers[l] for l in sorted_levels])
            
            content = "\n".join(current_lines).strip()
            if not content:
                return

            full_text = f"[{header_path}]\n{content}" if header_path else content
            
            chunks.append({
                "text": full_text,
                "metadata": {
                    "headers": current_headers.copy(),
                    "content": content
                }
            })
            
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                # Detect header level
                level = 0
                for char in stripped:
                    if char == '#':
                        level += 1
                    else:
                        break
                
                # Check if it's a valid header (space after #)
                if level > 0 and len(stripped) > level and stripped[level] == ' ':
                    title = stripped[level:].strip()
                    
                    # Flush previous content
                    flush_chunk()
                    current_lines = []
                    
                    # Update headers: clear deeper levels
                    keys_to_remove = [k for k in current_headers if k >= level]
                    for k in keys_to_remove:
                        del current_headers[k]
                    
                    current_headers[level] = title
                    continue
            
            current_lines.append(line)
        
        # Flush last chunk
        flush_chunk()
        return chunks

def get_embedding(text: str) -> List[float]:
    url = f"{BASE_URL}/embeddings"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": EMBEDDING_MODEL,
        "input": text,
        "encoding_format": "float"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data['data'][0]['embedding']
    except Exception as e:
        print(f"Error getting embedding: {e}")
        # Return empty or raise, decided to raise to fail fast in dev
        raise e

def main():
    # Update data directory to point to 'doc' for input files
    data_dir = "doc" 
    # Output file remains in 'data' directory for the server to pick up
    output_dir = "data"
    output_file = os.path.join(output_dir, "knowledge.pkl")
    
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    splitter = MarkdownSplitter()
    all_knowledge = []
    
    # Process all .md files in the doc directory
    md_files = glob.glob(os.path.join(data_dir, "*.md"))
    print(f"Found {len(md_files)} markdown files.")
    
    for file_path in md_files:
        print(f"Processing {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        chunks = splitter.split_text(content)
        print(f"  Split into {len(chunks)} chunks.")
        
        for i, chunk in enumerate(chunks):
            print(f"    Embedding chunk {i+1}/{len(chunks)}...")
            vector = get_embedding(chunk['text'])
            
            all_knowledge.append({
                "text": chunk['text'],
                "vector": vector,
                "source": os.path.basename(file_path)
            })
            
    print(f"Total knowledge chunks: {len(all_knowledge)}")
    
    # Save to pickle
    with open(output_file, 'wb') as f:
        pickle.dump(all_knowledge, f)
    
    print(f"Saved knowledge base to {output_file}")

if __name__ == "__main__":
    main()
