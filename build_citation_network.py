import json
import networkx as nx
from pyvis.network import Network
import os

# 读取引用网络数据
input_file = "pubmed_citation_network.json"
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 提取论文数据
papers = data.get('papers', []) + data.get('all_papers', [])

# 创建论文ID到信息的映射
paper_map = {}
for paper in papers:
    pmid = paper.get('PMID')
    if pmid:
        paper_map[pmid] = paper

# 创建引用网络
G = nx.DiGraph()

# 添加节点
for pmid, paper in paper_map.items():
    G.add_node(pmid, 
               title=paper.get('Title', 'N/A'),
               journal=paper.get('Journal', 'N/A'),
               year=paper.get('Year', 'N/A'),
               cited_by_count=len(paper.get('Cited_By', [])))

# 添加边（引用关系）
for pmid, paper in paper_map.items():
    references = paper.get('References', [])
    for ref_pmid in references:
        if ref_pmid in paper_map:
            G.add_edge(pmid, ref_pmid, label="cites")

# 计算被引用次数
cited_by_counts = {}
for pmid in G.nodes():
    cited_by_counts[pmid] = G.in_degree(pmid)

# 找出被引用最多的论文（核心论文）
sorted_papers = sorted(cited_by_counts.items(), key=lambda x: x[1], reverse=True)
top_papers = [pmid for pmid, count in sorted_papers[:10]]  # 前10个被引用最多的论文

print("核心论文（被引用最多的10篇）:")
for i, (pmid, count) in enumerate(sorted_papers[:10], 1):
    paper = paper_map.get(pmid, {})
    title = paper.get('Title', 'N/A')
    print(f"{i}. {title} (PMID: {pmid}) - 被引用 {count} 次")

# 创建可视化
net = Network(height="800px", width="100%", directed=True, notebook=True)

# 添加节点并设置样式
for pmid in G.nodes():
    paper = paper_map.get(pmid, {})
    title = paper.get('Title', 'N/A')
    journal = paper.get('Journal', 'N/A')
    year = paper.get('Year', 'N/A')
    cited_by_count = cited_by_counts.get(pmid, 0)
    
    # 设置节点颜色：核心论文为红色，其他为灰色
    if pmid in top_papers:
        color = "#ff4d4d"  # 红色
        size = 25
    else:
        color = "#999999"  # 灰色
        size = 15
    
    # 添加节点
    net.add_node(
        pmid,
        label=title[:30] + "..." if len(title) > 30 else title,
        title=f"Title: {title}\nJournal: {journal}\nYear: {year}\nCited by: {cited_by_count}",
        color=color,
        size=size
    )

# 添加边
for edge in G.edges():
    source, target = edge
    net.add_edge(source, target, arrowStrikethrough=False)

# 设置布局
net.barnes_hut(gravity=-80000, central_gravity=0.3, spring_length=100, spring_strength=0.001, damping=0.09)

# 保存可视化结果
output_dir = "visualization"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file = os.path.join(output_dir, "citation_network_visualization.html")
net.save_graph(output_file)

print(f"\n引用网络可视化已保存到: {output_file}")
print(f"网络包含 {G.number_of_nodes()} 个节点和 {G.number_of_edges()} 条边")

# 分析网络属性
print("\n网络分析结果:")
print(f"节点数: {G.number_of_nodes()}")
print(f"边数: {G.number_of_edges()}")
print(f"平均入度: {sum(cited_by_counts.values()) / len(cited_by_counts):.2f}")
print(f"平均出度: {G.number_of_edges() / G.number_of_nodes():.2f}")

# 计算网络密度
density = nx.density(G)
print(f"网络密度: {density:.4f}")
