import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time
import re
import datetime

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

TOPIC_KEYWORDS = {
    'genomicSelection': [
        'genomic selection', 'genomic prediction', 'genomic estimated breeding value',
        'gebv', 'gblup', 'rrblup', 'bayesian', '基因组选择', '基因组预测', '基因组估计育种值'
    ],
    'aiBreeding': [
        'artificial intelligence', 'machine learning', 'deep learning', 
        'neural network', 'random forest', 'support vector machine', 'svm',
        'convolutional neural network', 'cnn', 'recurrent neural network', 'rnn',
        '人工智能', '深度学习', '机器学习', '神经网络', '随机森林', '支持向量机'
    ],
    'molecularMarker': [
        'molecular marker', 'ssr marker', 'snp marker', 'indel', 'rapd', 'aflp',
        'genome-wide association', 'gwas', 'linkage mapping', 'qtl mapping',
        'association mapping', 'marker-assisted', 'mas', '分子标记', '全基因组关联'
    ],
    'quantitativeGenetics': [
        'quantitative trait', 'qtl', 'quantitative genetics', 'heritability',
        'genetic variance', 'additive effect', 'dominance', 'epistasis',
        'blup', 'best linear unbiased prediction', '数量遗传', '遗传力', '数量性状'
    ],
    'cropGenetics': [
        'rice', 'wheat', 'soybean', 'maize', 'corn', 'barley', 'oats', 'sorghum',
        'crop', 'cultivar', 'variety', 'breeding', 'hybrid', 'inbred line',
        'plant', 'agronomic trait', 'yield', 'drought tolerance', 'salt stress',
        'disease resistance', 'pest resistance', '作物', '产量', '遗传改良',
        '玉米', '小麦', '水稻', '大豆', '品种', '育种', '杂交', '抗旱', '耐盐'
    ]
}

def classify_topic(title, abstract=None):
    topics = []
    if not title or not isinstance(title, str):
        return ['other']
    
    text = title.lower()
    if abstract and isinstance(abstract, str):
        text += ' ' + abstract.lower()
    
    for topic_key, keywords in TOPIC_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            topics.append(topic_key)
    
    if not topics:
        topics = ['other']
    
    return topics

def build_search_query(keywords):
    current_year = datetime.datetime.now().year
    start_year = current_year - 10
    end_year = current_year - 1
    
    date_filter = f"{start_year}/01/01[PDAT] : {end_year}/12/31[PDAT]"
    
    keywords_lower = keywords.lower()
    
    query_parts = []
    
    author_pattern = r'(?:author|作者)[:\s]+([^,]+)'
    author_match = re.search(author_pattern, keywords_lower)
    if author_match:
        author_name = author_match.group(1).strip()
        query_parts.append(f"({author_name}[Author])")
        keywords = keywords.replace(author_match.group(0), '').strip()
    
    gene_pattern = r'(?:gene|基因)[:\s]+([\w\-]+)'
    gene_match = re.search(gene_pattern, keywords_lower)
    if gene_match:
        gene_name = gene_match.group(1).strip()
        query_parts.append(f"({gene_name}[Gene Name] OR {gene_name}[Title/Abstract])")
        keywords = keywords.replace(gene_match.group(0), '').strip()
    
    if keywords.strip():
        query_parts.append(f"({keywords.strip()}[Title/Abstract])")
    
    if not query_parts:
        query_parts = [f"({keywords}[Title/Abstract])"]
    
    main_query = ' AND '.join(query_parts)
    final_query = f"({main_query}) AND ({date_filter})"
    
    return final_query

def search_pubmed(keywords, max_results=20):
    combined_query = build_search_query(keywords)
    print(f"搜索查询: {combined_query}")
    
    encoded_query = urllib.parse.quote(combined_query)
    esearch_url = f"{PUBMED_API_URL}esearch.fcgi?db=pubmed&term={encoded_query}&retmax={max_results}&sort=cited&email={Entrez_email}"
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(esearch_url, timeout=30) as response:
                content = response.read()
            break
        except Exception as e:
            print(f"搜索请求失败 (尝试 {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt
                print(f"{sleep_time}秒后重试...")
                time.sleep(sleep_time)
            else:
                print("搜索请求最终失败，返回空结果")
                return []
    
    try:
        tree = ET.ElementTree(ET.fromstring(content))
        root = tree.getroot()
        
        ids = []
        for id_elem in root.findall('.//Id'):
            ids.append(id_elem.text)
        
        if not ids:
            print("未找到匹配文献")
            return []
        
        time.sleep(0.4)
        print(f"找到 {len(ids)} 篇文献")
        return ids
    except Exception as e:
        print(f"解析搜索结果失败: {str(e)}")
        return []

def fetch_article_details(ids):
    if not ids:
        return []
    
    id_string = ",".join(ids)
    fetch_url = f"{PUBMED_API_URL}efetch.fcgi?db=pubmed&id={id_string}&retmode=xml&email={Entrez_email}"
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(fetch_url, timeout=60) as fetch_response:
                fetch_content = fetch_response.read()
            break
        except Exception as e:
            print(f"获取文献详情失败 (尝试 {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt
                print(f"{sleep_time}秒后重试...")
                time.sleep(sleep_time)
            else:
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
        
        time.sleep(0.5)
        return articles
    except Exception as e:
        print(f"解析文献详情失败: {str(e)}")
        return []

def extract_article_info(pubmed_article):
    article_info = {}
    
    medline_citation = pubmed_article.find('MedlineCitation')
    if medline_citation is None:
        return None
    
    article = medline_citation.find('Article')
    if article is None:
        return None
    
    article_title = article.find('ArticleTitle')
    if article_title is not None and article_title.text:
        article_info['Title'] = article_title.text
    else:
        article_info['Title'] = 'Unknown'
    
    abstract_text = ''
    abstract = article.find('Abstract')
    if abstract is not None:
        abstract_parts = []
        for abs_text in abstract.findall('.//AbstractText'):
            if abs_text.text:
                abstract_parts.append(abs_text.text)
        abstract_text = ' '.join(abstract_parts)
    article_info['Abstract'] = abstract_text
    
    journal = article.find('Journal')
    if journal is not None:
        journal_title = journal.find('Title')
        if journal_title is not None and journal_title.text:
            article_info['Journal'] = journal_title.text
        else:
            article_info['Journal'] = 'Unknown'
    else:
        article_info['Journal'] = 'Unknown'
    
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
    
    pmid = medline_citation.find('PMID')
    if pmid is not None and pmid.text:
        article_info['PMID'] = pmid.text
    else:
        article_info['PMID'] = 'Unknown'
    
    author_list = article.find('AuthorList')
    authors = []
    authors_full = []
    first_author_lastname = None
    all_author_lastnames = []
    
    if author_list is not None:
        for author in author_list.findall('Author'):
            last_name = author.find('LastName')
            fore_name = author.find('ForeName')
            if last_name is not None and last_name.text:
                author_name = last_name.text
                if fore_name is not None and fore_name.text:
                    author_name = f"{last_name.text} {fore_name.text[0] if fore_name.text else ''}"
                authors.append(author_name)
                authors_full.append(author_name)
                all_author_lastnames.append(last_name.text.lower())
                if first_author_lastname is None:
                    first_author_lastname = last_name.text.lower()
        
        if authors:
            if len(authors) > 3:
                article_info['Authors'] = ', '.join(authors[:3]) + ' et al.'
            else:
                article_info['Authors'] = ', '.join(authors)
        else:
            article_info['Authors'] = 'Unknown'
    else:
        article_info['Authors'] = 'Unknown'
    
    article_info['Authors_Full'] = authors_full
    article_info['First_Author_Lastname'] = first_author_lastname
    article_info['All_Author_Lastnames'] = all_author_lastnames
    
    article_info['Topics'] = classify_topic(article_info.get('Title', ''), article_info.get('Abstract', ''))
    article_info['Topic'] = article_info['Topics'][0]
    
    return article_info

def calculate_self_other_citations(article, cited_by_pmids, all_articles_map):
    self_citation_count = 0
    other_citation_count = 0
    
    if not cited_by_pmids:
        return 0, 0
    
    article_authors = article.get('All_Author_Lastnames', [])
    first_author = article.get('First_Author_Lastname', '')
    
    if not article_authors:
        return 0, len(cited_by_pmids)
    
    for cited_pmid in cited_by_pmids:
        if cited_pmid in all_articles_map:
            citing_article = all_articles_map[cited_pmid]
            citing_authors = citing_article.get('All_Author_Lastnames', [])
            
            if citing_authors:
                has_overlap = False
                for citing_author in citing_authors:
                    if citing_author in article_authors:
                        has_overlap = True
                        break
                
                if has_overlap:
                    self_citation_count += 1
                else:
                    other_citation_count += 1
            else:
                other_citation_count += 1
        else:
            other_citation_count += 1
    
    return self_citation_count, other_citation_count

def get_citation_info(pmid, article=None, all_articles_map=None):
    references = []
    cited_by = []
    citation_count = 0
    
    try:
        summary_url = f"{PUBMED_API_URL}esummary.fcgi?db=pubmed&id={pmid}&email={Entrez_email}"
        with urllib.request.urlopen(summary_url, timeout=30) as summary_response:
            summary_content = summary_response.read()
        
        summary_tree = ET.ElementTree(ET.fromstring(summary_content))
        summary_root = summary_tree.getroot()
        
        for docsum in summary_root.findall('.//DocSum'):
            for item in docsum.findall('.//Item'):
                if item.get('Name') == 'PmcRefCount':
                    if item.text:
                        try:
                            citation_count = int(item.text)
                        except ValueError:
                            pass
                elif item.get('Name') == 'Cited':
                    if item.text and citation_count == 0:
                        try:
                            citation_count = int(item.text)
                        except ValueError:
                            pass
        
        time.sleep(0.3)
    except Exception as e:
        print(f"获取引用计数失败 (PMID: {pmid}): {str(e)}")
    
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
        
        if citation_count == 0:
            citation_count = len(cited_by)
        
        time.sleep(0.3)
    except Exception as e:
        print(f"获取被引用文献失败 (PMID: {pmid}): {str(e)}")
    
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
        
        time.sleep(0.3)
    except Exception as e:
        print(f"获取参考文献失败 (PMID: {pmid}): {str(e)}")
    
    self_citation_count = 0
    other_citation_count = 0
    
    if article and all_articles_map:
        self_citation_count, other_citation_count = calculate_self_other_citations(
            article, cited_by, all_articles_map
        )
    else:
        if citation_count > 0:
            other_citation_count = citation_count
    
    return references[:15], cited_by[:15], citation_count, self_citation_count, other_citation_count

def search_and_fetch(keywords, max_results=20, get_citations=True):
    print(f"开始搜索关键词: {keywords}")
    ids = search_pubmed(keywords, max_results)
    
    if not ids:
        return []
    
    articles = fetch_article_details(ids)
    print(f"成功获取 {len(articles)} 篇文献详情")
    
    all_articles_map = {a.get('PMID'): a for a in articles if a.get('PMID')}
    
    if get_citations:
        print("开始获取引用信息...")
        for i, article in enumerate(articles):
            pmid = article.get('PMID')
            if pmid and pmid != 'Unknown':
                try:
                    references, cited_by, citation_count, self_citations, other_citations = get_citation_info(
                        pmid, article, all_articles_map
                    )
                    article['References'] = references
                    article['References_Count'] = len(references)
                    article['Cited_By'] = cited_by
                    article['Cited_By_Count'] = citation_count
                    article['Self_Citations'] = self_citations
                    article['Other_Citations'] = other_citations
                except Exception as e:
                    print(f"获取引用信息失败 (PMID: {pmid}): {str(e)}")
                    article['References'] = []
                    article['References_Count'] = 0
                    article['Cited_By'] = []
                    article['Cited_By_Count'] = 0
                    article['Self_Citations'] = 0
                    article['Other_Citations'] = 0
            else:
                article['References'] = []
                article['References_Count'] = 0
                article['Cited_By'] = []
                article['Cited_By_Count'] = 0
                article['Self_Citations'] = 0
                article['Other_Citations'] = 0
            
            time.sleep(0.2)
    
    if get_citations and articles:
        articles.sort(key=lambda x: x.get('Cited_By_Count', 0), reverse=True)
    
    print(f"最终返回 {len(articles)} 篇文献")
    return articles

def get_citation_level(citations):
    if citations >= 50:
        return 'high', '高被引', '#F53F3F'
    elif citations >= 20:
        return 'medium_high', '中高被引', '#F7BA1E'
    elif citations >= 10:
        return 'valid', '有效被引', '#0FC6C2'
    else:
        return 'low', '无被引', '#86909C'

def get_node_size(citations):
    try:
        if not citations:
            return 7
        if not isinstance(citations, int):
            citations = int(citations)
        
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
