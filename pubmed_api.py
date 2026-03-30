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
    'quantitativeGenetics': {'name': '数量遗传学', 'color': '#86909C'}
}

def classify_topic(title):
    if not title:
        return 'cropGenetics'
    title_lower = title.lower()
    if any(kw in title_lower for kw in ['genomic selection', 'genomic', 'gs ', '基因组选择']):
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
        return 'cropGenetics'

def search_pubmed(keywords, max_results=20):
    encoded_terms = urllib.parse.quote(keywords)
    esearch_url = f"{PUBMED_API_URL}esearch.fcgi?db=pubmed&term={encoded_terms}&retmax={max_results}&sort=cited&email={Entrez_email}"
    
    try:
        with urllib.request.urlopen(esearch_url, timeout=30) as response:
            content = response.read()
    except Exception as e:
        raise Exception(f"搜索请求失败: {str(e)}")
    
    tree = ET.ElementTree(ET.fromstring(content))
    root = tree.getroot()
    
    ids = []
    for id_elem in root.findall('.//Id'):
        ids.append(id_elem.text)
    
    if not ids:
        return []
    
    return ids

def fetch_article_details(ids):
    if not ids:
        return []
    
    id_string = ",".join(ids)
    fetch_url = f"{PUBMED_API_URL}efetch.fcgi?db=pubmed&id={id_string}&retmode=xml&email={Entrez_email}"
    
    try:
        with urllib.request.urlopen(fetch_url, timeout=60) as fetch_response:
            fetch_content = fetch_response.read()
    except Exception as e:
        raise Exception(f"获取文献详情失败: {str(e)}")
    
    fetch_tree = ET.ElementTree(ET.fromstring(fetch_content))
    fetch_root = fetch_tree.getroot()
    
    articles = []
    for pubmed_article in fetch_root.findall('.//PubmedArticle'):
        article_info = extract_article_info(pubmed_article)
        if article_info:
            articles.append(article_info)
    
    return articles

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
        return None
    
    journal = article.find('Journal')
    if journal is not None:
        journal_title = journal.find('Title')
        if journal_title is not None:
            article_info['Journal'] = journal_title.text
    
    pub_date = article.find('PubDate')
    if pub_date is not None:
        year = pub_date.find('Year')
        if year is not None:
            article_info['Year'] = year.text
    
    if 'Year' not in article_info:
        if journal is not None:
            journal_issue = journal.find('JournalIssue')
            if journal_issue is not None:
                pub_date = journal_issue.find('PubDate')
                if pub_date is not None:
                    year = pub_date.find('Year')
                    if year is not None:
                        article_info['Year'] = year.text
    
    pmid = medline_citation.find('PMID')
    if pmid is not None:
        article_info['PMID'] = pmid.text
    
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
    
    article_info['Topic'] = classify_topic(article_info.get('Title', ''))
    
    return article_info

def get_citation_info(pmid):
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
    except Exception:
        pass
    
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
    except Exception:
        pass
    
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
    except Exception:
        pass
    
    # 如果通过 esummary API 获取到了被引数，返回它，否则使用链接解析的数量
    if citation_count > 0:
        return references, cited_by, citation_count
    else:
        return references, cited_by, len(cited_by)

def search_and_fetch(keywords, max_results=20, get_citations=True):
    ids = search_pubmed(keywords, max_results)
    
    if not ids:
        return []
    
    articles = fetch_article_details(ids)
    
    if get_citations:
        for i, article in enumerate(articles):
            pmid = article.get('PMID')
            if pmid:
                references, cited_by, citation_count = get_citation_info(pmid)
                article['References'] = references[:15]
                article['References_Count'] = len(references)
                article['Cited_By'] = cited_by[:15]
                article['Cited_By_Count'] = citation_count
                if i < len(articles) - 1:
                    time.sleep(0.3)
    
    return articles

def get_node_size(citations):
    if citations > 100:
        return 25
    elif citations > 50:
        return 18
    elif citations > 20:
        return 12
    else:
        return 7
