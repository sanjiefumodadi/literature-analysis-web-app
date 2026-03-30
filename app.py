import streamlit as st
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import networkx as nx
import os
import tempfile

# 配置页面
def setup_page():
    st.set_page_config(
        page_title="学术文献引用网络分析",
        page_icon="📚",
        layout="wide"
    )
    
    # 自定义CSS样式 - 现代化深色主题（复刻第二张图）
    st.markdown("""
    <style>
    /* 全局深色背景 - 深蓝色调 */
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
        color: #e0e0e0;
        min-height: 100vh;
        position: relative;
    }
    
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
    }
    
    /* 侧边栏样式 - 深蓝色背景 */
    .css-1d391kg {
        background: linear-gradient(180deg, #16213e 0%, #0f0f23 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem 1rem;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.3);
    }
    
    /* 标题样式 - 现代感 */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    h1 {
        font-size: 2.5rem;
        background: linear-gradient(90deg, #4D96FF, #6BCB77);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    h2 {
        font-size: 1.8rem;
        color: #4D96FF;
        border-bottom: 2px solid #4D96FF;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    
    /* 文本样式 */
    p, span, div {
        color: #e0e0e0;
    }
    
    /* 按钮样式 - 现代彩色 */
    .stButton>button {
        background: linear-gradient(135deg, #4D96FF, #6BCB77);
        border: none;
        color: white;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(77, 150, 255, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(77, 150, 255, 0.4);
    }
    
    /* 输入框样式 - 深色 */
    .stTextInput>div>div>input {
        background: rgba(30, 30, 50, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #e0e0e0;
        border-radius: 8px;
        padding: 0.75rem;
        box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #4D96FF;
        box-shadow: inset 0 2px 8px rgba(77, 150, 255, 0.2);
    }
    
    /* 滑块样式 */
    .stSlider {
        color: #4D96FF;
    }
    
    .stSlider>div>div>div>div {
        background: rgba(255, 255, 255, 0.1);
    }
    
    .stSlider>div>div>div>div>div {
        background: linear-gradient(90deg, #4D96FF, #6BCB77);
    }
    
    /* 卡片样式 - 彩色现代卡片 */
    .stExpander {
        background: rgba(30, 30, 50, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .stExpander:hover {
        box-shadow: 0 12px 40px rgba(77, 150, 255, 0.2);
        transform: translateY(-2px);
    }
    
    .stExpanderHeader {
        background: linear-gradient(90deg, #4D96FF, #6BCB77);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 600;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stExpanderContent {
        background: rgba(30, 30, 50, 0.8) !important;
        padding: 1rem;
    }
    
    /* 成功/错误消息 - 现代卡片 */
    .stSuccess, .stError, .stInfo, .stWarning {
        background: rgba(30, 30, 50, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        padding: 1rem !important;
    }
    
    /* 加载动画 */
    .stSpinner > div {
        border-top-color: #4D96FF !important;
        border-width: 4px !important;
    }
    
    /* 滚动条样式 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0f0f23;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #4D96FF;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #6BCB77;
    }
    
    /* 装饰元素 - 圆形背景 */
    .main::before {
        content: '';
        position: fixed;
        top: 10%;
        left: 10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(77, 150, 255, 0.1) 0%, transparent 70%);
        border-radius: 50%;
        z-index: 0;
    }
    
    .main::after {
        content: '';
        position: fixed;
        bottom: 10%;
        right: 10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(107, 203, 119, 0.1) 0%, transparent 70%);
        border-radius: 50%;
        z-index: 0;
    }
    
    /* 内容区域 */
    .block-container {
        z-index: 1;
        position: relative;
    }
    
    /* 现代仪表板元素 */
    .dashboard-card {
        background: rgba(30, 30, 50, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .dashboard-card:hover {
        box-shadow: 0 12px 40px rgba(77, 150, 255, 0.2);
        transform: translateY(-2px);
    }
    
    .card-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #4D96FF;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-content {
        color: #e0e0e0;
    }
    
    /* 状态卡片 */
    .status-card {
        background: linear-gradient(135deg, rgba(77, 150, 255, 0.1), rgba(107, 203, 119, 0.1));
        border: 1px solid rgba(77, 150, 255, 0.2);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .status-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: #4D96FF;
    }
    
    .status-label {
        font-size: 0.9rem;
        color: #b0b0b0;
    }
    
    /* 网格布局 */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    /* 响应式调整 */
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem;
        }
        
        h2 {
            font-size: 1.5rem;
        }
        
        .grid-container {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 现代仪表板标题栏
    st.title("学术文献引用网络分析")
    st.markdown("---")
    
    # 添加模式切换和控制按钮
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown("### 智能文献分析系统")
    with col2:
        st.button("📊 数据分析")
    with col3:
        st.button("⚙️ 设置")

# 主题分类和颜色映射
TOPICS = {
    'genomicSelection': {'name': '基因组选择', 'color': '#FFD93D'},
    'aiBreeding': {'name': '人工智能育种', 'color': '#6BCB77'},
    'cropGenetics': {'name': '作物遗传改良', 'color': '#4D96FF'},
    'molecularMarker': {'name': '分子标记辅助', 'color': '#FF6B6B'},
    'quantitativeGenetics': {'name': '数量遗传学', 'color': '#C9B1FF'}
}

# 根据标题分类主题
def classify_topic(title):
    title_lower = title.lower()
    if any(kw in title_lower for kw in ['genomic selection', 'genomic', 'gs', '基因组选择']):
        return 'genomicSelection'
    elif any(kw in title_lower for kw in ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural', '人工智能', '深度学习']):
        return 'aiBreeding'
    elif any(kw in title_lower for kw in ['crop', 'plant', 'yield', '作物', '产量', '遗传改良']):
        return 'cropGenetics'
    elif any(kw in title_lower for kw in ['molecular marker', 'marker', 'ssr', 'snp', '分子标记']):
        return 'molecularMarker'
    elif any(kw in title_lower for kw in ['quantitative', 'qtl', 'heritability', '数量遗传', '遗传力']):
        return 'quantitativeGenetics'
    else:
        return 'cropGenetics'  # 默认分类

# 调用PubMed API搜索文献
def search_pubmed(keywords, max_results=20):
    api_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    search_terms = f"({keywords})"
    encoded_terms = urllib.parse.quote(search_terms)
    esearch_url = f"{api_url}esearch.fcgi?db=pubmed&term={encoded_terms}&retmax={max_results}"
    
    with urllib.request.urlopen(esearch_url) as response:
        content = response.read()
    
    tree = ET.ElementTree(ET.fromstring(content))
    root = tree.getroot()
    
    ids = []
    for id_elem in root.findall('.//Id'):
        ids.append(id_elem.text)
    
    if not ids:
        return []
    
    id_string = ",".join(ids)
    fetch_url = f"{api_url}efetch.fcgi?db=pubmed&id={id_string}&retmode=xml"
    
    with urllib.request.urlopen(fetch_url) as fetch_response:
        fetch_content = fetch_response.read()
    
    fetch_tree = ET.ElementTree(ET.fromstring(fetch_content))
    fetch_root = fetch_tree.getroot()
    
    articles = []
    for pubmed_article in fetch_root.findall('.//PubmedArticle'):
        article_info = {}
        
        medline_citation = pubmed_article.find('MedlineCitation')
        if medline_citation:
            article = medline_citation.find('Article')
            if article:
                article_title = article.find('ArticleTitle')
                if article_title is not None:
                    article_info['Title'] = article_title.text
                
                journal = article.find('Journal')
                if journal:
                    journal_title = journal.find('Title')
                    if journal_title is not None:
                        article_info['Journal'] = journal_title.text
                
                pub_date = article.find('PubDate')
                if pub_date:
                    year = pub_date.find('Year')
                    if year is not None:
                        article_info['Year'] = year.text
                
                if 'Year' not in article_info:
                    journal = article.find('Journal')
                    if journal:
                        journal_issue = journal.find('JournalIssue')
                        if journal_issue:
                            pub_date = journal_issue.find('PubDate')
                            if pub_date:
                                year = pub_date.find('Year')
                                if year is not None:
                                    article_info['Year'] = year.text
                
                pmid = medline_citation.find('PMID')
                if pmid is not None:
                    article_info['PMID'] = pmid.text
                
                # 提取作者
                author_list = article.find('AuthorList')
                if author_list is not None:
                    authors = []
                    for author in author_list.findall('Author'):
                        last_name = author.find('LastName')
                        if last_name is not None:
                            authors.append(last_name.text)
                    if authors:
                        article_info['Authors'] = ', '.join(authors[:3]) + (' et al.' if len(authors) > 3 else '')
                    else:
                        article_info['Authors'] = 'Unknown'
                else:
                    article_info['Authors'] = 'Unknown'
        
        if article_info:
            # 分类主题
            article_info['Topic'] = classify_topic(article_info.get('Title', ''))
            articles.append(article_info)
    
    # 获取引用关系
    for article in articles:
        pmid = article.get('PMID')
        if pmid:
            try:
                ref_url = f"{api_url}elink.fcgi?dbfrom=pubmed&db=pubmed&id={pmid}&linkname=pubmed_pubmed_refs"
                with urllib.request.urlopen(ref_url) as ref_response:
                    ref_content = ref_response.read()
                
                ref_tree = ET.ElementTree(ET.fromstring(ref_content))
                ref_root = ref_tree.getroot()
                
                references = []
                for linkset in ref_root.findall('.//LinkSet'):
                    for linksetdb in linkset.findall('.//LinkSetDb'):
                        if linksetdb.get('LinkName') == 'pubmed_pubmed_refs':
                            for link in linksetdb.findall('.//Link'):
                                ref_id = link.find('Id').text
                                references.append(ref_id)
                
                article['References'] = references[:10]
                article['References_Count'] = len(references)
            except Exception as e:
                article['References'] = []
                article['References_Count'] = 0
            
            try:
                cited_url = f"{api_url}elink.fcgi?dbfrom=pubmed&db=pubmed&id={pmid}&linkname=pubmed_pubmed_citedin"
                with urllib.request.urlopen(cited_url) as cited_response:
                    cited_content = cited_response.read()
                
                cited_tree = ET.ElementTree(ET.fromstring(cited_content))
                cited_root = cited_tree.getroot()
                
                cited_by = []
                for linkset in cited_root.findall('.//LinkSet'):
                    for linksetdb in linkset.findall('.//LinkSetDb'):
                        if linksetdb.get('LinkName') == 'pubmed_pubmed_citedin':
                            for link in linksetdb.findall('.//Link'):
                                cited_id = link.find('Id').text
                                cited_by.append(cited_id)
                
                article['Cited_By'] = cited_by[:10]
                article['Cited_By_Count'] = len(cited_by)
            except Exception as e:
                article['Cited_By'] = []
                article['Cited_By_Count'] = 0
    
    return articles

# 计算节点大小
def get_node_size(citations):
    if citations > 50:
        return 25
    elif citations > 20:
        return 18
    elif citations > 10:
        return 12
    else:
        return 7

# 构建专业的学术引用网络可视化HTML
def build_academic_citation_network(articles):
    # 创建论文ID到信息的映射
    paper_map = {}
    for article in articles:
        pmid = article.get('PMID')
        if pmid:
            paper_map[pmid] = article
    
    # 创建引用网络
    G = nx.DiGraph()
    
    # 添加节点
    for pmid, paper in paper_map.items():
        G.add_node(pmid, 
                   title=paper.get('Title', 'N/A'),
                   journal=paper.get('Journal', 'N/A'),
                   year=paper.get('Year', 'N/A'),
                   citations=paper.get('Cited_By_Count', 0),
                   authors=paper.get('Authors', 'Unknown'),
                   topic=paper.get('Topic', 'cropGenetics'))
    
    # 添加边（引用关系）
    for pmid, paper in paper_map.items():
        references = paper.get('References', [])
        for ref_pmid in references:
            if ref_pmid in paper_map:
                G.add_edge(pmid, ref_pmid)
    
    # 找出核心文献（被引用最多的前5篇）
    cited_by_counts = {node: G.in_degree(node) for node in G.nodes()}
    core_papers = sorted(cited_by_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    core_pmids = {pmid for pmid, _ in core_papers}
    
    # 准备节点数据
    nodes_data = []
    for node in G.nodes(data=True):
        pmid = node[0]
        data = node[1]
        citations = data['citations']
        is_core = pmid in core_pmids
        
        nodes_data.append({
            'id': pmid,
            'title': data['title'],
            'authors': data['authors'],
            'year': data['year'],
            'citations': citations,
            'topic': data['topic'],
            'isCore': is_core,
            'size': get_node_size(citations)
        })
    
    # 准备边数据
    edges_data = []
    for edge in G.edges():
        edges_data.append({
            'source': edge[0],
            'target': edge[1],
            'strength': 0.5
        })
    
    # 生成HTML
    html_content = generate_academic_network_html(nodes_data, edges_data, len(nodes_data), len(edges_data), len(core_pmids))
    
    # 保存到临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        temp_file = f.name
    
    return temp_file, core_pmids, paper_map

# 生成专业的学术网络可视化HTML
def generate_academic_network_html(nodes, edges, node_count, edge_count, core_count):
    topics_json = json.dumps(TOPICS, ensure_ascii=False)
    nodes_json = json.dumps(nodes, ensure_ascii=False)
    edges_json = json.dumps(edges, ensure_ascii=False)
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>学术文献引用网络可视化</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
            min-height: 100vh;
            overflow: hidden;
        }}
        
        #container {{
            width: 100vw;
            height: 100vh;
            position: relative;
        }}
        
        #graph {{
            width: 100%;
            height: 100%;
        }}
        
        .node {{
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .node:hover {{
            filter: brightness(1.3);
        }}
        
        .link {{
            stroke-opacity: 0.4;
            transition: all 0.3s ease;
        }}
        
        .link:hover {{
            stroke-opacity: 0.8;
        }}
        
        .node-label {{
            font-size: 10px;
            fill: #e0e0e0;
            pointer-events: none;
            text-shadow: 0 1px 3px rgba(0,0,0,0.8);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .node:hover + .node-label,
        .node-label.visible {{
            opacity: 1;
        }}
        
        #tooltip {{
            position: absolute;
            padding: 12px 16px;
            background: rgba(20, 20, 35, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s ease;
            max-width: 320px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(10px);
            z-index: 1000;
        }}
        
        #tooltip.visible {{
            opacity: 1;
        }}
        
        #tooltip h4 {{
            margin: 0 0 8px 0;
            font-size: 14px;
            color: #fff;
            line-height: 1.4;
        }}
        
        #tooltip p {{
            margin: 4px 0;
            font-size: 12px;
            color: #b0b0b0;
            line-height: 1.5;
        }}
        
        #tooltip .citations {{
            color: #ffd700;
            font-weight: 600;
        }}
        
        #tooltip .topic {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            margin-top: 6px;
        }}
        
        #legend {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(20, 20, 35, 0.9);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        
        #legend h3 {{
            margin: 0 0 15px 0;
            font-size: 14px;
            color: #fff;
            font-weight: 600;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 10px 0;
            font-size: 12px;
            color: #d0d0d0;
        }}
        
        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }}
        
        .legend-size {{
            display: flex;
            align-items: center;
            margin: 15px 0;
            font-size: 12px;
            color: #d0d0d0;
        }}
        
        .size-circle {{
            border: 2px solid rgba(255,255,255,0.5);
            border-radius: 50%;
            margin-right: 10px;
            background: transparent;
        }}
        
        #controls {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            display: flex;
            gap: 10px;
        }}
        
        .control-btn {{
            padding: 10px 20px;
            background: rgba(30, 30, 50, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            color: #e0e0e0;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }}
        
        .control-btn:hover {{
            background: rgba(50, 50, 80, 0.9);
            border-color: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }}
        
        #stats {{
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(20, 20, 35, 0.9);
            padding: 15px 20px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            color: #d0d0d0;
            font-size: 12px;
        }}
        
        #stats div {{
            margin: 5px 0;
        }}
        
        #stats span {{
            color: #fff;
            font-weight: 600;
        }}

        .pulse {{
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0% {{ filter: brightness(1); }}
            50% {{ filter: brightness(1.3); }}
            100% {{ filter: brightness(1); }}
        }}
    </style>
</head>
<body>
    <div id="container">
        <svg id="graph"></svg>
        
        <div id="tooltip">
            <h4 id="tt-title"></h4>
            <p id="tt-author"></p>
            <p id="tt-year"></p>
            <p>被引次数: <span id="tt-citations" class="citations"></span></p>
            <p>PMID: <span id="tt-pmid"></span></p>
            <span id="tt-topic" class="topic"></span>
        </div>
        
        <div id="stats">
            <div>文献总数: <span id="node-count">{node_count}</span></div>
            <div>引用关系: <span id="edge-count">{edge_count}</span></div>
            <div>核心文献: <span id="core-count">{core_count}</span></div>
        </div>
        
        <div id="legend">
            <h3>研究主题</h3>
            <div class="legend-item">
                <div class="legend-color" style="background: #FFD93D;"></div>
                <span>基因组选择</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #6BCB77;"></div>
                <span>人工智能育种</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #4D96FF;"></div>
                <span>作物遗传改良</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FF6B6B;"></div>
                <span>分子标记辅助</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #C9B1FF;"></div>
                <span>数量遗传学</span>
            </div>
            <div style="margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px;">
                <h3 style="font-size: 12px; margin-bottom: 10px;">节点大小</h3>
                <div class="legend-size">
                    <div class="size-circle" style="width: 8px; height: 8px;"></div>
                    <span>低被引 (&lt; 10)</span>
                </div>
                <div class="legend-size">
                    <div class="size-circle" style="width: 14px; height: 14px;"></div>
                    <span>中被引 (10-50)</span>
                </div>
                <div class="legend-size">
                    <div class="size-circle" style="width: 22px; height: 22px;"></div>
                    <span>高被引 (&gt; 50)</span>
                </div>
            </div>
        </div>
        
        <div id="controls">
            <button class="control-btn" onclick="resetZoom()">重置视图</button>
            <button class="control-btn" onclick="toggleAnimation()">切换动画</button>
            <button class="control-btn" onclick="highlightCore()">高亮核心</button>
        </div>
    </div>

    <script>
        const topics = {topics_json};
        const nodes = {nodes_json};
        const edges = {edges_json};
        
        const svg = d3.select('#graph');
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        svg.attr('width', width).attr('height', height);
        
        const g = svg.append('g');
        
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {{
                g.attr('transform', event.transform);
            }});
        
        svg.call(zoom);
        
        const getNodeSize = (citations) => {{
            if (citations > 100) return 25;
            if (citations > 50) return 18;
            if (citations > 20) return 12;
            return 7;
        }};
        
        const getLinkWidth = (strength) => {{
            return strength * 2 + 0.5;
        }};
        
        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(edges)
                .id(d => d.id)
                .distance(d => 80 + (1 - d.strength) * 100)
                .strength(d => d.strength * 0.5))
            .force('charge', d3.forceManyBody()
                .strength(d => d.isCore ? -800 : -300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide()
                .radius(d => getNodeSize(d.citations) + 10))
            .force('x', d3.forceX(width / 2).strength(0.05))
            .force('y', d3.forceY(height / 2).strength(0.05));
        
        const link = g.append('g')
            .selectAll('line')
            .data(edges)
            .enter()
            .append('line')
            .attr('class', 'link')
            .attr('stroke', '#5a6a8a')
            .attr('stroke-width', d => getLinkWidth(d.strength));
        
        const node = g.append('g')
            .selectAll('circle')
            .data(nodes)
            .enter()
            .append('circle')
            .attr('class', d => `node ${{d.isCore ? 'pulse' : ''}}`)
            .attr('r', d => getNodeSize(d.citations))
            .attr('fill', d => topics[d.topic].color)
            .attr('stroke', d => d.isCore ? '#fff' : 'rgba(255,255,255,0.3)')
            .attr('stroke-width', d => d.isCore ? 3 : 1)
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));
        
        const label = g.append('g')
            .selectAll('text')
            .data(nodes.filter(d => d.isCore || d.citations > 60))
            .enter()
            .append('text')
            .attr('class', 'node-label visible')
            .attr('text-anchor', 'middle')
            .attr('dy', d => getNodeSize(d.citations) + 15)
            .text(d => d.title.length > 25 ? d.title.substring(0, 25) + '...' : d.title);
        
        const tooltip = d3.select('#tooltip');
        
        node.on('mouseover', function(event, d) {{
            d3.select(this)
                .transition()
                .duration(200)
                .attr('r', getNodeSize(d.citations) * 1.3);
            
            tooltip.select('#tt-title').text(d.title);
            tooltip.select('#tt-author').text(`作者: ${{d.authors}}`);
            tooltip.select('#tt-year').text(`发表年份: ${{d.year}}`);
            tooltip.select('#tt-citations').text(d.citations);
            tooltip.select('#tt-pmid').text(d.id);
            tooltip.select('#tt-topic')
                .text(topics[d.topic].name)
                .style('background', topics[d.topic].color)
                .style('color', '#000');
            
            tooltip
                .style('left', (event.pageX + 15) + 'px')
                .style('top', (event.pageY - 10) + 'px')
                .classed('visible', true);
            
            link.style('stroke', l => 
                (l.source.id === d.id || l.target.id === d.id) ? '#fff' : '#5a6a8a'
            ).style('stroke-opacity', l => 
                (l.source.id === d.id || l.target.id === d.id) ? 1 : 0.2
            );
        }})
        .on('mouseout', function(event, d) {{
            d3.select(this)
                .transition()
                .duration(200)
                .attr('r', getNodeSize(d.citations));
            
            tooltip.classed('visible', false);
            
            link.style('stroke', '#5a6a8a')
                .style('stroke-opacity', 0.4);
        }})
        .on('click', function(event, d) {{
            const connectedIds = new Set();
            connectedIds.add(d.id);
            
            edges.forEach(l => {{
                if (l.source.id === d.id) connectedIds.add(l.target.id);
                if (l.target.id === d.id) connectedIds.add(l.source.id);
            }});
            
            node.style('opacity', n => connectedIds.has(n.id) ? 1 : 0.2);
            link.style('opacity', l => 
                (l.source.id === d.id || l.target.id === d.id) ? 1 : 0.05
            );
            
            setTimeout(() => {{
                node.style('opacity', 1);
                link.style('opacity', 1);
            }}, 2000);
        }});
        
        simulation.on('tick', () => {{
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);
            
            label
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        }});
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        let animationEnabled = true;
        
        function resetZoom() {{
            svg.transition()
                .duration(750)
                .call(zoom.transform, d3.zoomIdentity);
        }}
        
        function toggleAnimation() {{
            animationEnabled = !animationEnabled;
            if (animationEnabled) {{
                simulation.restart();
            }} else {{
                simulation.stop();
            }}
        }}
        
        function highlightCore() {{
            node.style('opacity', d => d.isCore ? 1 : 0.1);
            link.style('opacity', 0.05);
            
            setTimeout(() => {{
                node.transition().duration(500).style('opacity', 1);
                link.transition().duration(500).style('opacity', 1);
            }}, 2000);
        }}
        
        window.addEventListener('resize', () => {{
            const newWidth = window.innerWidth;
            const newHeight = window.innerHeight;
            svg.attr('width', newWidth).attr('height', newHeight);
            simulation.force('center', d3.forceCenter(newWidth / 2, newHeight / 2));
            simulation.alpha(0.3).restart();
        }});
    </script>
</body>
</html>'''
    
    return html

# 主函数
def main():
    setup_page()
    
    # 左侧：搜索参数
    with st.sidebar:
        st.header("搜索参数")
        keywords = st.text_input("输入关键词", "genomic selection")
        max_results = st.slider("最大结果数", 5, 50, 20)
        search_button = st.button("搜索")
    
    # 右侧：搜索结果和可视化
    if search_button:
        with st.spinner("正在搜索PubMed..."):
            articles = search_pubmed(keywords, max_results)
        
        if not articles:
            st.error("未找到相关文献")
            return
        
        # 现代仪表板布局
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="status-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="status-value">{len(articles)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="status-label">文献总数</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            total_references = sum(article.get('References_Count', 0) for article in articles)
            st.markdown('<div class="status-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="status-value">{total_references}</div>', unsafe_allow_html=True)
            st.markdown('<div class="status-label">引用关系</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="status-card">', unsafe_allow_html=True)
            st.markdown('<div class="status-value">5</div>', unsafe_allow_html=True)
            st.markdown('<div class="status-label">核心文献</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 文献列表
        st.subheader("文献列表")
        for i, article in enumerate(articles, 1):
            with st.expander(f"文献 {i}: {article.get('Title', 'N/A')}"):
                st.write(f"**期刊**: {article.get('Journal', 'N/A')}")
                st.write(f"**年份**: {article.get('Year', 'N/A')}")
                st.write(f"**PMID**: {article.get('PMID', 'N/A')}")
                st.write(f"**作者**: {article.get('Authors', 'N/A')}")
                st.write(f"**引用数**: {article.get('References_Count', 0)}")
                st.write(f"**被引用数**: {article.get('Cited_By_Count', 0)}")
                topic = article.get('Topic', 'cropGenetics')
                st.write(f"**主题**: {TOPICS[topic]['name']}")
        
        # 引用网络
        st.subheader("引用网络")
        with st.spinner("正在构建引用网络..."):
            temp_file, core_pmids, paper_map = build_academic_citation_network(articles)
        
        # 显示网络
        with open(temp_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        st.components.v1.html(html_content, height=800)
        
        # 核心论文
        st.subheader("核心论文")
        if core_pmids:
            for i, pmid in enumerate(list(core_pmids)[:5], 1):
                paper = paper_map.get(pmid, {})
                st.write(f"**{i}. {paper.get('Title', 'N/A')}**")
                st.write(f"   期刊: {paper.get('Journal', 'N/A')}, 年份: {paper.get('Year', 'N/A')}, 被引用: {paper.get('Cited_By_Count', 0)} 次")
        else:
            st.write("未找到核心论文")

if __name__ == "__main__":
    main()