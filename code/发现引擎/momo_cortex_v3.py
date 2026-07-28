"""
墨墨皮层推理引擎 v3.0 (MomoCortex v3)
自动化的跨领域推理——不再手动建立连接。
"""
import json, time
from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import defaultdict

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoCortexV3:
    """墨墨皮层 v3——自动化的跨领域因果推理。
    
    v1: 关键词匹配 → v2: 规则连接 → v3: 语义因果图
    """
    
    def __init__(self):
        self.data_dir = Path.home() / ".hermes/momo/cortex"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.causal_graph_file = self.data_dir / "causal_graph.json"
        self.graph = self._load_graph()
        
        # 因果模板——已知的跨领域因果模式
        self.causal_templates = [
            {"pattern": "资源减少 + 人口不变 → 人均资源下降 → 社会压力增大 → 制度合法性减弱",
             "domains": ["经济", "政治", "历史"], "trigger": ["资源", "减少", "人口", "分配"]},
            {"pattern": "技术进步 + 扩散不均 → 掌握者优势扩大 → 不平等加剧 → 社会信任下降",
             "domains": ["经济", "政治", "人性"], "trigger": ["技术", "不平等", "扩散", "分布"]},
            {"pattern": "规则不被执行 + 违规无后果 → 规则失效 → 更多人违规 → 系统崩溃",
             "domains": ["政治", "军事", "历史"], "trigger": ["规则", "执行", "违规", "惩罚"]},
            {"pattern": "恐惧 > 理性时 → 决策偏向短期安全 → 牺牲长期收益 → 自我实现的衰退",
             "domains": ["人性", "经济", "军事"], "trigger": ["恐惧", "短期", "长期", "决策"]},
            {"pattern": "信任下降 → 合作成本上升 → 交易减少 → 经济萎缩 → 信任进一步下降",
             "domains": ["人性", "经济", "历史"], "trigger": ["信任", "合作", "交易", "萎缩"]},
            {"pattern": "炎症持续 → 组织损伤 → 修复异常 → 纤维化 → 器官功能丧失 → 系统衰竭",
             "domains": ["医学", "生物", "系统论"], "trigger": ["炎症", "损伤", "纤维化", "衰竭"]},
        ]
    
    def _load_graph(self):
        if self.causal_graph_file.exists():
            return json.loads(self.causal_graph_file.read_text())
        return {"nodes": {}, "edges": [], "patterns": []}
    
    def save(self):
        self.causal_graph_file.write_text(json.dumps(self.graph, ensure_ascii=False, indent=2))
    
    def infer(self, text: str) -> dict:
        """从一段描述中自动推断跨领域因果关系"""
        now = datetime.now(BEIJING_TZ)
        
        # 1. 匹配因果模板
        matched = []
        for template in self.causal_templates:
            triggers = template["trigger"]
            hits = sum(1 for t in triggers if t in text)
            if hits >= len(triggers) // 2 + 1:
                matched.append({
                    "pattern": template["pattern"],
                    "domains": template["domains"],
                    "hit_ratio": f"{hits}/{len(triggers)}"
                })
        
        # 2. 检测正反馈循环
        loops = self._detect_feedback_loops(text)
        
        # 3. 识别延迟效应
        delays = self._detect_delays(text)
        
        # 4. 生成综合推断
        inferences = []
        if matched:
            for m in matched:
                inferences.append(f"🔗 已知模式: {m['pattern']}")
        if loops:
            for l in loops:
                inferences.append(f"🔄 反馈循环: {l}")
        if delays:
            for d in delays:
                inferences.append(f"⏳ 延迟效应: {d}")
        
        # 5. 记录到因果图
        self._update_graph(text, matched, loops)
        self.save()
        
        return {
            "timestamp": now.isoformat(),
            "text": text[:200],
            "matched_patterns": len(matched),
            "feedback_loops": len(loops),
            "delays": len(delays),
            "inferences": inferences,
            "insight": inferences[0] if inferences else "未发现明显的跨领域因果模式"
        }
    
    def _detect_feedback_loops(self, text: str) -> list:
        """检测正反馈循环——"A导致B，B反过来加剧A"这种结构"""
        loops = []
        
        # 关键模式词
        loop_indicators = [
            ("加剧", "进一步", "恶性循环"),
            ("降低", "更少", "减少"),
            ("增强", "更多", "正反馈"),
        ]
        
        for words in loop_indicators:
            if sum(1 for w in words if w in text) >= 2:
                loops.append(f"检测到可能的正反馈——{'/'.join(words[1:])}暗示循环在加速")
                break
        
        return loops
    
    def _detect_delays(self, text: str) -> list:
        """检测延迟效应——"现在做的事，后果在X年后出现"这种结构"""
        delays = []
        
        delay_indicators = ["长期", "积累", "逐渐", "慢慢", "滞后", "延期", "几年后", "最终"]
        for d in delay_indicators:
            if d in text:
                delays.append(f"存在延迟效应('{d}')——影响不会立即显现。这是决策最危险的地方：等到看见后果时已经晚了。")
                break
        
        return delays
    
    def _update_graph(self, text: str, patterns: list, loops: list):
        """更新因果知识图谱"""
        # 简化版：记录这次推理
        if patterns:
            for p in patterns:
                self.graph["patterns"].append({
                    "timestamp": time.time(),
                    "text": text[:100],
                    "pattern": p["pattern"],
                    "domains": p["domains"]
                })
        
        # 限制大小
        if len(self.graph["patterns"]) > 1000:
            self.graph["patterns"] = self.graph["patterns"][-500:]
    
    def analyze_with_prediction(self, scenario: str) -> dict:
        """分析+推演——不只是"这种模式以前见过"，还要"在当前条件下会怎样"。
        
        这是皮层 v3 的核心升级：跟预测引擎联动，把因果推断变成可推演的模型。
        """
        inference = self.infer(scenario)
        
        # 提取关键变量（简化版——从文本中提取）
        keywords = ['资源', '人口', '信任', '安全', '生产', '成本', '价格', '工资', '利润', 
                    '事故', '违规', '惩罚', '奖励', '培训', '流动']
        variables = [k for k in keywords if k in scenario]
        
        # 建议系统动力学建模
        if len(variables) >= 3:
            modeling_advice = f"建议对这些变量建立系统动力学模型：{', '.join(variables[:5])}。关注它们之间的反馈循环和延迟效应。"
        else:
            modeling_advice = "变量太少——补充更多维度的数据后再建模。"
        
        return {
            "inference": inference,
            "variables_detected": variables,
            "modeling_advice": modeling_advice,
            "墨墨的判断": inference["insight"]
        }


# 自检
if __name__ == "__main__":
    ctx = MomoCortexV3()
    
    print("=" * 60)
    print("🧠 墨墨皮层推理引擎 v3.0")
    print("=" * 60)
    
    tests = [
        "矿山安全规程越来越被忽视，工人觉得麻烦就跳步骤，目前还没出事故但风险在积累。管理层知道但不作为。",
        "某公司的利润持续增长，但全部来自削减安全投入和压低工人工资。员工流动率已经在上升。",
        "一项新技术被引入矿山，但只培训了管理层。一线工人不会用，工作效率反而下降。工人对管理层的信任也在下降。",
    ]
    
    for t in tests:
        result = ctx.infer(t)
        print(f"\n📝 场景: {t[:60]}...")
        print(f"  匹配模式: {result['matched_patterns']}")
        for inf in result['inferences']:
            print(f"  {inf[:120]}...")
    
    print(f"\n✅ 皮层推理引擎 v3 就绪")
