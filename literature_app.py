import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os
import json
import random

from pubmed_api import TOPICS, get_node_size, classify_topic, search_and_fetch
from network_template import generate_network_html

def setup_page():
    st.set_page_config(
        page_title="学术文献引用网络分析",
        layout="wide"
    )
    
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .main {
            background: #F5F7FA;
        }
        
        .stApp {
            background: #F5F7FA;
        }
        
        h1 {
            color: #333;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 24px;
        }
        
        h2 {
            color: #333;
            font-size: 20px;
            font-weight: 600;
            margin: 24px 0 16px 0;
        }
        
        h3 {
            color: #333;
            font-size: 16px;
            font-weight: 600;
            margin: 16px 0 8px 0;
        }
        
        h4 {
            color: #333;
            font-size: 14px;
            font-weight: 600;
            margin: 12px 0 4px 0;
        }
        
        p, span, div {
            color: #666;
            font-size: 14px;
            line-height: 1.5;
        }
        
        .stButton>button {
            background: #FFFFFF;
            border: 1px solid #E5E6EB;
            color: #333;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .stButton>button:hover {
            background: #F5F7FA;
            border-color: #165DFF;
            color: #165DFF;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(22, 93, 255, 0.15);
        }
        
        .stButton>button:active {
            transform: translateY(0);
        }
        
        .stTextInput>div>div>input {
            background: #FFFFFF;
            border: 1px solid #E5E6EB;
            color: #333;
            border-radius: 8px;
            padding: 10px 12px;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        
        .stTextInput>div>div>input:focus {
            border-color: #165DFF;
            box-shadow: 0 0 0 3px rgba(22, 93, 255, 0.1);
        }
        
        .stSlider>div>div>div>div {
            background: #FFFFFF;
            border: 1px solid #E5E6EB;
            border-radius: 4px;
        }
        
        .stSlider>div>div>div>div>div {
            background: #FFFFFF;
            border: 1px solid #E5E6EB;
            border-radius: 4px;
        }
        
        .stSlider>div>div>div>div>div:hover {
            background: #FFFFFF;
            border-color: #165DFF;
            box-shadow: 0 2px 6px rgba(22, 93, 255, 0.15);
        }
        
        div[data-testid="stExpander"] {
            background: #FFFFFF !important;
            border: 1px solid #E5E6EB !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
            margin: 12px 0 !important;
        }
        
        .stExpanderHeader {
            font-weight: 600 !important;
            color: #333 !important;
            font-size: 14px !important;
        }
        
        .stExpanderContent {
            background: #FFFFFF !important;
            padding: 16px !important;
        }
        
        .stSidebar {
            background: #FFFFFF;
            border-right: 1px solid #E5E6EB;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
        }
        
        .stSidebar > div:first-child {
            padding: 24px;
        }
        
        .stSidebar h2 {
            color: #333;
            font-size: 18px;
            font-weight: 600;
            margin: 0 0 16px 0;
        }
        
        .stSidebar p {
            color: #666;
            font-size: 14px;
            margin: 8px 0;
        }
        
        .stSidebar .stButton>button {
            width: 100%;
            margin-top: 16px;
        }
        
        .stMarkdown {
            color: #666 !important;
        }
        
        .element-container {
            margin: 8px 0;
        }
        
        label {
            color: #666 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
        }
        
        .core-paper {
            background: linear-gradient(135deg, rgba(22, 93, 255, 0.05), rgba(22, 93, 255, 0.05));
            border: 2px solid #165DFF;
            border-radius: 12px;
            padding: 20px;
            margin: 12px 0;
            box-shadow: 0 2px 8px rgba(22, 93, 255, 0.1);
            transition: all 0.3s ease;
        }
        
        .core-paper:hover {
            box-shadow: 0 4px 12px rgba(22, 93, 255, 0.15);
            transform: translateY(-2px);
        }
        
        .normal-paper {
            background: #FFFFFF;
            border: 1px solid #E5E6EB;
            border-radius: 12px;
            padding: 16px;
            margin: 12px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }
        
        .normal-paper:hover {
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
            transform: translateY(-1px);
        }
        
        .paper-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
            line-height: 1.4;
        }
        
        .paper-meta {
            font-size: 13px;
            color: #666;
            line-height: 1.5;
        }
        
        .citation-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 8px;
            background: #165DFF;
            color: white;
        }
        
        .topic-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            margin-top: 8px;
            margin-right: 6px;
            font-weight: 500;
            color: white;
        }
        
        .stInfo, .stSuccess, .stWarning, .stError {
            background: #FFFFFF !important;
            border: 1px solid #E5E6EB !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
            padding: 16px !important;
            margin: 12px 0 !important;
        }
        
        .stSpinner > div {
            border-top-color: #165DFF !important;
            border-width: 3px !important;
        }
        
        .card {
            background: #FFFFFF;
            border: 1px solid #E5E6EB;
            border-radius: 12px;
            padding: 20px;
            margin: 16px 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }
        
        .card-title {
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .card-content {
            color: #666;
            line-height: 1.5;
        }
        
        .feature-item {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            margin: 12px 0;
            padding: 12px;
            background: #F8F9FA;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .feature-item:hover {
            background: #F0F2F5;
            transform: translateX(4px);
        }
        
        .feature-icon {
            font-size: 20px;
            color: #165DFF;
            margin-top: 2px;
        }
        
        .feature-text {
            flex: 1;
        }
        
        .feature-text h4 {
            margin: 0 0 4px 0;
            font-size: 14px;
            font-weight: 600;
            color: #333;
        }
        
        .feature-text p {
            margin: 0;
            font-size: 13px;
            color: #666;
        }
    </style>
    """, unsafe_allow_html=True)


def build_network_data(articles):
    paper_map = {}
    for article in articles:
        pmid = article.get('PMID')
        if pmid:
            paper_map[pmid] = article
    
    nodes = []
    edges = []
    all_pmids = set(paper_map.keys())
    
    cited_counts = {}
    for pmid, paper in paper_map.items():
        cited_by = paper.get('Cited_By', [])
        for cited_pmid in cited_by:
            if cited_pmid in all_pmids:
                cited_counts[cited_pmid] = cited_counts.get(cited_pmid, 0) + 1
    
    for pmid, paper in paper_map.items():
        citations = paper.get('Cited_By_Count', 0)
        internal_citations = cited_counts.get(pmid, 0)
        total_score = citations + internal_citations * 5
        
        nodes.append({
            'id': pmid,
            'title': paper.get('Title', 'N/A'),
            'authors': paper.get('Authors', 'Unknown'),
            'year': paper.get('Year', 'N/A'),
            'citations': citations,
            'topic': paper.get('Topic', 'cropGenetics'),
            'isCore': False,
            'size': get_node_size(citations)
        })
    
    nodes_sorted = sorted(nodes, key=lambda x: x['citations'], reverse=True)
    core_pmids = set()
    for node in nodes_sorted[:min(5, len(nodes_sorted))]:
        core_pmids.add(node['id'])
    
    for node in nodes:
        node['isCore'] = node['id'] in core_pmids
    
    for pmid, paper in paper_map.items():
        references = paper.get('References', [])
        for ref_pmid in references:
            if ref_pmid in paper_map:
                edges.append({
                    'source': pmid,
                    'target': ref_pmid,
                    'strength': 0.5
                })
        
        cited_by = paper.get('Cited_By', [])
        for cite_pmid in cited_by:
            if cite_pmid in paper_map:
                edge_exists = any(
                    (e['source'] == cite_pmid and e['target'] == pmid) or
                    (e['source'] == pmid and e['target'] == cite_pmid)
                    for e in edges
                )
                if not edge_exists:
                    edges.append({
                        'source': cite_pmid,
                        'target': pmid,
                        'strength': 0.6
                    })
    
    return nodes, edges, core_pmids

def render_paper_card(article, is_core=False, topic_info_list=None):
    css_class = "core-paper" if is_core else "normal-paper"
    title = article.get('Title', 'N/A')
    authors = article.get('Authors', 'Unknown')
    year = article.get('Year', 'N/A')
    journal = article.get('Journal', 'N/A')
    pmid = article.get('PMID', 'N/A')
    citations = article.get('Cited_By_Count', 0)
    self_citations = article.get('Self_Citations', 0)
    other_citations = article.get('Other_Citations', 0)
    topics = article.get('Topics', [article.get('Topic', 'cropGenetics')])
    
    if topic_info_list is None:
        topic_info_list = []
        for topic_key in topics:
            topic_info_list.append(TOPICS.get(topic_key, {'name': '其他', 'color': '#888888'}))
    
    core_badge = '<span class="citation-badge" style="background: #FFD93D; color: #000;">核心文献</span>' if is_core else ''
    
    topic_badges = ''
    for topic_info in topic_info_list:
        topic_badges += f'<span class="topic-badge" style="background: {topic_info["color"]}; color: #000;">{topic_info["name"]}</span>'
    
    citation_level = ''
    if citations >= 50:
        citation_level = '<span style="color:#F53F3F;font-weight:600;">高被引</span>'
    elif citations >= 20:
        citation_level = '<span style="color:#F7BA1E;font-weight:600;">中高被引</span>'
    elif citations >= 10:
        citation_level = '<span style="color:#0FC6C2;font-weight:600;">有效被引</span>'
    
    html = f'''
    <div class="{css_class}">
        <div class="paper-title">{title}{core_badge}</div>
        <div class="paper-meta">
            <strong>作者:</strong> {authors}<br>
            <strong>期刊:</strong> {journal}<br>
            <strong>年份:</strong> {year} | <strong>PMID:</strong> {pmid}<br>
            <strong>总被引:</strong> {citations} ({citation_level}) | <strong>自引:</strong> {self_citations} | <strong>他引:</strong> {other_citations}
        </div>
        {topic_badges}
    </div>
    '''
    return html

def main():
    setup_page()
    
    st.title("学术文献引用网络分析")
    st.markdown("---")
    
    with st.sidebar:
        st.header("搜索设置")
        keywords = st.text_input(
            "输入搜索关键词",
            placeholder="例如: genomic selection breeding 或 author:Zhang gene:BRCA1",
            help="支持：关键词、author:作者名、gene:基因名等精确搜索"
        )
        
        max_results = st.slider(
            "最大文献数量",
            min_value=5,
            max_value=50,
            value=20,
            step=5
        )
        
        search_btn = st.button("开始搜索", use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 研究主题图例")
        for topic_key, topic_info in TOPICS.items():
            st.markdown(
                f'<div style="display:flex;align-items:center;margin:8px 0;">'
                f'<div style="width:16px;height:16px;border-radius:50%;background:{topic_info["color"]};margin-right:10px;"></div>'
                f'<span style="color:#000000;">{topic_info["name"]}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
    
    if 'articles' not in st.session_state:
        st.session_state.articles = []
    if 'core_pmids' not in st.session_state:
        st.session_state.core_pmids = set()
    
    if search_btn:
        with st.spinner("正在调用 PubMed API 搜索文献..."):
            try:
                if not keywords:
                    st.warning("请输入搜索关键词！")
                else:
                    articles = search_and_fetch(keywords, max_results=max_results)
                    if articles:
                        st.session_state.articles = articles
                        _, _, core_pmids = build_network_data(articles)
                        st.session_state.core_pmids = core_pmids
                        st.success(f"成功获取 {len(articles)} 篇文献！")
                    else:
                        st.warning("未找到匹配的文献。")
            except Exception as e:
                st.error(f"搜索出错: {str(e)}")
    
    articles = st.session_state.articles
    core_pmids = st.session_state.core_pmids
    
    if articles:
        st.subheader("文献列表")
        
        core_articles = [a for a in articles if a.get('PMID') in core_pmids]
        other_articles = [a for a in articles if a.get('PMID') not in core_pmids]
        
        if core_articles:
            st.markdown("#### 核心文献（高被引）")
            for article in core_articles:
                topic_keys = article.get('Topics', [article.get('Topic', 'cropGenetics')])
                topic_info_list = [TOPICS.get(tk, {'name': '其他', 'color': '#888888'}) for tk in topic_keys]
                st.markdown(render_paper_card(article, is_core=True, topic_info_list=topic_info_list), unsafe_allow_html=True)
        
        if other_articles:
            with st.expander("查看其他文献", expanded=False):
                for article in other_articles:
                    topic_keys = article.get('Topics', [article.get('Topic', 'cropGenetics')])
                    topic_info_list = [TOPICS.get(tk, {'name': '其他', 'color': '#888888'}) for tk in topic_keys]
                    st.markdown(render_paper_card(article, is_core=False, topic_info_list=topic_info_list), unsafe_allow_html=True)
        
        st.subheader("引用网络可视化")
        
        nodes, edges, _ = build_network_data(articles)
        
        if nodes:
            node_count = len(nodes)
            edge_count = len(edges)
            core_count = len([n for n in nodes if n['isCore']])
            
            html_content = generate_network_html(nodes, edges, node_count, edge_count, core_count)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file = f.name
            
            try:
                with open(temp_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                components.html(html_content, height=700, scrolling=False)
            finally:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
        else:
            st.info("暂无网络数据")
    else:
        st.markdown("""
        <div class="card">
            <div class="card-title">使用说明</div>
            <div class="card-content">
                <div class="feature-item">
                    <div class="feature-icon">1</div>
                    <div class="feature-text">
                        <h4>输入关键词</h4>
                        <p>支持：普通关键词、author:作者名、gene:基因名等精确搜索</p>
                    </div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">2</div>
                    <div class="feature-text">
                        <h4>设置数量</h4>
                        <p>调整滑块选择要获取的文献数量（5-50篇）</p>
                    </div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">3</div>
                    <div class="feature-text">
                        <h4>开始搜索</h4>
                        <p>点击"开始搜索"按钮，系统会自动调用PubMed API获取文献数据</p>
                    </div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">4</div>
                    <div class="feature-text">
                        <h4>查看结果</h4>
                        <p>左侧显示文献列表，核心文献会高亮显示；右侧显示引用网络可视化图</p>
                    </div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">5</div>
                    <div class="feature-text">
                        <h4>交互操作</h4>
                        <p>鼠标悬停查看文献详情，点击节点高亮相关连接，使用底部按钮重置视图或高亮核心文献</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-title">功能特点</div>
            <div class="card-content">
                <div class="feature-item">
                    <div class="feature-icon">●</div>
                    <div class="feature-text">
                        <h4>自动调用PubMed API</h4>
                        <p>实时获取最新的学术文献数据</p>
                    </div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">●</div>
                    <div class="feature-text">
                        <h4>真实引用数据</h4>
                        <p>从PubMed获取真实被引数据，区分自引和他引</p>
                    </div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">●</div>
                    <div class="feature-text">
                        <h4>智能识别核心论文</h4>
                        <p>基于被引次数自动识别高影响力文献</p>
                    </div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">●</div>
                    <div class="feature-text">
                        <h4>多主题标签</h4>
                        <p>支持一篇文献多个主题分类标签</p>
                    </div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">●</div>
                    <div class="feature-text">
                        <h4>交互式网络可视化</h4>
                        <p>使用D3.js实现流畅的力导向图交互效果</p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
