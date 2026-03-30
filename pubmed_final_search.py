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
esearch_url = f"{api_url}esearch.fcgi?db=pubmed&term={encoded_terms}&retmax=30"
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
    
    # 第二步：获取每篇文献的详细信息
    if ids:
        # 分批处理，每次处理10篇
        batch_size = 10
        all_articles = []
        
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i+batch_size]
            id_string = ",".join(batch_ids)
            fetch_url = f"{api_url}efetch.fcgi?db=pubmed&id={id_string}&retmode=xml"
            print(f"\n处理批次 {i//batch_size + 1}/{(len(ids)+batch_size-1)//batch_size}")
            print(f"获取详细信息URL: {fetch_url}")
            
            with urllib.request.urlopen(fetch_url) as fetch_response:
                fetch_content = fetch_response.read()
            print("获取详细信息成功")
            
            # 解析XML
            fetch_tree = ET.ElementTree(ET.fromstring(fetch_content))
            fetch_root = fetch_tree.getroot()
            
            # 提取文献信息
            pubmed_articles = fetch_root.findall('.//PubmedArticle')
            print(f"处理 {len(pubmed_articles)} 篇文献")
            
            for pubmed_article in pubmed_articles:
                article_info = {}
                
                # 提取Title
                medline_citation = pubmed_article.find('MedlineCitation')
                if medline_citation is not None:
                    article = medline_citation.find('Article')
                    if article is not None:
                        # 标题
                        article_title = article.find('ArticleTitle')
                        if article_title is not None:
                            article_info['Title'] = article_title.text
                        
                        # 期刊
                        journal = article.find('Journal')
                        if journal is not None:
                            journal_title = journal.find('Title')
                            if journal_title is not None:
                                article_info['Journal'] = journal_title.text
                        
                        # 年份
                        # 尝试从Journal的JournalIssue中获取PubDate
                        journal = article.find('Journal')
                        if journal is not None:
                            journal_issue = journal.find('JournalIssue')
                            if journal_issue is not None:
                                pub_date = journal_issue.find('PubDate')
                                if pub_date is not None:
                                    year = pub_date.find('Year')
                                    if year is not None:
                                        article_info['Year'] = year.text
                        
                        # 如果没有找到，尝试从Article的PubDate获取
                        if 'Year' not in article_info:
                            pub_date = article.find('PubDate')
                            if pub_date is not None:
                                year = pub_date.find('Year')
                                if year is not None:
                                    article_info['Year'] = year.text
                        
                        # 如果仍然没有找到，尝试从MedlineCitation的DateCompleted获取年份
                        if 'Year' not in article_info:
                            date_completed = medline_citation.find('DateCompleted')
                            if date_completed is not None:
                                year = date_completed.find('Year')
                                if year is not None:
                                    article_info['Year'] = year.text
                        
                        # 如果仍然没有找到，尝试从MedlineCitation的DateRevised获取年份
                        if 'Year' not in article_info:
                            date_revised = medline_citation.find('DateRevised')
                            if date_revised is not None:
                                year = date_revised.find('Year')
                                if year is not None:
                                    article_info['Year'] = year.text
                        
                        # PMID
                        pmid = medline_citation.find('PMID')
                        if pmid is not None:
                            article_info['PMID'] = pmid.text
                
                if article_info:
                    all_articles.append(article_info)
                    print(f"添加文献: {article_info.get('Title', 'N/A')}")

        print(f"\n总共获取了 {len(all_articles)} 篇文献")
        
        # 第三步：获取每篇文献的引用和被引用关系
        print("\n获取引用和被引用关系...")
        for i, article in enumerate(all_articles):
            pmid = article.get('PMID')
            if pmid:
                print(f"获取 PMID {pmid} 的引用关系... ({i+1}/{len(all_articles)})")
                
                # 获取引用关系（该论文引用的其他论文）
                try:
                    ref_url = f"{api_url}elink.fcgi?dbfrom=pubmed&db=pubmed&id={pmid}&linkname=pubmed_pubmed_refs"
                    print(f"  - 引用URL: {ref_url}")
                    with urllib.request.urlopen(ref_url) as ref_response:
                        ref_content = ref_response.read()
                    
                    # 保存响应内容用于调试
                    ref_file = os.path.join(output_dir, f"ref_{pmid}.xml")
                    with open(ref_file, 'wb') as f:
                        f.write(ref_content)
                    print(f"  - 引用响应已保存到: {ref_file}")
                    
                    ref_tree = ET.ElementTree(ET.fromstring(ref_content))
                    ref_root = ref_tree.getroot()
                    
                    references = []
                    for linkset in ref_root.findall('.//LinkSet'):
                        for linksetdb in linkset.findall('.//LinkSetDb'):
                            print(f"  - LinkSetDb: {linksetdb.get('LinkName')}")
                            if linksetdb.get('LinkName') == 'pubmed_pubmed_refs':
                                for link in linksetdb.findall('.//Link'):
                                    ref_id = link.find('Id').text
                                    references.append(ref_id)
                                    print(f"  - 引用: {ref_id}")
                    
                    article['References'] = references[:10]  # 保留前10个引用
                    article['References_Count'] = len(references)
                    print(f"  - 引用了 {len(references)} 篇论文")
                except Exception as e:
                    print(f"  - 获取引用关系时出错: {e}")
                    article['References'] = []
                    article['References_Count'] = 0
                
                # 获取被引用关系（引用该论文的其他论文）
                try:
                    cited_url = f"{api_url}elink.fcgi?dbfrom=pubmed&db=pubmed&id={pmid}&linkname=pubmed_pubmed_citedin"
                    print(f"  - 被引用URL: {cited_url}")
                    with urllib.request.urlopen(cited_url) as cited_response:
                        cited_content = cited_response.read()
                    
                    # 保存响应内容用于调试
                    cited_file = os.path.join(output_dir, f"cited_{pmid}.xml")
                    with open(cited_file, 'wb') as f:
                        f.write(cited_content)
                    print(f"  - 被引用响应已保存到: {cited_file}")
                    
                    cited_tree = ET.ElementTree(ET.fromstring(cited_content))
                    cited_root = cited_tree.getroot()
                    
                    cited_by = []
                    for linkset in cited_root.findall('.//LinkSet'):
                        for linksetdb in linkset.findall('.//LinkSetDb'):
                            print(f"  - LinkSetDb: {linksetdb.get('LinkName')}")
                            if linksetdb.get('LinkName') == 'pubmed_pubmed_citedin':
                                for link in linksetdb.findall('.//Link'):
                                    cited_id = link.find('Id').text
                                    cited_by.append(cited_id)
                                    print(f"  - 被引用: {cited_id}")
                    
                    article['Cited_By'] = cited_by[:10]  # 保留前10个被引用
                    article['Cited_By_Count'] = len(cited_by)
                    print(f"  - 被 {len(cited_by)} 篇论文引用")
                except Exception as e:
                    print(f"  - 获取被引用关系时出错: {e}")
                    article['Cited_By'] = []
                    article['Cited_By_Count'] = 0

        # 筛选权威文献（被引用次数大于10）
        authored_articles = [article for article in all_articles if article.get('Cited_By_Count', 0) > 10]
        print(f"\n筛选出 {len(authored_articles)} 篇权威文献（被引用次数>10）")
        
        # 按被引用次数排序
        authored_articles.sort(key=lambda x: x.get('Cited_By_Count', 0), reverse=True)
        
        # 保存所有文献（包括非权威）
        all_articles_file = os.path.join(output_dir, "all_breeding_literature.json")
        with open(all_articles_file, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)
        print(f"所有文献保存成功: {all_articles_file}")
        
        # 保存权威文献
        output_json_file = os.path.join(output_dir, "breeding_literature.json")
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(authored_articles, f, ensure_ascii=False, indent=2)
        print(f"权威文献JSON文件保存成功: {output_json_file}")
        
        # 保存为CSV文件
        output_csv_file = os.path.join(output_dir, "breeding_literature.csv")
        with open(output_csv_file, 'w', encoding='utf-8', newline='') as f:
            f.write("Title,Journal,Year,PMID,References Count,Cited By Count\n")
            for article in authored_articles:
                title = article.get('Title', '').replace('"', '""')
                journal = article.get('Journal', '').replace('"', '""')
                year = article.get('Year', '')
                pmid = article.get('PMID', '')
                refs_count = article.get('References_Count', 0)
                cited_count = article.get('Cited_By_Count', 0)
                f.write(f'"{title}","{journal}",{year},{pmid},{refs_count},{cited_count}\n')
        print(f"权威文献CSV文件保存成功: {output_csv_file}")
        
        # 输出结果
        print("\n权威文献搜索结果：")
        print("=" * 120)
        for i, article in enumerate(authored_articles, 1):
            print(f"文献 {i}:")
            print(f"Title: {article.get('Title', 'N/A')}")
            print(f"Journal: {article.get('Journal', 'N/A')}")
            print(f"Year: {article.get('Year', 'N/A')}")
            print(f"PMID: {article.get('PMID', 'N/A')}")
            print(f"References: {article.get('References_Count', 0)}")
            print(f"Cited By: {article.get('Cited_By_Count', 0)}")
            print("-" * 120)
        else:
            print("未找到符合条件的权威文献")
            
        # 输出所有文献
        print("\n所有搜索到的文献：")
        print("=" * 120)
        for i, article in enumerate(all_articles, 1):
            print(f"文献 {i}:")
            print(f"Title: {article.get('Title', 'N/A')}")
            print(f"Journal: {article.get('Journal', 'N/A')}")
            print(f"Year: {article.get('Year', 'N/A')}")
            print(f"PMID: {article.get('PMID', 'N/A')}")
            print(f"References: {article.get('References_Count', 0)}")
            print(f"Cited By: {article.get('Cited_By_Count', 0)}")
            print("-" * 120)
except Exception as e:
    print(f"发生错误: {e}")
    import traceback
    traceback.print_exc()
