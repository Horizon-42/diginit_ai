import pandas as pd
import os
import glob

def combine_csvs(resource_dir, output_file):
    all_files = glob.glob(os.path.join(resource_dir, "*.csv"))
    
    combined_df = pd.DataFrame()
    
    for filename in all_files:
        if filename.endswith("urls.csv") or filename.endswith("combined_laws.csv"):
            continue
            
        print(f"Processing {filename}...")
        try:
            df = pd.read_csv(filename)
            
            # Add law_name column derived from filename
            law_name = os.path.splitext(os.path.basename(filename))[0]
            # Clean up law name (replace underscores with spaces, title case)
            # law_name_clean = law_name.replace("_", " ").title()
            # User asked for "law_name of law_title", let's keep the filename as ID-like law_name
            df['law_name'] = law_name
            
            combined_df = pd.concat([combined_df, df], ignore_index=True)
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            
    if combined_df.empty:
        print("No data combined.")
        return

    # "Fill the empty index with simple math"
    # We interpret this as filling missing hierarchical values with 0
    # Columns to fill: Chapter, SubChapter, Section, Subsection, Point, Subpoint
    # We also need to handle that some might be strings like "3a". 
    # So we fill NaNs with "0".
    
    fill_cols = ["Chapter", "SubChapter", "Section", "Subsection", "Point", "Subpoint"]
    for col in fill_cols:
        if col in combined_df.columns:
            combined_df[col] = combined_df[col].fillna("0")
            combined_df[col] = combined_df[col].replace("", "0")

    # Also fill Titles with empty string if NaN
    title_cols = ["ChapterTitle", "SubChapterTitle", "SectionTitle"]
    for col in title_cols:
        if col in combined_df.columns:
            combined_df[col] = combined_df[col].fillna("")

    # Add a global index column (simple math: 0, 1, 2...)
    combined_df.reset_index(drop=True, inplace=True)
    combined_df['global_index'] = combined_df.index

    # Save
    combined_df.to_csv(output_file, index=False)
    print(f"Successfully created {output_file} with {len(combined_df)} rows.")

if __name__ == "__main__":
    resource_dir = "/Users/liudongxu/Desktop/studys/dignit_ai/rag_resource"
    output_file = os.path.join(resource_dir, "combined_laws.csv")
    combine_csvs(resource_dir, output_file)
