python
import os
import re
import json
import hashlib
import requests
import google.generativeai as genai

# Configuration Parameters
PZ_RAW_URL = "https://githubusercontent.com"
HASH_TRACKING_FILE = "last_known_hash.json"
OUTPUT_WIKI_FILE = "docs/weapons.md"
INDEX_FILE = "docs/index.md"

def fetch_pz_data() -> tuple[str, str]:
    """Fetches vanilla script parameters and computes cryptographic state verification."""
    print("Fetching raw Project Zomboid script definitions...")
    response = requests.get(PZ_RAW_URL)
    response.raise_for_status()
    raw_text = response.text
    
    # Compute SHA-256 to evaluate update velocity changes
    current_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()
    return raw_text, current_hash

def extract_sample_blocks(raw_text: str) -> str:
    """
    Extracts key weapon segments out of the multi-megabyte script file
    to prevent token limits on the free tier.
    """
    weapons_to_track = ["item Axe", "item Sledgehammer", "item Crowbar", "item Pistol"]
    extracted_segments = []
    
    for weapon in weapons_to_track:
        match = re.search(rf"({weapon}\s*\{{[^}}]*\}})", raw_text)
        if match:
            extracted_segments.append(match.group(1))
            
    return "\n\n".join(extracted_segments)

def check_for_updates(current_hash: str) -> bool:
    """Enforces Epistemic Ingestion Check; exits if file state hasn't moved."""
    if not os.path.exists(HASH_TRACKING_FILE):
        return True
    with open(HASH_TRACKING_FILE, 'r') as f:
        data = json.load(f)
        return data.get("hash") != current_hash

def generate_wiki_content(raw_code_snippet: str) -> str:
    """Orchestrates structured LLM synthesis utilizing zero-preamble configuration constraints."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Critical Security Violation: GEMINI_API_KEY environment variable is absent.")
        
    genai.configure(api_key=api_key)
    
    # Utilizing gemini-1.5-flash for optimized, rapid free-tier throughput
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    system_prompt = (
        "You are an expert Project Zomboid Wiki editor. Convert raw game engine script blocks (ZedScripts) "
        "into clear, professional, encyclopedic wiki pages using Markdown. "
        "Include tables displaying item parameters like Damage, Weight, and Type. "
        "Strictly avoid preambles, introductory small talk, or notes. Output the clean Markdown text directly."
    )
    
    prompt = f"System Rules:\n{system_prompt}\n\nTransform this raw Project Zomboid script data into the wiki article:\n{raw_code_snippet}"
    
    response = model.generate_content(prompt)
    return response.text

def main():
    # Initialize basic directory architecture requirements
    os.makedirs("docs", exist_ok=True)
    
    # Create simple home index file if absent
    if not os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "w") as f:
            f.write("# Project Zomboid AutoWiki\nWelcome to an automated wiki dynamically parsed from live code repositories.")

    try:
        raw_text, current_hash = fetch_pz_data()
        
        if not check_for_updates(current_hash):
            print("Zero operational variance detected. System state matches current wiki build. Terminating run.")
            return
            
        print("Delta update found! Triggering synthesis engine pipeline...")
        targeted_code = extract_sample_blocks(raw_text)
        wiki_markdown = generate_wiki_content(targeted_code)
        
        # Write output markdown documentation
        with open(OUTPUT_WIKI_FILE, "w", encoding="utf-8") as f:
            f.write(wiki_markdown)
            
        # Serialize the validated tracking state
        with open(HASH_TRACKING_FILE, "w") as f:
            json.dump({"hash": current_hash}, f)
            
        print("AutoWiki successfully updated and compiled.")
        
    except Exception as e:
        print(f"Pipeline Process Interrupted: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
