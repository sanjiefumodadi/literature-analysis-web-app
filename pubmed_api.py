import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time
import re

# 设置 NCBI API 调用的邮箱地址
Entrez_email = "904304877@qq.com"

PUBMED_API_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

TOPICS = {
    'genomicSelection': {'name': '基因组选择', 'color': '#722ED1'},
    'aiBreeding': {'name': '人工智能育种', 'color': '#0FC6C2'},
    'cropGenetics': {'name': '作物遗传改良', 'color': '#F7BA1E'},
    'molecularMarker': {'name': '分子标记辅助', 'color': '#F53F3F'},
    'quantitativeGenetics': {'name': '数量遗传学', 'color': '#86909C'},
    'other': {'name': '其他领域', 'color': '#999999'}
}

def classify_topic(title):
    """学术级精准分类函数 - 优化版"""
    # 空值安全处理
    if not title or not isinstance(title, str):
        return 'other'
    
    title_lower = title.lower()
    
    # 长关键词优先匹配，按优先级排序（避免子串误判）
    
    # 1. 基因组选择（最高优先级）
    genomic_selection_keywords = [
        'genomic selection', 'genomic prediction', 'genomic estimated breeding value',
        'gebv', 'gblup', 'rrblup', 'bayesian', '基因组选择', '基因组预测', '基因组估计育种值'
    ]
    if any(kw in title_lower for kw in genomic_selection_keywords):
        return 'genomicSelection'
    
    # 2. AI育种/机器学习（避免短词匹配）
    ai_keywords = [
        'artificial intelligence', 'machine learning', 'deep learning', 
        'neural network', 'random forest', 'support vector machine', 'svm',
        'convolutional neural network', 'cnn', 'recurrent neural network', 'rnn',
        '人工智能', '深度学习', '机器学习', '神经网络', '随机森林', '支持向量机'
    ]
    if any(kw in title_lower for kw in ai_keywords):
        return 'aiBreeding'
    
    # 3. 分子标记辅助（在作物遗传改良之前，避免被拦截）
    marker_keywords = [
        'molecular marker', 'ssr marker', 'snp marker', 'indel', 'rapd', 'aflp',
        'genome-wide association', 'gwas', 'linkage mapping', 'qtl mapping',
        'association mapping', 'marker-assisted', 'mas', '分子标记', '全基因组关联'
    ]
    if any(kw in title_lower for kw in marker_keywords):
        return 'molecularMarker'
    
    # 4. 数量遗传学（在作物遗传改良之前）
    quantitative_keywords = [
        'quantitative trait', 'qtl', 'quantitative genetics', 'heritability',
        'genetic variance', 'additive effect', 'dominance', 'epistasis',
        'blup', 'best linear unbiased prediction', '数量遗传', '遗传力', '数量性状'
    ]
    if any(kw in title_lower for kw in quantitative_keywords):
        return 'quantitativeGenetics'
    
    # 5. 作物遗传改良（更广泛的农业关键词）
    crop_keywords = [
        'rice', 'wheat', 'soybean', 'maize', 'corn', 'barley', 'oats', 'sorghum',
        'crop', 'cultivar', 'variety', 'breeding', 'hybrid', 'inbred line',
        'plant', 'agronomic trait', 'yield', 'drought tolerance', 'salt stress',
        'disease resistance', 'pest resistance', '作物', '产量', '遗传改良',
        '玉米', '小麦', '水稻', '大豆', '品种', '育种', '杂交', '抗旱', '耐盐'
    ]
    if any(kw in title_lower for kw in crop_keywords):
        return 'cropGenetics'
    
    # 6. 其他领域（默认分类）
    return 'other'

def search_pubmed(keywords, max_results=20):
    """稳定、合规的PubMed搜索函数"""
    encoded_terms = urllib.parse.quote(keywords)
    # 新增年份过滤：2018/01/01 到 2023/12/31
    esearch_url = f"{PUBMED_API_URL}esearch.fcgi?db=pubmed&term={encoded_terms}&retmax={max_results}&sort=pub_date&mindate=2018/01/01&maxdate=2023/12/31&email={Entrez_email}"
    
    # 网络重试机制
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(esearch_url, timeout=30) as response:
                content = response.read()
            break
        except Exception as e:
            print(f"搜索请求失败 (尝试 {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                # 指数退避重试
                sleep_time = 2 ** attempt
                print(f"{sleep_time}秒后重试...")
                time.sleep(sleep_time)
            else:
                # 最后一次尝试失败，返回空列表
                print("搜索请求最终失败，返回空结果")
                return []
    
    try:
        tree = ET.ElementTree(ET.fromstring(content))
        root = tree.getroot()
        
        ids = []
        for id_elem in root.findall('.//Id'):
            ids.append(id_elem.text)
        
        if not ids:
            return []
        
        # NCBI 合规限流
        time.sleep(0.4)
        return ids
    except Exception as e:
        print(f"解析搜索结果失败: {str(e)}")
        return []

def fetch_article_details(ids):
    """鲁棒性、空值安全的文献详情获取函数"""
    if not ids:
        return []
    
    id_string = ",".join(ids)
    fetch_url = f"{PUBMED_API_URL}efetch.fcgi?db=pubmed&id={id_string}&retmode=xml&email={Entrez_email}"
    
    # 网络重试机制
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(fetch_url, timeout=60) as fetch_response:
                fetch_content = fetch_response.read()
            break
        except Exception as e:
            print(f"获取文献详情失败 (尝试 {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                # 指数退避重试
                sleep_time = 2 ** attempt
                print(f"{sleep_time}秒后重试...")
                time.sleep(sleep_time)
            else:
                # 最后一次尝试失败，返回空列表
                print("获取文献详情最终失败，返回空结果")
                return []
    
    try:
        fetch_tree = ET.ElementTree(ET.fromstring(fetch_content))
        fetch_root = fetch_tree.getroot()
        
        articles = []
        for pubmed_article in fetch_root.findall('.//PubmedArticle'):
            try:
                article_info = extract_article_info(pubmed_article)
                if article_info:
                    articles.append(article_info)
            except Exception as e:
                print(f"处理单篇文献失败: {str(e)}")
                continue
        
        # 限流处理
        time.sleep(0.5)
        return articles
    except Exception as e:
        print(f"解析文献详情失败: {str(e)}")
        return []

def extract_article_info(pubmed_article):
    """鲁棒性的文献信息提取函数"""
    article_info = {}
    
    medline_citation = pubmed_article.find('MedlineCitation')
    if medline_citation is None:
        return None
    
    article = medline_citation.find('Article')
    if article is None:
        return None
    
    # 标题提取
    article_title = article.find('ArticleTitle')
    if article_title is not None and article_title.text:
        article_info['Title'] = article_title.text
    else:
        article_info['Title'] = 'Unknown'
    
    # 期刊提取
    journal = article.find('Journal')
    if journal is not None:
        journal_title = journal.find('Title')
        if journal_title is not None and journal_title.text:
            article_info['Journal'] = journal_title.text
        else:
            article_info['Journal'] = 'Unknown'
    else:
        article_info['Journal'] = 'Unknown'
    
    # 年份提取
    year = None
    pub_date = article.find('PubDate')
    if pub_date is not None:
        year_elem = pub_date.find('Year')
        if year_elem is not None and year_elem.text:
            year = year_elem.text
    
    if not year and journal is not None:
        journal_issue = journal.find('JournalIssue')
        if journal_issue is not None:
            pub_date = journal_issue.find('PubDate')
            if pub_date is not None:
                year_elem = pub_date.find('Year')
                if year_elem is not None and year_elem.text:
                    year = year_elem.text
    
    article_info['Year'] = year if year else 'Unknown'
    
    # PMID提取
    pmid = medline_citation.find('PMID')
    if pmid is not None and pmid.text:
        article_info['PMID'] = pmid.text
    else:
        article_info['PMID'] = 'Unknown'
    
    # 作者提取
    author_list = article.find('AuthorList')
    if author_list is not None:
        authors = []
        for author in author_list.findall('Author'):
            last_name = author.find('LastName')
            fore_name = author.find('ForeName')
            if last_name is not None and last_name.text:
                author_name = last_name.text
                if fore_name is not None and fore_name.text:
                    author_name = f"{last_name.text} {fore_name.text[0] if fore_name.text else ''}"
                authors.append(author_name)
        
        if authors:
            if len(authors) > 3:
                article_info['Authors'] = ', '.join(authors[:3]) + ' et al.'
            else:
                article_info['Authors'] = ', '.join(authors)
        else:
            article_info['Authors'] = 'Unknown'
    else:
        article_info['Authors'] = 'Unknown'
    
    # 主题分类
    article_info['Topic'] = classify_topic(article_info.get('Title', ''))
    
    return article_info

def get_citation_info(pmid):
    """合规、稳定的引用统计函数"""
    references = []
    cited_by = []
    citation_count = 0
    
    # 优先使用 esummary API 获取官方统计的被引数
    try:
        summary_url = f"{PUBMED_API_URL}esummary.fcgi?db=pubmed&id={pmid}&email={Entrez_email}"
        with urllib.request.urlopen(summary_url, timeout=30) as summary_response:
            summary_content = summary_response.read()
        
        summary_tree = ET.ElementTree(ET.fromstring(summary_content))
        summary_root = summary_tree.getroot()
        
        for docsum in summary_root.findall('.//DocSum'):
            for item in docsum.findall('.//Item'):
                if item.get('Name') == 'Cited':
                    if item.text:
                        citation_count = int(item.text)
                    break
        # 限流
        time.sleep(0.4)
    except Exception as e:
        print(f"获取引用计数失败 (PMID: {pmid}): {str(e)}")
    
    # 获取引用的文献
    try:
        ref_url = f"{PUBMED_API_URL}elink.fcgi?dbfrom=pubmed&db=pubmed&id={pmid}&linkname=pubmed_pubmed_refs&email={Entrez_email}"
        with urllib.request.urlopen(ref_url, timeout=30) as ref_response:
            ref_content = ref_response.read()
        
        ref_tree = ET.ElementTree(ET.fromstring(ref_content))
        ref_root = ref_tree.getroot()
        
        for linkset in ref_root.findall('.//LinkSet'):
            for linksetdb in linkset.findall('.//LinkSetDb'):
                if linksetdb.get('LinkName') == 'pubmed_pubmed_refs':
                    for link in linksetdb.findall('.//Link'):
                        ref_id = link.find('Id')
                        if ref_id is not None and ref_id.text:
                            references.append(ref_id.text)
        # 限流
        time.sleep(0.4)
    except Exception as e:
        print(f"获取参考文献失败 (PMID: {pmid}): {str(e)}")
    
    # 获取被引用的文献
    try:
        cited_url = f"{PUBMED_API_URL}elink.fcgi?dbfrom=pubmed&db=pubmed&id={pmid}&linkname=pubmed_pubmed_citedin&email={Entrez_email}"
        with urllib.request.urlopen(cited_url, timeout=30) as cited_response:
            cited_content = cited_response.read()
        
        cited_tree = ET.ElementTree(ET.fromstring(cited_content))
        cited_root = cited_tree.getroot()
        
        for linkset in cited_root.findall('.//LinkSet'):
            for linksetdb in linkset.findall('.//LinkSetDb'):
                if linksetdb.get('LinkName') == 'pubmed_pubmed_citedin':
                    for link in linksetdb.findall('.//Link'):
                        cited_id = link.find('Id')
                        if cited_id is not None and cited_id.text:
                            cited_by.append(cited_id.text)
        # 限流
        time.sleep(0.4)
    except Exception as e:
        print(f"获取被引用文献失败 (PMID: {pmid}): {str(e)}")
    
    # 如果通过 esummary API 获取到了被引数，返回它，否则使用链接解析的数量
    if citation_count > 0:
        return references[:15], cited_by[:15], citation_count
    else:
        return references[:15], cited_by[:15], len(cited_by)

def search_and_fetch(keywords, max_results=20, get_citations=True):
    """主流程优化函数"""
    print(f"开始搜索关键词: {keywords}")
    ids = search_pubmed(keywords, max_results)
    print(f"搜索到 {len(ids)} 篇文献")
    
    if not ids:
        return []
    
    articles = fetch_article_details(ids)
    print(f"成功获取 {len(articles)} 篇文献详情")
    
    if get_citations:
        print("开始获取引用信息...")
        for i, article in enumerate(articles):
            pmid = article.get('PMID')
            if pmid and pmid != 'Unknown':
                try:
                    references, cited_by, citation_count = get_citation_info(pmid)
                    article['References'] = references
                    article['References_Count'] = len(references)
                    article['Cited_By'] = cited_by
                    article['Cited_By_Count'] = citation_count
                except Exception as e:
                    print(f"获取引用信息失败 (PMID: {pmid}): {str(e)}")
                    # 为失败的条目设置默认值
                    article['References'] = []
                    article['References_Count'] = 0
                    article['Cited_By'] = []
                    article['Cited_By_Count'] = 0
            else:
                # 为无PMID的条目设置默认值
                article['References'] = []
                article['References_Count'] = 0
                article['Cited_By'] = []
                article['Cited_By_Count'] = 0
            
            # 限流优化
            time.sleep(0.5)
    
    # 严格过滤逻辑：仅保留被引次数≥100的高影响力文献
    filtered_articles = []
    if get_citations and articles:
        for article in articles:
            citation_count = article.get('Cited_By_Count', 0)
            # 严格标准：被引数必须≥100
            if isinstance(citation_count, int) and citation_count >= 100:
                filtered_articles.append(article)
            elif isinstance(citation_count, str):
                try:
                    if int(citation_count) >= 100:
                        filtered_articles.append(article)
                except ValueError:
                    pass
    elif not get_citations:
        # 如果不获取引用信息，则不过滤
        filtered_articles = articles
    
    print(f"严格过滤后剩余 {len(filtered_articles)} 篇高影响力文献（被引≥100次）")
    return filtered_articles

def get_node_size(citations):
    """可视化适配优化函数"""
    # 类型安全和空值处理
    try:
        if not citations:
            return 7
        if not isinstance(citations, int):
            citations = int(citations)
        
        # 优化节点大小梯度
        if citations > 200:
            return 30
        elif citations > 100:
            return 25
        elif citations > 50:
            return 20
        elif citations > 20:
            return 15
        elif citations > 10:
            return 12
        else:
            return 7
    except (ValueError, TypeError):
        return 7
