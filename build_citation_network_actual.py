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

# 读取所有论文数据
def load_papers():
    papers = []
    citation_info_dir = "d:\\新建文件夹 (2)\\文献资料\\citation_info"
    
    # 读取all_citations.json
    all_citations_file = os.path.join(citation_info_dir, "all_citations.json")
    if os.path.exists(all_citations_file):
        with open(all_citations_file, 'r', encoding='utf-8') as f:
            papers = json.load(f)
    
    # 读取单独的citation_*.json文件
    for filename in os.listdir(citation_info_dir):
        if filename.startswith("citation_") and filename.endswith(".json") and filename != "all_citations.json":
            file_path = os.path.join(citation_info_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                paper = json.load(f)
                # 检查是否已存在
                if not any(p['PMID'] == paper['PMID'] for p in papers):
                    papers.append(paper)
    
    return papers

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
        print(f"Error getting references for PMID {pmid}: {e}")
    
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
        print(f"Error getting cited by for PMID {pmid}: {e}")
    
    return cited_by

# 获取论文详细信息
def get_paper_info(pmid):
    try:
        # 使用Entrez.esummary获取论文信息
        handle = Entrez.esummary(db="pubmed", id=pmid)
        record = Entrez.read(handle)
        handle.close()
        
        if record:
            article = record[0]
            paper_info = {
                "PMID": pmid,
                "Title": article.get("Title", ""),
                "Journal": article.get("FullJournalName", ""),
                "Year": article.get("PubDate", "").split()[0] if article.get("PubDate") else "",
                "Authors": article.get("AuthorList", []),
                "DOI": article.get("DOI", ""),
                "Abstract": article.get("Abstract", "")
            }
            return paper_info
    except Exception as e:
        print(f"Error getting paper info for PMID {pmid}: {e}")
    
    return None

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
        time.sleep(1)
    
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
    output_file = "citation_network_actual.html"
    net.write_html(output_file)
    print(f"引用网络已生成并保存为: {output_file}")
    
    return output_file

# 主函数
def main():
    print("加载论文数据...")
    papers = load_papers()
    print(f"共加载 {len(papers)} 篇论文")
    
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

if __name__ == "__main__":
    main()