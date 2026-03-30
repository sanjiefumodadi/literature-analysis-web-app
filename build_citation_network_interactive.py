import json
import networkx as nx
import plotly.graph_objects as go
import os
import random

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
    print(f"{i}. {title[:80]}... (PMID: {pmid}) - 被引用 {count} 次")

# 使用力导向布局，调整参数以匹配示例图效果
# 减小k值使节点分布更紧凑，增加迭代次数获得更稳定的布局
pos = nx.spring_layout(G, k=0.3, iterations=300, seed=42, center=(0, 0), scale=1.5)

# 为了使核心节点更自然地居中，根据被引次数调整节点的吸引力
# 不需要手动调整位置，让力导向布局自动处理

# 准备节点数据
node_x = []
node_y = []
node_text = []
node_color = []
node_size = []
node_list = []

# 定义颜色方案（多色，匹配示例图）
color_scheme = [
    "#F7DC6F", "#45B7D1", "#FF6B6B", "#96CEB4",  # 黄色、蓝色、红色、绿色
    "#FFEAA7", "#4ECDC4", "#DDA0DD", "#98D8C8"
]

# 基于引用关系进行简单聚类
# 计算每个节点的邻居相似度，用于聚类
node_clusters = {}
cluster_id = 0
visited = set()

for pmid in G.nodes():
    if pmid not in visited:
        # BFS聚类
        queue = [pmid]
        visited.add(pmid)
        while queue:
            current = queue.pop(0)
            node_clusters[current] = cluster_id
            # 添加直接邻居
            for neighbor in G.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
            # 添加引用当前节点的节点
            for pred in G.predecessors(current):
                if pred not in visited:
                    visited.add(pred)
                    queue.append(pred)
        cluster_id += 1

# 为每个节点分配颜色（基于聚类）
max_cited = max(cited_by_counts.values()) if cited_by_counts else 1

for pmid in G.nodes():
    node_list.append(pmid)
    x, y = pos[pmid]
    node_x.append(x)
    node_y.append(y)
    
    paper = paper_map.get(pmid, {})
    title = paper.get('Title', 'N/A')
    journal = paper.get('Journal', 'N/A')
    year = paper.get('Year', 'N/A')
    cited_by_count = cited_by_counts.get(pmid, 0)
    
    # 根据聚类分配颜色
    cluster_id_node = node_clusters.get(pmid, 0)
    color_idx = cluster_id_node % len(color_scheme)
    color = color_scheme[color_idx]
    
    # 节点大小根据被引次数动态计算（正相关）
    size = 8 + cited_by_count * 3  # 基础大小8，被引次数每增加1，大小增加3
    size = min(size, 35)  # 最大大小35
    
    node_color.append(color)
    node_size.append(size)
    
    # 节点悬停文本
    hover_text = f"PMID: {pmid}<br>Title: {title}<br>Journal: {journal}<br>Year: {year}<br>Cited by: {cited_by_count}"
    node_text.append(hover_text)

# 准备边数据
edge_x = []
edge_y = []
edge_traces = []

# 计算边的权重（引用强度）
edge_weights = {}
for edge in G.edges():
    source, target = edge
    # 引用强度基于被引用次数
    target_cited_count = cited_by_counts.get(target, 0)
    weight = 1 + target_cited_count * 0.2
    edge_weights[edge] = weight

# 为每条边创建单独的trace以支持不同颜色和宽度
for edge in G.edges():
    source, target = edge
    x0, y0 = pos[source]
    x1, y1 = pos[target]
    
    # 边的宽度根据权重计算
    weight = edge_weights.get(edge, 1)
    width = max(0.8, weight * 0.6)
    
    # 边的颜色统一为黄色，匹配示例图
    edge_color = "#F7DC6F"  # 黄色
    
    # 创建边的trace
    edge_trace = go.Scatter(
        x=[x0, x1, None],
        y=[y0, y1, None],
        line=dict(width=width, color=edge_color),
        hoverinfo='none',
        mode='lines',
        showlegend=False
    )
    edge_traces.append(edge_trace)

# 创建节点的trace
node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    hoverinfo='text',
    text=node_text,
    marker=dict(
        showscale=False,
        color=node_color,
        size=node_size,
        line_width=1,
        line_color='rgba(255, 255, 255, 0.5)',
        # 悬停时的样式
        opacity=0.8,
        # 点击时的效果
        line=dict(width=2, color='white')
    ),
    # 支持点击事件
    customdata=[pmid for pmid in node_list],
    showlegend=False
)

# 创建图形
fig = go.Figure(data=edge_traces + [node_trace],
                layout=go.Layout(
                    title=dict(
                        text='Citation Network Visualization<br><sup>Interactive Force-Directed Graph</sup>',
                        font=dict(size=16, color='#ffffff')
                    ),
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=40, l=5, r=5, t=60),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor='#1a1a1a',  # 深色背景
                    paper_bgcolor='#1a1a1a',  # 深色背景
                    dragmode='pan',
                    clickmode='event+select',
                    # 添加工具栏样式
                    modebar={
                        'bgcolor': 'rgba(26, 26, 26, 0.8)',
                        'color': '#ffffff',
                        'activecolor': '#4ECDC4'
                    }
                ))

# 添加缩放和控制按钮
fig.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            direction="left",
            buttons=[
                dict(
                    args=[{"xaxis.autorange": True, "yaxis.autorange": True}],
                    label="Reset View",
                    method="relayout"
                ),
                dict(
                    args=[{"dragmode": "pan"}],
                    label="Pan",
                    method="relayout"
                ),
                dict(
                    args=[{"dragmode": "zoom"}],
                    label="Zoom",
                    method="relayout"
                )
            ],
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.1,
            xanchor="left",
            y=1.1,
            yanchor="top",
            font=dict(color='#ffffff')
        )
    ]
)

# 添加交互说明
fig.update_layout(
    annotations=[
        dict(
            text="Interactive Features:<br>• Hover: Show paper details<br>• Click: Select nodes<br>• Drag: Pan view<br>• Scroll: Zoom in/out<br>• Buttons: Reset/Change mode",
            showarrow=False,
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.02,
            font=dict(color="#888888", size=11),
            align="center"
        )
    ]
)

# 保存为HTML（可交互）
output_dir = "visualization"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_html = os.path.join(output_dir, "citation_network_interactive.html")
# 保存为完整的HTML文件，包含所有必要的JavaScript依赖
fig.write_html(
    output_html,
    include_plotlyjs='cdn',
    full_html=True,
    config={
        'displayModeBar': True,
        'scrollZoom': True,
        'responsive': True,
        'modeBarButtonsToAdd': [
            'pan2d', 'zoom2d', 'zoomIn2d', 'zoomOut2d',
            'autoScale2d', 'resetScale2d',
            'hoverClosestCartesian', 'hoverCompareCartesian'
        ],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'citation_network',
            'scale': 2
        }
    }
)

# 保存为PNG图片（静态）
output_png = os.path.join(output_dir, "citation_network.png")
fig.write_image(output_png, width=1200, height=800, scale=2)

print(f"\n可交互可视化已保存到: {output_html}")
print(f"静态图片已保存到: {output_png}")
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
