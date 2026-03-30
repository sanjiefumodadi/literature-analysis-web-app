import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import datetime

# 计算当前年份，用于过滤近两年的文献
current_year = datetime.datetime.now().year

# 定义搜索关键词
search_terms = "(genomic selection[Title/Abstract] OR AI breeding[Title/Abstract] OR smart breeding[Title/Abstract]) AND ("1900"[Date - Publication] : "2023"[Date - Publication])"

# 定义API端点（使用直接的PubMed API）
api_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# 第一步：搜索文献，获取PubMed IDs
encoded_terms = urllib.parse.quote(search_terms)
esearch_url = f"{api_url}esearch.fcgi?db=pubmed&term={encoded_terms}&retmax=20"
print(f"搜索URL: {esearch_url}")

with urllib.request.urlopen(esearch_url) as response:
    content = response.read()

# 解析XML
tree = ET.ElementTree(ET.fromstring(content))
root = tree.getroot()

# 提取PubMed IDs
ids = []
for id_elem in root.findall('.//Id'):
    ids.append(id_elem.text)

print(f"找到 {len(ids)} 篇文献")

# 第二步：获取每篇文献的详细信息
if ids:
    id_string = ",".join(ids)
    fetch_url = f"{api_url}efetch.fcgi?db=pubmed&id={id_string}&retmode=xml"
    
    with urllib.request.urlopen(fetch_url) as fetch_response:
        fetch_content = fetch_response.read()
    
    # 解析XML
    fetch_tree = ET.ElementTree(ET.fromstring(fetch_content))
    fetch_root = fetch_tree.getroot()
    
    # 提取文献信息
    articles = []
    print(f"找到 {len(fetch_root.findall('.//PubmedArticle'))} 篇文献")
    
    for pubmed_article in fetch_root.findall('.//PubmedArticle'):
        article_info = {}
        
        # 提取Title
        medline_citation = pubmed_article.find('MedlineCitation')
        if medline_citation:
            article = medline_citation.find('Article')
            if article:
                # 标题
                article_title = article.find('ArticleTitle')
                if article_title is not None:
                    article_info['Title'] = article_title.text
                
                # 期刊
                journal = article.find('Journal')
                if journal:
                    journal_title = journal.find('Title')
                    if journal_title is not None:
                        article_info['Journal'] = journal_title.text
                
                # 年份
                # 尝试从Article的PubDate获取年份
                pub_date = article.find('PubDate')
                if pub_date:
                    year = pub_date.find('Year')
                    if year is not None:
                        article_info['Year'] = year.text
                
                # 如果Article中没有PubDate，尝试从JournalIssue中获取
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
                
                # PMID
                pmid = medline_citation.find('PMID')
                if pmid is not None:
                    article_info['PMID'] = pmid.text
        
        if article_info:
            # 过滤近两年的文献
            if article_info.get('Year'):
                try:
                    year = int(article_info['Year'])
                    if year < current_year - 2:
                        articles.append(article_info)
                        print(f"添加文献: {article_info.get('Title', 'N/A')}")
                    else:
                        print(f"跳过近两年的文献: {article_info.get('Title', 'N/A')}")
                except ValueError:
                    print(f"年份格式不正确: {article_info['Year']}")
            else:
                print(f"缺少年份信息，跳过: {article_info.get('Title', 'N/A')}")

print(f"总共添加了 {len(articles)} 篇非近两年文献")

# 第三步：获取每篇文献的引用和被引用关系
print("\n获取引用和被引用关系...")
for i, article in enumerate(articles):
    pmid = article.get('PMID')
    if pmid:
        print(f"获取 PMID {pmid} 的引用关系... ({i+1}/{len(articles)})")
        
        # 获取引用关系（该论文引用的其他论文）
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
            
            article['References'] = references[:5]  # 只保留前5个引用
            article['References_Count'] = len(references)
            print(f"  - 引用了 {len(references)} 篇论文")
        except Exception as e:
            print(f"  - 获取引用关系时出错: {e}")
            article['References'] = []
            article['References_Count'] = 0
        
        # 获取被引用关系（引用该论文的其他论文）
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
            
            article['Cited_By'] = cited_by[:5]  # 只保留前5个被引用
            article['Cited_By_Count'] = len(cited_by)
            print(f"  - 被 {len(cited_by)} 篇论文引用")
        except Exception as e:
            print(f"  - 获取被引用关系时出错: {e}")
            article['Cited_By'] = []
            article['Cited_By_Count'] = 0

# 保存到JSON文件
output_json_file = "pubmed_citation_results.json"
with open(output_json_file, 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"\n所有信息已整合并保存到: {output_json_file}")

# 输出结果
print("\n搜索结果：")
print("=" * 80)
for i, article in enumerate(articles, 1):
    print(f"文献 {i}:")
    print(f"Title: {article.get('Title', 'N/A')}")
    print(f"Journal: {article.get('Journal', 'N/A')}")
    print(f"Year: {article.get('Year', 'N/A')}")
    print(f"PMID: {article.get('PMID', 'N/A')}")
    print(f"References: {article.get('References_Count', 0)}")
    print(f"Cited By: {article.get('Cited_By_Count', 0)}")
    print("-" * 80)
else:
    print("未找到相关文献")
