import json
import time
from Bio import Entrez
import datetime

# 设置Entrez邮箱（必须）
Entrez.email = "example@example.com"
# 设置超时时间
Entrez.timeout = 10

# 计算当前年份，用于过滤近两年的文献
current_year = datetime.datetime.now().year

# 搜索相关论文
def search_papers(query, max_results=20):
    papers = []
    try:
        # 使用Entrez.esearch搜索论文
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()
        
        if 'IdList' in record:
            pmids = record['IdList']
            print(f"找到 {len(pmids)} 篇相关论文")
            
            # 获取每篇论文的详细信息
            for i, pmid in enumerate(pmids):
                print(f"获取论文 {i+1}/{len(pmids)} 的详细信息 (PMID: {pmid})...")
                try:
                    paper_info = get_paper_info(pmid)
                    if paper_info:
                        # 过滤近两年的文献
                        if paper_info.get('Year'):
                            try:
                                year = int(paper_info['Year'])
                                if year < current_year - 2:
                                    papers.append(paper_info)
                                    print(f"  OK 成功获取论文信息: {paper_info['Title'][:50]}...")
                                else:
                                    print(f"  SKIP 跳过近两年的文献: {paper_info['Title'][:50]}...")
                            except ValueError:
                                # 年份格式不正确，跳过
                                print(f"  SKIP 年份格式不正确: {paper_info['Year']}")
                        else:
                            print(f"  SKIP 缺少年份信息，跳过")
                    else:
                        print(f"  SKIP 无法获取论文信息")
                except Exception as e:
                    print(f"  ERROR 获取论文信息时出错: {e}")
                time.sleep(0.1)  # 添加延迟，避免API限流
        else:
            print("未找到论文")
    except Exception as e:
        print(f"搜索论文时出错: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"成功获取 {len(papers)} 篇非近两年论文的详细信息")
    return papers

# 获取论文详细信息
def get_paper_info(pmid):
    try:
        # 使用Entrez.esummary获取论文信息
        handle = Entrez.esummary(db="pubmed", id=pmid)
        record = Entrez.read(handle)
        handle.close()
        
        if record and len(record) > 0:
            article = record[0]
            paper_info = {
                "PMID": pmid,
                "Title": article.get("Title", ""),
                "Journal": article.get("FullJournalName", ""),
                "Year": article.get("PubDate", "").split()[0] if article.get("PubDate") else "",
            }
            return paper_info
        else:
            print(f"未找到论文信息 (PMID {pmid})")
    except Exception as e:
        print(f"获取论文信息时出错 (PMID {pmid}): {e}")
    
    return None

# 获取论文的引用关系（该论文引用的其他论文）
def get_references(pmid, max_refs=5):
    references = []
    try:
        # 使用Entrez.elink获取引用关系
        handle = Entrez.elink(dbfrom="pubmed", db="pubmed", id=pmid, linkname="pubmed_pubmed_refs")
        record = Entrez.read(handle)
        handle.close()
        
        if record:
            for linkset in record:
                if 'LinkSetDb' in linkset:
                    for linksetdb in linkset['LinkSetDb']:
                        if linksetdb.get('LinkName') == 'pubmed_pubmed_refs':
                            if 'Link' in linksetdb:
                                for link in linksetdb['Link'][:max_refs]:
                                    if 'Id' in link:
                                        references.append(link['Id'])
    except Exception as e:
        print(f"获取引用关系时出错 (PMID {pmid}): {e}")
    
    return references

# 获取论文的被引用关系（引用该论文的其他论文）
def get_cited_by(pmid, max_cited=5):
    cited_by = []
    try:
        # 使用Entrez.elink获取被引用关系
        handle = Entrez.elink(dbfrom="pubmed", db="pubmed", id=pmid, linkname="pubmed_pubmed_citedin")
        record = Entrez.read(handle)
        handle.close()
        
        if record:
            for linkset in record:
                if 'LinkSetDb' in linkset:
                    for linksetdb in linkset['LinkSetDb']:
                        if linksetdb.get('LinkName') == 'pubmed_pubmed_citedin':
                            if 'Link' in linksetdb:
                                for link in linksetdb['Link'][:max_cited]:
                                    if 'Id' in link:
                                        cited_by.append(link['Id'])
    except Exception as e:
        print(f"获取被引用关系时出错 (PMID {pmid}): {e}")
    
    return cited_by

# 主函数
def main():
    try:
        print("搜索相关论文...")
        # 搜索基因组选择、AI育种和智能育种相关论文，并限制年份在2024年之前
        query = '((genomic selection) OR (AI breeding) OR (smart breeding) OR (artificial intelligence in plant breeding)) AND ("1900"[Date - Publication] : "2023"[Date - Publication])'
        papers = search_papers(query, max_results=10)
        print(f"共找到 {len(papers)} 篇相关论文")
        
        if len(papers) < 1:
            print("论文数量不足，无法继续")
            return
        
        # 为每篇论文获取引用和被引用关系
        print("获取引用和被引用关系...")
        for i, paper in enumerate(papers):
            pmid = paper['PMID']
            print(f"获取 PMID {pmid} 的引用关系... ({i+1}/{len(papers)})")
            
            try:
                # 获取引用关系
                references = get_references(pmid)
                paper['References'] = references
                paper['References_Count'] = len(references)
                print(f"  - 引用了 {len(references)} 篇论文")
                
                # 获取被引用关系
                cited_by = get_cited_by(pmid)
                paper['Cited_By'] = cited_by
                paper['Cited_By_Count'] = len(cited_by)
                print(f"  - 被 {len(cited_by)} 篇论文引用")
            except Exception as e:
                print(f"处理 PMID {pmid} 时出错: {e}")
            
            time.sleep(0.1)  # 添加延迟，避免API限流
        
        # 保存到JSON文件
        output_json_file = "pubmed_citation_results.json"
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        
        print(f"所有信息已整合并保存到: {output_json_file}")
        
    except Exception as e:
        print(f"主函数执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
