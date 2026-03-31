import json

TOPICS = {
    'genomicSelection': {'name': '基因组选择', 'color': '#FFD93D'},
    'aiBreeding': {'name': '人工智能育种', 'color': '#6BCB77'},
    'cropGenetics': {'name': '作物遗传改良', 'color': '#4D96FF'},
    'molecularMarker': {'name': '分子标记辅助', 'color': '#FF6B6B'},
    'quantitativeGenetics': {'name': '数量遗传学', 'color': '#C9B1FF'}
}

def generate_network_html(nodes, edges, node_count, edge_count, core_count):
    topics_json = json.dumps(TOPICS, ensure_ascii=False)
    nodes_json = json.dumps(nodes, ensure_ascii=False)
    edges_json = json.dumps(edges, ensure_ascii=False)
    
    # 完全复刻第二张图的HTML结构和样式
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>学术文献引用网络可视化</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
            min-height: 100vh;
            overflow: hidden;
        }
        
        #container {
            width: 100%;
            height: 600px;
            position: relative;
        }
        
        #graph {
            width: 100%;
            height: 100%;
        }
        
        .node {
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .node:hover {
            filter: brightness(1.3);
        }
        
        .link {
            stroke-opacity: 0.4;
            transition: all 0.3s ease;
        }
        
        .link:hover {
            stroke-opacity: 0.8;
        }
        
        .node-label {
            font-size: 10px;
            fill: #e0e0e0;
            pointer-events: none;
            text-shadow: 0 1px 3px rgba(0,0,0,0.8);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .node:hover + .node-label,
        .node-label.visible {
            opacity: 1;
        }
        
        #tooltip {
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
        }
        
        #tooltip.visible {
            opacity: 1;
        }
        
        #tooltip h4 {
            margin: 0 0 8px 0;
            font-size: 14px;
            color: #fff;
            line-height: 1.4;
        }
        
        #tooltip p {
            margin: 4px 0;
            font-size: 12px;
            color: #b0b0b0;
            line-height: 1.5;
        }
        
        #tooltip .citations {
            color: #ffd700;
            font-weight: 600;
        }
        
        #tooltip .topic {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            margin-top: 6px;
        }
        
        #legend {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(20, 20, 35, 0.9);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        #legend h3 {
            margin: 0 0 15px 0;
            font-size: 14px;
            color: #fff;
            font-weight: 600;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            margin: 10px 0;
            font-size: 12px;
            color: #d0d0d0;
        }
        
        .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        
        .legend-size {
            display: flex;
            align-items: center;
            margin: 15px 0;
            font-size: 12px;
            color: #d0d0d0;
        }
        
        .size-circle {
            border: 2px solid rgba(255,255,255,0.5);
            border-radius: 50%;
            margin-right: 10px;
            background: transparent;
        }
        
        #controls {
            position: absolute;
            bottom: 20px;
            left: 20px;
            display: flex;
            gap: 10px;
        }
        
        .control-btn {
            padding: 10px 20px;
            background: rgba(30, 30, 50, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            color: #e0e0e0;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        
        .control-btn:hover {
            background: rgba(50, 50, 80, 0.9);
            border-color: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }
        
        #stats {
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
        }
        
        #stats div {
            margin: 5px 0;
        }
        
        #stats span {
            color: #fff;
            font-weight: 600;
        }

        .pulse {
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { filter: brightness(1); }
            50% { filter: brightness(1.3); }
            100% { filter: brightness(1); }
        }
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
            <div>文献总数: <span id="node-count">''' + str(node_count) + '''</span></div>
            <div>引用关系: <span id="edge-count">''' + str(edge_count) + '''</span></div>
            <div>核心文献: <span id="core-count">''' + str(core_count) + '''</span></div>
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
        // 主题配置
        const topics = ''' + topics_json + ''';
        
        // 网络数据
        const data = {
            nodes: ''' + nodes_json + ''',
            edges: ''' + edges_json + '''
        };
        
        // 计算节点大小
        const getNodeSize = (citations) => {
            if (citations > 100) return 25;
            if (citations > 50) return 18;
            if (citations > 20) return 12;
            return 7;
        };
        
        // 计算连线粗细
        const getLinkWidth = (strength) => {
            return strength * 2 + 0.5;
        };
        
        // 设置SVG
        const svg = d3.select('#graph');
        const width = document.getElementById('container').offsetWidth;
        const height = document.getElementById('container').offsetHeight;
        
        svg.attr('width', width).attr('height', height);
        
        // 创建缩放行为
        const g = svg.append('g');
        
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
            });
        
        svg.call(zoom);
        
        // 创建力导向模拟
        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.edges)
                .id(d => d.id)
                .distance(d => 120 + (1 - d.strength) * 100)
                .strength(d => d.strength * 0.3))
            .force('charge', d3.forceManyBody()
                .strength(d => d.isCore ? -1200 : -500))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide()
                .radius(d => getNodeSize(d.citations) + 15))
            .force('x', d3.forceX(width / 2).strength(0.03))
            .force('y', d3.forceY(height / 2).strength(0.03));
        
        // 绘制连线
        const link = g.append('g')
            .selectAll('line')
            .data(data.edges)
            .enter()
            .append('line')
            .attr('class', 'link')
            .attr('stroke', '#5a6a8a')
            .attr('stroke-width', d => getLinkWidth(d.strength));
        
        // 绘制节点
        const node = g.append('g')
            .selectAll('circle')
            .data(data.nodes)
            .enter()
            .append('circle')
            .attr('class', d => `node ${d.isCore ? 'pulse' : ''}`)
            .attr('r', d => getNodeSize(d.citations))
            .attr('fill', d => topics[d.topic].color)
            .attr('stroke', d => d.isCore ? '#fff' : 'rgba(255,255,255,0.3)')
            .attr('stroke-width', d => d.isCore ? 3 : 1)
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));
        
        // 添加标签（仅核心节点和高度被引节点）
        const label = g.append('g')
            .selectAll('text')
            .data(data.nodes.filter(d => d.isCore || d.citations > 60))
            .enter()
            .append('text')
            .attr('class', 'node-label visible')
            .attr('text-anchor', 'middle')
            .attr('dy', d => getNodeSize(d.citations) + 15)
            .text(d => d.title.length > 25 ? d.title.substring(0, 25) + '...' : d.title);
        
        // 工具提示
        const tooltip = d3.select('#tooltip');
        
        node.on('mouseover', function(event, d) {
            d3.select(this)
                .transition()
                .duration(200)
                .attr('r', getNodeSize(d.citations) * 1.3);
            
            tooltip.select('#tt-title').text(d.title);
            tooltip.select('#tt-author').text(`作者: ${d.authors}`);
            tooltip.select('#tt-year').text(`发表年份: ${d.year}`);
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
            
            // 高亮相连的连线
            link.style('stroke', l => 
                (l.source.id === d.id || l.target.id === d.id) ? '#fff' : '#5a6a8a'
            ).style('stroke-opacity', l => 
                (l.source.id === d.id || l.target.id === d.id) ? 1 : 0.2
            );
        })
        .on('mouseout', function(event, d) {
            d3.select(this)
                .transition()
                .duration(200)
                .attr('r', getNodeSize(d.citations));
            
            tooltip.classed('visible', false);
            
            link.style('stroke', '#5a6a8a')
                .style('stroke-opacity', 0.4);
        })
        .on('click', function(event, d) {
            // 点击高亮相连节点
            const connectedIds = new Set();
            connectedIds.add(d.id);
            
            data.edges.forEach(l => {
                if (l.source.id === d.id) connectedIds.add(l.target.id);
                if (l.target.id === d.id) connectedIds.add(l.source.id);
            });
            
            node.style('opacity', n => connectedIds.has(n.id) ? 1 : 0.2);
            link.style('opacity', l => 
                (l.source.id === d.id || l.target.id === d.id) ? 1 : 0.05
            );
            
            setTimeout(() => {
                node.style('opacity', 1);
                link.style('opacity', 1);
            }, 2000);
        });
        
        // 模拟更新位置
        simulation.on('tick', () => {
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
        });
        
        // 拖拽函数
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        // 控制按钮功能
        let animationEnabled = true;
        
        function resetZoom() {
            svg.transition()
                .duration(750)
                .call(zoom.transform, d3.zoomIdentity);
        }
        
        function toggleAnimation() {
            animationEnabled = !animationEnabled;
            if (animationEnabled) {
                simulation.restart();
            } else {
                simulation.stop();
            }
        }
        
        function highlightCore() {
            node.style('opacity', d => d.isCore ? 1 : 0.1);
            link.style('opacity', 0.05);
            
            setTimeout(() => {
                node.transition().duration(500).style('opacity', 1);
                link.transition().duration(500).style('opacity', 1);
            }, 2000);
        }
        
        // 窗口大小调整
        window.addEventListener('resize', () => {
            const newWidth = document.getElementById('container').offsetWidth;
            const newHeight = document.getElementById('container').offsetHeight;
            
            svg.attr('width', newWidth).attr('height', newHeight);
            simulation.force('center', d3.forceCenter(newWidth / 2, newHeight / 2));
            simulation.alpha(0.3).restart();
        });
    </script>
</body>
</html>'''
    
    return html
