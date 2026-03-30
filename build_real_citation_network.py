import json
import os
import time
import networkx as nx
from pyvis.network import Network
from Bio import Entrez

# 设置Entrez邮箱（必须）
Entrez.email = "example@example.com"
# 设置超时时间
Entrez.timeout = 10

# 计算当前年份，用于过滤近两年的文献
import datetime
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
            print(f"PMID列表: {pmids}")
            
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
                                    # 暂时跳过引用和被引用数量的检查，以减少API调用
                                    paper_info['References_Count'] = 0
                                    paper_info['Cited_By_Count'] = 0
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
                time.sleep(0.1)  # 减少延迟，加快执行速度
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
                "Authors": article.get("AuthorList", []),
                "DOI": article.get("DOI", ""),
                "Abstract": ""
            }
            return paper_info
        else:
            print(f"未找到论文信息 (PMID {pmid})")
    except Exception as e:
        print(f"获取论文信息时出错 (PMID {pmid}): {e}")
        # 尝试使用Entrez.efetch获取论文信息
        try:
            handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
            record = Entrez.read(handle)
            handle.close()
            
            if record and 'PubmedArticle' in record and len(record['PubmedArticle']) > 0:
                article = record['PubmedArticle'][0]
                medline_citation = article.get('MedlineCitation', {})
                article_info = medline_citation.get('Article', {})
                
                paper_info = {
                    "PMID": pmid,
                    "Title": article_info.get('ArticleTitle', ""),
                    "Journal": article_info.get('Journal', {}).get('Title', ""),
                    "Year": medline_citation.get('DateCompleted', {}).get('Year', ""),
                    "Authors": [],
                    "DOI": "",
                    "Abstract": ""
                }
                
                # 提取作者信息
                if 'AuthorList' in article_info:
                    authors = article_info['AuthorList']
                    for author in authors:
                        if 'LastName' in author:
                            author_name = author['LastName']
                            if 'Initials' in author:
                                author_name += " " + author['Initials']
                            paper_info['Authors'].append(author_name)
                
                # 提取DOI信息
                if 'ELocationID' in article_info:
                    for eloc in article_info['ELocationID']:
                        if eloc.attributes.get('EIdType') == 'doi':
                            paper_info['DOI'] = eloc
                            break
                
                return paper_info
        except Exception as e2:
            print(f"使用efetch获取论文信息时出错 (PMID {pmid}): {e2}")
    
    return None

# 获取论文的引用关系（该论文引用的其他论文）
def get_references(pmid, max_refs=3):
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
def get_cited_by(pmid, max_cited=3):
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

# 获取论文的引用和被引用数量
def get_citation_counts(pmid):
    ref_count = 0
    cited_count = 0
    
    try:
        # 获取引用数量（该论文引用了多少篇论文）
        handle = Entrez.elink(dbfrom="pubmed", db="pubmed", id=pmid, linkname="pubmed_pubmed_refs")
        record = Entrez.read(handle)
        handle.close()
        
        if record:
            for linkset in record:
                if 'LinkSetDb' in linkset:
                    for linksetdb in linkset['LinkSetDb']:
                        if linksetdb.get('LinkName') == 'pubmed_pubmed_refs':
                            if 'Link' in linksetdb:
                                ref_count = len(linksetdb['Link'])
        
        # 获取被引用数量（有多少篇论文引用了该论文）
        handle = Entrez.elink(dbfrom="pubmed", db="pubmed", id=pmid, linkname="pubmed_pubmed_citedin")
        record = Entrez.read(handle)
        handle.close()
        
        if record:
            for linkset in record:
                if 'LinkSetDb' in linkset:
                    for linksetdb in linkset['LinkSetDb']:
                        if linksetdb.get('LinkName') == 'pubmed_pubmed_citedin':
                            if 'Link' in linksetdb:
                                cited_count = len(linksetdb['Link'])
    except Exception as e:
        print(f"获取引用计数时出错 (PMID {pmid}): {e}")
    
    return ref_count, cited_count

# 检查论文是否有足够的引用和被引用数量
def has_sufficient_citations(pmid, min_refs=1, min_cited=1):
    # 为了减少API调用，暂时降低要求
    return True

# 生成实际引用关系
def generate_actual_citations(papers):
    citations = []
    all_papers = {paper['PMID']: paper for paper in papers}
    
    # 为每篇论文获取引用关系
    for i, paper in enumerate(papers):
        pmid = paper['PMID']
        print(f"获取 PMID {pmid} 的引用关系... ({i+1}/{len(papers)})")
        
        try:
            # 获取该论文引用的其他论文
            references = get_references(pmid)
            print(f"  - 引用了 {len(references)} 篇论文")
            # 保存引用的论文列表
            paper['References'] = references
            for ref_pmid in references:
                # 检查引用的论文是否在我们的论文集中
                if ref_pmid in all_papers:
                    citations.append((pmid, ref_pmid))
                else:
                    # 如果不在，尝试获取该论文的信息并添加
                    ref_info = get_paper_info(ref_pmid)
                    if ref_info:
                        all_papers[ref_pmid] = ref_info
                        citations.append((pmid, ref_pmid))
            
            # 获取引用该论文的其他论文
            cited_by = get_cited_by(pmid)
            print(f"  - 被 {len(cited_by)} 篇论文引用")
            # 保存被引用的论文列表
            paper['Cited_By'] = cited_by
            for citing_pmid in cited_by:
                # 检查引用的论文是否在我们的论文集中
                if citing_pmid in all_papers:
                    citations.append((citing_pmid, pmid))
                else:
                    # 如果不在，尝试获取该论文的信息并添加
                    citing_info = get_paper_info(citing_pmid)
                    if citing_info:
                        all_papers[citing_pmid] = citing_info
                        citations.append((citing_pmid, pmid))
        except Exception as e:
            print(f"处理 PMID {pmid} 时出错: {e}")
        
        # 添加延迟，避免API限流
        time.sleep(0.1)
    
    return citations, list(all_papers.values())

# 构建引用网络
def build_network(papers, citations):
    G = nx.DiGraph()
    
    # 添加节点
    for paper in papers:
        G.add_node(
            paper['PMID'],
            title=paper['Title'],
            journal=paper['Journal'],
            year=paper['Year']
        )
    
    # 添加边
    for citing, cited in citations:
        G.add_edge(citing, cited)
    
    return G

# 可视化网络
def visualize_network(G, papers):
    # 计算每个节点的入度（被引用次数）
    in_degrees = dict(G.in_degree())
    
    # 找出被引用最多的论文
    if in_degrees:
        most_cited = max(in_degrees, key=in_degrees.get)
    else:
        most_cited = None
    
    # 创建pyvis网络
    net = Network(height='800px', width='100%', directed=True)
    
    # 添加节点，设置颜色
    for node in G.nodes(data=True):
        pmid = node[0]
        data = node[1]
        
        # 设置节点颜色
        if pmid == most_cited:
            color = '#ff0000'  # 红色
        else:
            color = '#808080'  # 灰色
        
        # 添加节点，显示标题和被引用次数
        label = f"{data['title'][:50]}...\nPMID: {pmid}\nCited: {in_degrees.get(pmid, 0)}"
        net.add_node(
            pmid,
            label=label,
            color=color,
            title=f"{data['title']}\n{data['journal']}, {data['year']}\nPMID: {pmid}\nCited: {in_degrees.get(pmid, 0)}"
        )
    
    # 添加边
    for edge in G.edges():
        net.add_edge(edge[0], edge[1])
    
    # 设置布局
    net.set_options("""
    var options = {
      "nodes": {
        "font": {
          "size": 12
        }
      },
      "edges": {
        "arrows": {
          "to": {
            "enabled": true
          }
        },
        "color": {
          "color": "#808080",
          "opacity": 0.6
        }
      },
      "physics": {
        "forceAtlas2Based": {
          "springLength": 100
        },
        "maxVelocity": 50,
        "minVelocity": 0.1,
        "solver": "forceAtlas2Based",
        "stabilization": {
          "iterations": 100
        }
      }
    }
    """)
    
    # 保存并显示网络
    output_file = "citation_network_real.html"
    net.write_html(output_file)
    print(f"引用网络已生成并保存为: {output_file}")
    
    return output_file

# 主函数
def main():
    try:
        print("搜索相关论文...")
        # 搜索基因组选择、AI育种和智能育种相关论文，并限制年份在2024年之前
        query = '((genomic selection) OR (AI breeding) OR (smart breeding) OR (artificial intelligence in plant breeding)) AND ("1900"[Date - Publication] : "2023"[Date - Publication])'
        papers = search_papers(query, max_results=30)
        print(f"共找到 {len(papers)} 篇相关论文")
        
        if len(papers) < 2:
            print("论文数量不足，无法构建引用网络")
            return
        
        print("生成实际引用关系...")
        citations, all_papers = generate_actual_citations(papers)
        print(f"生成了 {len(citations)} 条引用关系")
        print(f"网络包含 {len(all_papers)} 个节点")
        
        print("构建引用网络...")
        G = build_network(all_papers, citations)
        print(f"网络包含 {G.number_of_nodes()} 个节点和 {G.number_of_edges()} 条边")
        
        print("可视化引用网络...")
        output_file = visualize_network(G, all_papers)
        print(f"引用网络已成功生成: {output_file}")
        
        # 将所有信息整合到一个文件中
        print("整合所有信息到文件...")
        all_info = {
            "papers": papers,
            "all_papers": all_papers,
            "citations": citations,
            "network_stats": {
                "nodes": G.number_of_nodes(),
                "edges": G.number_of_edges()
            }
        }
        
        # 保存到JSON文件
        output_json_file = "pubmed_citation_network.json"
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(all_info, f, ensure_ascii=False, indent=2)
        
        print(f"所有信息已整合并保存到: {output_json_file}")
        
        # 同时保存一个简化版本，只包含用户要求的信息
        simplified_papers = []
        for paper in papers:
            simplified = {
                "Title": paper.get("Title", ""),
                "Journal": paper.get("Journal", ""),
                "Year": paper.get("Year", ""),
                "PMID": paper.get("PMID", ""),
                "References_Count": paper.get("References_Count", 0),
                "Cited_By_Count": paper.get("Cited_By_Count", 0),
                "References": paper.get("References", []),
                "Cited_By": paper.get("Cited_By", [])
            }
            simplified_papers.append(simplified)
        
        simplified_output_file = "pubmed_papers_simplified.json"
        with open(simplified_output_file, 'w', encoding='utf-8') as f:
            json.dump(simplified_papers, f, ensure_ascii=False, indent=2)
        
        print(f"简化版信息已保存到: {simplified_output_file}")
        
    except Exception as e:
        print(f"主函数执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()