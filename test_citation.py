import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import os

# 定义API端点
api_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# 创建保存结果的文件夹
output_dir = "test_citation"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 测试的PMID（选择一些可能有引用关系的论文）
test_pmids = ["37000000", "36000000", "35000000"]

for pmid in test_pmids:
    print(f"\n测试 PMID: {pmid}")
    
    # 获取引用关系
    try:
        ref_url = f"{api_url}elink.fcgi?dbfrom=pubmed&db=pubmed&id={pmid}&linkname=pubmed_pubmed_refs"
        print(f"引用URL: {ref_url}")
        
        with urllib.request.urlopen(ref_url) as ref_response:
            ref_content = ref_response.read()
        
        # 保存响应
        ref_file = os.path.join(output_dir, f"ref_{pmid}.xml")
        with open(ref_file, 'wb') as f:
            f.write(ref_content)
        print(f"引用响应已保存到: {ref_file}")
        
        # 解析
        ref_tree = ET.ElementTree(ET.fromstring(ref_content))
        ref_root = ref_tree.getroot()
        
        references = []
        for linkset in ref_root.findall('.//LinkSet'):
            for linksetdb in linkset.findall('.//LinkSetDb'):
                print(f"LinkSetDb: {linksetdb.get('LinkName')}")
                if linksetdb.get('LinkName') == 'pubmed_pubmed_refs':
                    for link in linksetdb.findall('.//Link'):
                        ref_id = link.find('Id').text
                        references.append(ref_id)
                        print(f"引用: {ref_id}")
        
        print(f"引用了 {len(references)} 篇论文")
        
    except Exception as e:
        print(f"获取引用关系时出错: {e}")
    
    # 获取被引用关系
    try:
        cited_url = f"{api_url}elink.fcgi?dbfrom=pubmed&db=pubmed&id={pmid}&linkname=pubmed_pubmed_citedin"
        print(f"被引用URL: {cited_url}")
        
        with urllib.request.urlopen(cited_url) as cited_response:
            cited_content = cited_response.read()
        
        # 保存响应
        cited_file = os.path.join(output_dir, f"cited_{pmid}.xml")
        with open(cited_file, 'wb') as f:
            f.write(cited_content)
        print(f"被引用响应已保存到: {cited_file}")
        
        # 解析
        cited_tree = ET.ElementTree(ET.fromstring(cited_content))
        cited_root = cited_tree.getroot()
        
        cited_by = []
        for linkset in cited_root.findall('.//LinkSet'):
            for linksetdb in linkset.findall('.//LinkSetDb'):
                print(f"LinkSetDb: {linksetdb.get('LinkName')}")
                if linksetdb.get('LinkName') == 'pubmed_pubmed_citedin':
                    for link in linksetdb.findall('.//Link'):
                        cited_id = link.find('Id').text
                        cited_by.append(cited_id)
                        print(f"被引用: {cited_id}")
        
        print(f"被 {len(cited_by)} 篇论文引用")
        
    except Exception as e:
        print(f"获取被引用关系时出错: {e}")

print("\n测试完成")
