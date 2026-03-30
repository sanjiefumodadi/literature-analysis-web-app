import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import os

# 定义搜索关键词
search_terms = "(genomic selection[Title/Abstract] OR AI breeding[Title/Abstract] OR smart breeding[Title/Abstract] OR intelligent breeding[Title/Abstract])"

# 定义API端点
api_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# 创建保存结果的文件夹
output_dir = "breeding_literature"
print(f"创建文件夹: {output_dir}")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"文件夹 {output_dir} 创建成功")
else:
    print(f"文件夹 {output_dir} 已存在")

# 第一步：搜索文献，获取PubMed IDs
print("\n开始搜索相关文献...")
encoded_terms = urllib.parse.quote(search_terms)
esearch_url = f"{api_url}esearch.fcgi?db=pubmed&term={encoded_terms}&retmax=10"
print(f"搜索URL: {esearch_url}")

try:
    with urllib.request.urlopen(esearch_url) as response:
        content = response.read()
    print("搜索成功")
    
    # 解析XML
    tree = ET.ElementTree(ET.fromstring(content))
    root = tree.getroot()
    
    # 提取PubMed IDs
    ids = []
    for id_elem in root.findall('.//Id'):
        ids.append(id_elem.text)
    
    print(f"找到 {len(ids)} 篇文献")
    print(f"PMIDs: {ids}")
    
    # 保存初步结果
    initial_result = {"pmids": ids}
    initial_file = os.path.join(output_dir, "initial_results.json")
    with open(initial_file, 'w', encoding='utf-8') as f:
        json.dump(initial_result, f, ensure_ascii=False, indent=2)
    print(f"初步结果保存成功: {initial_file}")
    
    # 第二步：获取每篇文献的详细信息（只处理前5篇）
    if ids:
        id_string = ",".join(ids[:5])  # 只处理前5篇
        fetch_url = f"{api_url}efetch.fcgi?db=pubmed&id={id_string}&retmode=xml"
        print(f"\n获取详细信息URL: {fetch_url}")
        
        with urllib.request.urlopen(fetch_url) as fetch_response:
            fetch_content = fetch_response.read()
        print("获取详细信息成功")
        
        # 保存原始XML响应
        xml_file = os.path.join(output_dir, "raw_response.xml")
        with open(xml_file, 'wb') as f:
            f.write(fetch_content)
        print(f"原始XML保存成功: {xml_file}")
        
        # 解析XML
        fetch_tree = ET.ElementTree(ET.fromstring(fetch_content))
        fetch_root = fetch_tree.getroot()
        
        # 提取文献信息
        articles = []
        pubmed_articles = fetch_root.findall('.//PubmedArticle')
        print(f"处理 {len(pubmed_articles)} 篇文献")
        
        for pubmed_article in pubmed_articles:
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
                    # 尝试从Journal的JournalIssue中获取PubDate
                    journal = article.find('Journal')
                    if journal:
                        journal_issue = journal.find('JournalIssue')
                        if journal_issue:
                            pub_date = journal_issue.find('PubDate')
                            if pub_date:
                                year = pub_date.find('Year')
                                if year is not None:
                                    article_info['Year'] = year.text
                    
                    # 如果没有找到，尝试从Article的PubDate获取
                    if 'Year' not in article_info:
                        pub_date = article.find('PubDate')
                        if pub_date:
                            year = pub_date.find('Year')
                            if year is not None:
                                article_info['Year'] = year.text
                    
                    # 如果仍然没有找到，尝试从MedlineCitation的DateCompleted获取年份
                    if 'Year' not in article_info:
                        date_completed = medline_citation.find('DateCompleted')
                        if date_completed:
                            year = date_completed.find('Year')
                            if year is not None:
                                article_info['Year'] = year.text
                    
                    # 如果仍然没有找到，尝试从MedlineCitation的DateRevised获取年份
                    if 'Year' not in article_info:
                        date_revised = medline_citation.find('DateRevised')
                        if date_revised:
                            year = date_revised.find('Year')
                            if year is not None:
                                article_info['Year'] = year.text
                    
                    # PMID
                    pmid = medline_citation.find('PMID')
                    if pmid is not None:
                        article_info['PMID'] = pmid.text
            
            if article_info:
                articles.append(article_info)
                print(f"添加文献: {article_info.get('Title', 'N/A')}")

        print(f"总共获取了 {len(articles)} 篇文献")
        
        # 保存到JSON文件
        output_json_file = os.path.join(output_dir, "breeding_literature.json")
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"JSON文件保存成功: {output_json_file}")
        
        # 保存为CSV文件
        output_csv_file = os.path.join(output_dir, "breeding_literature.csv")
        with open(output_csv_file, 'w', encoding='utf-8', newline='') as f:
            f.write("Title,Journal,Year,PMID\n")
            for article in articles:
                title = article.get('Title', '').replace('"', '""')
                journal = article.get('Journal', '').replace('"', '""')
                year = article.get('Year', '')
                pmid = article.get('PMID', '')
                f.write(f'"{title}","{journal}",{year},{pmid}\n')
        print(f"CSV文件保存成功: {output_csv_file}")
        
        # 输出结果
        print("\n搜索结果：")
        print("=" * 120)
        for i, article in enumerate(articles, 1):
            print(f"文献 {i}:")
            print(f"Title: {article.get('Title', 'N/A')}")
            print(f"Journal: {article.get('Journal', 'N/A')}")
            print(f"Year: {article.get('Year', 'N/A')}")
            print(f"PMID: {article.get('PMID', 'N/A')}")
            print("-" * 120)
except Exception as e:
    print(f"发生错误: {e}")
    import traceback
    traceback.print_exc()
