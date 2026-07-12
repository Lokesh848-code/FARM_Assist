import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class FarmingRetriever:
    def __init__(self, filepath="master_farming_dataset.txt"):
        self.filepath = filepath
        self.chunks = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self.load_and_process()

    def load_and_process(self):
        if not os.path.exists(self.filepath):
            self.chunks = ["No agricultural knowledge base loaded. Please upload master_farming_dataset.txt."]
            return

        with open(self.filepath, "r", encoding="utf-8") as f:
            content = f.read()

        is_large_dataset = "MASTER FARMING ADVISORY DATASET" in content or "SECTION A:" in content

        if not is_large_dataset:
            self.parse_simple_dataset(content)
        else:
            self.parse_large_dataset(content)

        if not self.chunks:
            self.chunks = ["No valid chunks parsed from dataset. Please check format."]
            return

        self.vectorizer = TfidfVectorizer(stop_words='english', token_pattern=r'(?u)\b\w+\b')
        try:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.chunks)
        except ValueError:
            self.vectorizer = TfidfVectorizer(token_pattern=r'(?u)\b\w+\b')
            self.tfidf_matrix = self.vectorizer.fit_transform(self.chunks)

    def parse_simple_dataset(self, content):
        current_crop = "General Agriculture"
        current_section = "General Information"
        current_content_lines = []
        
        lines = content.splitlines()
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            crop_match = re.search(r'CROP:\s*(.*)', stripped, re.IGNORECASE)
            section_match = re.search(r'SECTION:\s*(.*)', stripped, re.IGNORECASE)
            
            if crop_match:
                if current_content_lines:
                    chunk_text = f"Crop: {current_crop}\nSection: {current_section}\nContent: " + " ".join(current_content_lines)
                    self.chunks.append(chunk_text)
                    current_content_lines = []
                current_crop = crop_match.group(1).strip()
                current_section = "General Info"
            elif section_match:
                if current_content_lines:
                    chunk_text = f"Crop: {current_crop}\nSection: {current_section}\nContent: " + " ".join(current_content_lines)
                    self.chunks.append(chunk_text)
                    current_content_lines = []
                current_section = section_match.group(1).strip()
            elif stripped.startswith("===") or stripped.startswith("---"):
                continue
            else:
                current_content_lines.append(stripped)
                
        if current_content_lines:
            chunk_text = f"Crop: {current_crop}\nSection: {current_section}\nContent: " + " ".join(current_content_lines)
            self.chunks.append(chunk_text)

    def parse_large_dataset(self, content):
        section_matches = list(re.finditer(r'SECTION\s+([A-Z]):\s*(.*?)\n={2,}', content, re.IGNORECASE))
        
        if not section_matches:
            self.chunks = [p.strip() for p in content.split("\n\n") if p.strip()]
            return
            
        for i in range(len(section_matches)):
            start_idx = section_matches[i].end()
            end_idx = section_matches[i+1].start() if i + 1 < len(section_matches) else len(content)
            
            section_letter = section_matches[i].group(1).upper()
            section_title = section_matches[i].group(2).strip()
            section_text = content[start_idx:end_idx]
            
            if section_letter == 'A':
                crop_matches = list(re.finditer(r'---\s*(.*?):\s*100 recorded soil/climate samples\s*---', section_text))
                for j in range(len(crop_matches)):
                    c_start = crop_matches[j].end()
                    c_end = crop_matches[j+1].start() if j + 1 < len(crop_matches) else len(section_text)
                    crop_name = crop_matches[j].group(1).strip()
                    crop_samples = section_text[c_start:c_end].strip().splitlines()
                    
                    group_size = 10
                    for k in range(0, len(crop_samples), group_size):
                        group = crop_samples[k:k+group_size]
                        cleaned_group = []
                        for line in group:
                            # 1. Clean CropName record prefix
                            cleaned_line = re.sub(rf'^{re.escape(crop_name)}\s+record', 'Record', line, flags=re.IGNORECASE)
                            # 2. Clean 'typical range for CropName' -> 'typical range'
                            cleaned_line = re.sub(rf'typical\s+range\s+for\s+{re.escape(crop_name)}', 'typical range', cleaned_line, flags=re.IGNORECASE)
                            # 3. Clean 'for CropName' at the end of the sentence
                            cleaned_line = re.sub(rf'typical\s+range\s+for\s+the\s+{re.escape(crop_name)}', 'typical range', cleaned_line, flags=re.IGNORECASE)
                            cleaned_line = re.sub(rf'for\s+{re.escape(crop_name)}\b', '', cleaned_line, flags=re.IGNORECASE)
                            cleaned_group.append(cleaned_line)
                        group_text = "\n".join(cleaned_group)
                        self.chunks.append(f"Section: {section_title}\nCrop: {crop_name}\nSoil & Climate Samples:\n{group_text}")
                        
            elif section_letter in ['B', 'C']:
                crop_matches = list(re.finditer(r'---\s*(.*?)\s*---', section_text))
                for j in range(len(crop_matches)):
                    c_start = crop_matches[j].end()
                    c_end = crop_matches[j+1].start() if j + 1 < len(crop_matches) else len(section_text)
                    crop_title = crop_matches[j].group(1).strip()
                    crop_content = section_text[c_start:c_end].strip()
                    self.chunks.append(f"Section: {section_title}\nCrop/Subject: {crop_title}\nContent:\n{crop_content}")
                    
            elif section_letter in ['E', 'F', 'L', 'G']:
                paragraphs = section_text.split("\n\n")
                for p in paragraphs:
                    p_clean = p.strip()
                    if p_clean and len(p_clean) > 30:
                        self.chunks.append(f"Section: {section_title}\nContent:\n{p_clean}")
                        
            elif section_letter == 'H':
                faq_matches = list(re.finditer(r'Q:\s*(.*?)\n', section_text))
                for j in range(len(faq_matches)):
                    f_start = faq_matches[j].start()
                    f_end = faq_matches[j+1].start() if j + 1 < len(faq_matches) else len(section_text)
                    faq_content = section_text[f_start:f_end].strip()
                    self.chunks.append(f"Section: {section_title}\n{faq_content}")
                    
            elif section_letter == 'K':
                lines = section_text.strip().splitlines()
                for line in lines:
                    l_clean = line.strip()
                    if l_clean and ":" in l_clean:
                        self.chunks.append(f"Section: {section_title}\nContent:\n{l_clean}")
                        
            else:
                sub_sections = re.split(r'\n---\n', section_text)
                for sub in sub_sections:
                    sub_clean = sub.strip()
                    if sub_clean and len(sub_clean) > 30:
                        self.chunks.append(f"Section: {section_title}\nContent:\n{sub_clean}")

    def retrieve(self, query, top_k=3):
        if not self.vectorizer or not self.chunks:
            return []
        
        try:
            query_vec = self.vectorizer.transform([query])
            similarities = (self.tfidf_matrix * query_vec.T).toarray().flatten()
        except Exception:
            similarities = np.zeros(len(self.chunks))
            query_words = set(query.lower().split())
            for i, chunk in enumerate(self.chunks):
                chunk_words = set(chunk.lower().split())
                overlap = len(query_words.intersection(chunk_words))
                similarities[i] = overlap

        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = similarities[idx]
            results.append({
                "chunk": self.chunks[idx],
                "score": float(score)
            })
        return results
