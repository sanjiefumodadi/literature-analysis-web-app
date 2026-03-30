import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

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

# 创建图形
fig, ax = plt.subplots(figsize=(16, 12))

# 设置布局
pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

# 准备节点颜色和大小
node_colors = []
node_sizes = []
for pmid in G.nodes():
    if pmid in top_papers:
        node_colors.append('#ff4d4d')  # 红色 - 核心论文
        node_sizes.append(800)
    else:
        node_colors.append('#999999')  # 灰色 - 其他论文
        node_sizes.append(300)

# 绘制边
nx.draw_networkx_edges(G, pos, 
                       edge_color='#666666',
                       arrows=True,
                       arrowsize=15,
                       arrowstyle='->',
                       width=0.8,
                       alpha=0.6,
                       ax=ax)

# 绘制节点
nx.draw_networkx_nodes(G, pos,
                       node_color=node_colors,
                       node_size=node_sizes,
                       alpha=0.9,
                       ax=ax)

# 添加节点标签（只显示核心论文的标题）
labels = {}
for pmid in G.nodes():
    if pmid in top_papers:
        paper = paper_map.get(pmid, {})
        title = paper.get('Title', '')
        # 截断长标题
        if len(title) > 40:
            title = title[:37] + '...'
        labels[pmid] = title

nx.draw_networkx_labels(G, pos, labels, 
                        font_size=8,
                        font_color='black',
                        ax=ax)

# 添加图例
red_patch = mpatches.Patch(color='#ff4d4d', label='核心论文（被引用最多）')
gray_patch = mpatches.Patch(color='#