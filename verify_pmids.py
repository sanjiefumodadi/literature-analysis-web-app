import json
from Bio import Entrez

# 设置Entrez邮箱（必须）
Entrez.email = "example@example.com"
# 设置超时时间
Entrez.timeout = 10

# 读取论文数据
def load_papers():
    citation_info_dir = r"d:\新建文件夹 (2)\文献资料\citation_info"
    all_citations_file = os.path.join(citation_info_dir, "all_citations.json")
    
    if os.path.exists(all_citations_file):
        with open(all_citations_file, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        return papers
    return []

# 验证PMID是否真实存在
def verify_pmid(pmid):
    try:
        handle = Entrez.esummary(db="pubmed", id=pmid)
        record = Entrez.read(handle)
        handle.close()
        
        if record:
            return True
    except Exception as e:
        print(f"Error verifying PMID {pmid}: {e}")
    return False

# 主函数
def main():
    papers = load_papers()
    print(f"共加载 {len(papers)} 篇论文")
    
    valid_pmids = []
    invalid_pmids = []
    
    for paper in papers:
        pmid = paper['PMID']
        print(f"验证 PMID {pmid}...")
        if verify_pmid(pmid):
            valid_pmids.append(pmid)
            print(f"  ✓ PMID {pmid} 有效")
        else:
            invalid_pmids.append(pmid)
            print(f"  ✗ PMID {pmid} 无效")
    
    print(f"\n验证结果:")
    print(f"有效 PMID: {len(valid_pmids)}")
    print(f"无效 PMID: {len(invalid_pmids)}")
    
    if invalid_pmids:
        print(f"无效 PMID 列表: {invalid_pmids}")

if __name__ == "__main__":
    import os
    main()