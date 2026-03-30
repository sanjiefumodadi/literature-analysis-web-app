import json
import networkx as nx
from pyvis.network import Network

# 读取文献数据
with open('pubmed_citation_results.json', 'r', encoding='utf-8') as f:
    papers = json.load(f)

# 构建引用网络
G = nx.DiGraph()

# 添加节点
for paper in papers:
    pmid = paper['PMID']
    title = paper['Title']
    journal = paper['Journal']
    year = paper['Year']
    cited_by_count = paper['Cited_By_Count']
    
    # 添加节点，包含论文信息
    G.add_node(
        pmid,
        title=title,
        journal=journal,
        year=year,
        cited_by_count=cited_by_count
    )

# 添加边（引用关系）
for paper in papers:
    pmid = paper['PMID']
    references = paper['References']
    
    for ref_pmid in references:
        # 只添加在论文集中存在的引用关系
        if ref_pmid in G:
            G.add_edge(pmid, ref_pmid)

# 找出被引用最多的论文
cited_by_counts = {node: G.in_degree(node) for node in G.nodes()}
if cited_by_counts:
    most_cited_pmid = max(cited_by_counts, key=cited_by_counts.get)
    most_cited_count = cited_by_counts[most_cited_pmid]
    print(f"被引用最多的论文: PMID {most_cited_pmid}，被引用 {most_cited_count} 次")
else:
    most_cited_pmid = None
    print("没有引用关系")

# 创建pyvis网络
net = Network(height='800px', width='100%', directed=True)

# 添加节点，设置颜色
for node in G.nodes(data=True):
    pmid = node[0]
    data = node[1]
    
    # 设置节点颜色
    if pmid == most_cited_pmid:
        color = '#ff0000'  # 红色
    else:
        color = '#808080'  # 灰色
    
    # 添加节点，显示标题和被引用次数
    label = f"{data['title'][:50]}...\nPMID: {pmid}\nCited: {data['cited_by_count']}"
    net.add_node(
        pmid,
        label=label,
        color=color,
        title=f"{data['title']}\n{data['journal']}, {data['year']}\nPMID: {pmid}\nCited: {data['cited_by_count']}"
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
output_file = "citation_network_visualization.html"
net.write_html(output_file)
print(f"引用网络已生成并保存为: {output_file}")

# 打印网络统计信息
print(f"网络包含 {G.number_of_nodes()} 个节点和 {G.number_of_edges()} 条边")
