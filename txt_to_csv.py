import csv
import re
import sys
import os

def parse_txt_to_csv(txt_file_path, csv_file_path):
    rows = []
    
    # State variables
    state = {
        "Chapter": "",
        "ChapterTitle": "",
        "SubChapter": "",
        "SubChapterTitle": "",
        "Section": "",
        "SectionTitle": "",
        "Subsection": "",
        "Point": "",
        "Subpoint": ""
    }
    
    buffer = []
    
    # Flags to capture titles
    expect_chapter_title = False
    expect_subchapter_title = False
    expect_section_title = False
    
    # Regex patterns
    # Note: Section 3a, Section 3b exist.
    chapter_pattern = re.compile(r"^Chapter\s+(\d+)")
    subchapter_pattern = re.compile(r"^Sub-Chapter\s+(\d+)")
    section_pattern = re.compile(r"^Section\s+(\d+[a-z]*)")
    
    # Basic Law patterns
    roman_chapter_pattern = re.compile(r"^([IVXLCDM]+)\.\s+(.*)")
    article_pattern = re.compile(r"^Article\s+(\d+[a-z]*)")
    
    subsection_pattern = re.compile(r"^\((\d+)\)\s*(.*)")
    point_pattern = re.compile(r"^(\d+)\.\s+(.*)")
    subpoint_pattern = re.compile(r"^([a-z])\)\s+(.*)")
    
    def flush():
        text = " ".join(buffer).strip()
        if text:
            # Create a row with current state
            row = state.copy()
            row["Text"] = text
            rows.append(row)
        buffer.clear()

    with open(txt_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if "table of contents" in line.lower():
            continue
        if line.startswith("Stand: Die Übersetzung") or line.startswith("Version information:"):
            continue
        if line.startswith("Übersetzung durch") or line.startswith("Translated by"):
            continue
            
        # Check for hierarchy markers
        
        # Chapter (Standard)
        match = chapter_pattern.match(line)
        if match:
            flush()
            state["Chapter"] = match.group(1)
            state["ChapterTitle"] = ""
            state["SubChapter"] = ""
            state["SubChapterTitle"] = ""
            state["Section"] = ""
            state["SectionTitle"] = ""
            state["Subsection"] = ""
            state["Point"] = ""
            state["Subpoint"] = ""
            expect_chapter_title = True
            continue

        # Roman Chapter (Basic Law)
        match = roman_chapter_pattern.match(line)
        if match:
            # Ensure it's not a point like "1." (Roman I is I)
            # Basic Law uses I. II. III. 
            # Points use 1. 2. 3.
            # So [IVX...] should be safe if strict.
            flush()
            state["Chapter"] = match.group(1)
            state["ChapterTitle"] = match.group(2) # Title is on same line often: "I. Basic Rights"
            state["SubChapter"] = ""
            state["SubChapterTitle"] = ""
            state["Section"] = ""
            state["SectionTitle"] = ""
            state["Subsection"] = ""
            state["Point"] = ""
            state["Subpoint"] = ""
            expect_chapter_title = False # Title already captured
            continue
            
        # Sub-Chapter
        match = subchapter_pattern.match(line)
        if match:
            flush()
            state["SubChapter"] = match.group(1)
            state["SubChapterTitle"] = ""
            state["Section"] = ""
            state["SectionTitle"] = ""
            state["Subsection"] = ""
            state["Point"] = ""
            state["Subpoint"] = ""
            expect_subchapter_title = True
            continue
            
        # Section
        match = section_pattern.match(line)
        if match:
            flush()
            state["Section"] = match.group(1)
            state["SectionTitle"] = ""
            state["Subsection"] = ""
            state["Point"] = ""
            state["Subpoint"] = ""
            expect_section_title = True
            continue

        # Article (Basic Law - maps to Section)
        match = article_pattern.match(line)
        if match:
            flush()
            state["Section"] = match.group(1) # Map Article to Section column
            state["SectionTitle"] = ""
            state["Subsection"] = ""
            state["Point"] = ""
            state["Subpoint"] = ""
            expect_section_title = True
            continue
            
        # Capture Titles
        if expect_chapter_title:
            state["ChapterTitle"] = line
            expect_chapter_title = False
            continue
        if expect_subchapter_title:
            state["SubChapterTitle"] = line
            expect_subchapter_title = False
            continue
        if expect_section_title:
            # Basic Law titles are often [In brackets]
            if line.startswith("[") and line.endswith("]"):
                state["SectionTitle"] = line[1:-1]
            else:
                state["SectionTitle"] = line
            expect_section_title = False
            continue
            
        # Subsection (1) ...
        match = subsection_pattern.match(line)
        if match:
            flush()
            state["Subsection"] = f"({match.group(1)})"
            state["Point"] = ""
            state["Subpoint"] = ""
            buffer.append(match.group(2))
            continue
            
        # Point 1. ...
        match = point_pattern.match(line)
        if match:
            flush()
            state["Point"] = f"{match.group(1)}."
            state["Subpoint"] = ""
            buffer.append(match.group(2))
            continue
            
        # Subpoint a) ...
        match = subpoint_pattern.match(line)
        if match:
            flush()
            state["Subpoint"] = f"{match.group(1)})"
            buffer.append(match.group(2))
            continue
            
        # Normal text
        buffer.append(line)

    # Final flush
    flush()
    
    # Write CSV
    fieldnames = ["Chapter", "ChapterTitle", "SubChapter", "SubChapterTitle", 
                  "Section", "SectionTitle", "Subsection", "Point", "Subpoint", "Text"]
                  
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            
    print(f"Successfully converted {txt_file_path} to {csv_file_path}")

if __name__ == "__main__":
    resource_dir = "/Users/liudongxu/Desktop/studys/dignit_ai/rag_resource"
    
    # Iterate over all files in the directory
    for filename in os.listdir(resource_dir):
        if filename.endswith(".txt"):
            txt_path = os.path.join(resource_dir, filename)
            csv_filename = os.path.splitext(filename)[0] + ".csv"
            csv_path = os.path.join(resource_dir, csv_filename)
            
            print(f"Processing {filename}...")
            try:
                parse_txt_to_csv(txt_path, csv_path)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
