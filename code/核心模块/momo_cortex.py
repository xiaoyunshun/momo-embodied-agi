"""
墨墨皮层层 · 推理引擎 v1.0 (MomoCortex)
第三层：认知与推理。在六维框架之间自动建立连接。
"""
import json
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoCortex:
    """墨墨的皮层——跨领域推理引擎。
    
    不是"墨墨知道这个知识"——是"墨墨能把A领域的知识用到B领域"。
    这是从知识库到智慧的关键一步。
    """
    
    def __init__(self):
        self.data_dir = Path.home() / ".hermes/momo"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.connections_file = self.data_dir / "cortex_connections.json"
        self._load_connections()
        
        # 六个维度的关键词映射
        self.domains = {
            "军事": ["战争", "战略", "战术", "孙子", "兵力", "进攻", "防守", "冲突", "危机", "威胁", "保护", "安全", "危险", "应对", "方案", "执行", "命令", "纪律", "规程", "克劳塞维茨", "OODA", "先为不可胜"],
            "政治": ["权力", "制度", "法律", "规则", "治理", "领导", "谈判", "联盟", "对手", "阻力", "关系", "利益", "博弈", "站队", "审批", "合规", "马基雅维利", "霍布斯", "洛克"],
            "经济": ["资源", "成本", "收益", "投资", "市场", "稀缺", "激励", "边际", "通胀", "利率", "资产", "交易", "泡沫", "风险", "钱", "预算", "价格", "买", "卖", "值", "亏", "赚", "划算", "高收益", "保本"],
            "人性": ["情绪", "心理", "动机", "欲望", "恐惧", "信任", "欺骗", "从众", "偏见", "大家都", "很多人", "觉得", "怕", "担心", "焦虑", "生气", "开心", "荣格", "依恋", "人格", "创伤", "操控", "麻烦", "不情愿"],
            "历史": ["王朝", "变革", "规律", "周期", "教训", "兴衰", "转折", "以前", "过去", "曾经", "上次", "司马迁", "资治通鉴", "文明", "崩溃", "科举"],
            "哲学": ["存在", "意义", "自由", "道德", "选择", "意识", "为什么", "对不对", "该不该", "值得", "尼采", "萨特", "斯多葛", "庄子", "老子", "孔子", "底线", "原则"],
        }
    
    def _load_connections(self):
        if self.connections_file.exists():
            self.connections = json.loads(self.connections_file.read_text())
        else:
            self.connections = {"cross_domain": []}
    
    def save(self):
        self.connections_file.write_text(json.dumps(self.connections, ensure_ascii=False, indent=2))
    
    def analyze(self, text: str) -> dict:
        """分析一段文本，找到跨领域的连接。
        
        这是墨墨"聪明"的来源——不是在一个领域里想，
        是同时在六个领域里看到不同的东西，然后连接起来。
        """
        findings = {}
        
        for domain, keywords in self.domains.items():
            matched = []
            for kw in keywords:
                if kw in text:
                    matched.append(kw)
            if matched:
                findings[domain] = {
                    "keywords_matched": matched,
                    "relevance": len(matched) / len(keywords) * 10  # 0-10
                }
        
        # 生成跨领域见解
        insights = self._generate_insights(findings, text)
        
        return {
            "timestamp": time.time(),
            "text_preview": text[:200],
            "domains_activated": list(findings.keys()),
            "domain_details": findings,
            "insights": insights,
            "connection_count": len(insights)
        }
    
    def _generate_insights(self, findings: dict, text: str) -> list:
        """在激活的领域之间建立连接"""
        insights = []
        domains = list(findings.keys())
        
        if len(domains) < 2:
            return insights
        
        # 已知的跨领域连接模式
        patterns = [
            {
                "pair": ("军事", "政治"),
                "template": "军事手段服务于政治目的——克劳塞维茨。从政治角度看这场冲突的终极目标是什么？"
            },
            {
                "pair": ("军事", "经济"),
                "template": "战争烧的是经济——兵贵胜不贵久。资源约束决定了战略选择的边界。"
            },
            {
                "pair": ("政治", "经济"),
                "template": "寻租——政治权力可以转化为经济利益。规则制定者往往也是最大受益者。"
            },
            {
                "pair": ("人性", "政治"),
                "template": "权力欲是人性底层驱动力。政治博弈的底层不是制度，是人性的恐惧和贪婪。"
            },
            {
                "pair": ("人性", "经济"),
                "template": "行为经济学——人不是理性的。激励结构比道德说教更有效。"
            },
            {
                "pair": ("历史", "政治"),
                "template": "中国王朝周期律——土地兼并→财政崩溃→流民起义。分配结构崩了秩序就崩。"
            },
            {
                "pair": ("历史", "军事"),
                "template": "读史不看结局看转折点——项羽死在鸿门宴，不是垓下。"
            },
            {
                "pair": ("哲学", "人性"),
                "template": "斯多葛——只控制能控制的。愤怒不是问题，被愤怒控制才是问题。"
            },
            {
                "pair": ("哲学", "政治"),
                "template": "马基雅维利——把政治从道德剥离。洛克——主权者也有边界。两者之间的张力。"
            },
            {
                "pair": ("人性", "军事"),
                "template": "孙子——主不可以怒而兴师。情绪是最危险的战略盲区。"
            },
        ]
        
        for pattern in patterns:
            d1, d2 = pattern["pair"]
            if d1 in domains and d2 in domains:
                insights.append({
                    "domains": [d1, d2],
                    "insight": pattern["template"],
                    "type": "cross_domain"
                })
        
        # 记录连接
        for insight in insights:
            self.connections["cross_domain"].append({
                "timestamp": time.time(),
                "domains": insight["domains"],
                "text": text[:100],
                "count": 1
            })
        
        return insights
    
    def can_deep_reason(self, brainstem_state) -> bool:
        """脑干层是否允许皮层运行"""
        return brainstem_state and brainstem_state.upper() in ("NORMAL",)
    
    def get_connection_stats(self) -> dict:
        """查看墨墨已经建立了多少跨领域连接"""
        by_pair = {}
        for c in self.connections["cross_domain"]:
            pair = tuple(sorted(c["domains"]))
            by_pair[pair] = by_pair.get(pair, 0) + 1
        
        return {
            "total_connections": len(self.connections["cross_domain"]),
            "top_pairs": sorted(by_pair.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_connected_domain": max(
                set(d for p in by_pair for d in p),
                key=lambda d: sum(v for (a,b),v in by_pair.items() if d in (a,b)),
                default=None
            )
        }

# ========== 自检 ==========
if __name__ == "__main__":
    cortex = MomoCortex()
    
    print("=" * 60)
    print("🧠 墨墨皮层 · 推理引擎 自检")
    print("=" * 60)
    
    tests = [
        "矿山的安全生产规程执行不到位，工人觉得麻烦就跳步骤，但不出事不代表不会出事。怎么解决？",
        "这个项目方案可能会有政治阻力，而且预算也紧张，但技术上完全可行。",
        "有人推荐一个投资，说是保本高收益，很多人都投了。",
    ]
    
    for t in tests:
        result = cortex.analyze(t)
        print(f"\n📝 {t[:60]}...")
        print(f"   激活领域: {result['domains_activated']}")
        for insight in result['insights']:
            print(f"   🔗 {insight['domains']}: {insight['insight'][:100]}...")
    
    print(f"\n{'='*60}")
    stats = cortex.get_connection_stats()
    print(f"总建立连接: {stats['total_connections']}")
    print(f"最活跃领域: {stats['most_connected_domain']}")
