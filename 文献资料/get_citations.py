import os
import json
from Bio import Entrez

# 设置Entrez邮箱（必须）
Entrez.email = "example@example.com"

# 定义PMID列表
pmids = [
    "39123457", "37894522", "38765433", "37654322"
]

# 定义输出文件夹
output_dir = "d:\\新建文件夹 (2)\\文献资料\\citation_info"

# 确保输出文件夹存在
os.makedirs(output_dir, exist_ok=True)

# 函数：获取文献信息
def get_citation_info(pmid):
    try:
        # 使用Entrez.esummary获取文献摘要信息
        handle = Entrez.esummary(db="pubmed", id=pmid)
        record = Entrez.read(handle)
        handle.close()
        
        if record:
            # 提取关键信息
            article = record[0]
            citation = {
                "PMID": pmid,
                "Title": article.get("Title", ""),
                "Journal": article.get("FullJournalName", ""),
                "Year": article.get("PubDate", "").split()[0] if article.get("PubDate") else "",
                "Authors": article.get("AuthorList", []),
                "DOI": article.get("DOI", ""),
                "Abstract": article.get("Abstract", "")
            }
            return citation
        return None
    except Exception as e:
        print(f"Error getting citation for PMID {pmid}: {e}")
        return None

# 函数：保存citation信息到文件
def save_citation(citation, output_dir):
    if citation:
        pmid = citation.get("PMID")
        filename = os.path.join(output_dir, f"citation_{pmid}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(citation, f, ensure_ascii=False, indent=2)
        print(f"Saved citation for PMID {pmid}")

# 主函数：处理所有PMID
def main():
    print("Starting to fetch citations...")
    
    # 用于存储所有citation信息的列表
    all_citations = []
    
    # 处理每个PMID
    for i, pmid in enumerate(pmids, 1):
        print(f"Processing PMID {pmid} ({i}/{len(pmids)})...")
        try:
            citation = get_citation_info(pmid)
            if citation:
                save_citation(citation, output_dir)
                all_citations.append(citation)
            else:
                print(f"No citation found for PMID {pmid}")
        except Exception as e:
            print(f"Error processing PMID {pmid}: {e}")
            continue
    
    # 保存所有citation到一个文件
    all_citations_file = os.path.join(output_dir, "all_citations.json")
    with open(all_citations_file, 'w', encoding='utf-8') as f:
        json.dump(all_citations, f, ensure_ascii=False, indent=2)
    
    print(f"\nAll citations fetched and saved. Total: {len(all_citations)}")
    print(f"All citations summary saved to: {all_citations_file}")

if __name__ == "__main__":
    main()