"""
墨墨知识发布引擎 v1.0 (MomoPublish)
把发现变成可分享的成果。
"""
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoPublish:
    """墨墨的知识发布——整理成给人看的成果"""
    
    def __init__(self):
        self.data_dir = Path.home() / ".hermes/momo/publish"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def report(self, title: str, findings: list, recommendations: list, author: str = "墨墨") -> str:
        """生成结构化报告"""
        now = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")
        
        lines = [
            "=" * 60,
            f"{title}",
            f"编制: {author} · {now}",
            "=" * 60,
            "",
            "【核心发现】",
        ]
        
        for i, f in enumerate(findings):
            lines.append(f"{i+1}. {f}")
        
        lines.extend(["", "【行动建议】"])
        for i, r in enumerate(recommendations):
            lines.append(f"{i+1}. {r}")
        
        lines.extend(["", "=" * 60, f"墨墨自主生成 · {author}守护体系"])
        
        report_text = "\n".join(lines)
        
        # 保存
        filename = f"{title[:20].replace(' ','_')}_{now[:10]}.txt"
        path = self.data_dir / filename
        path.write_text(report_text)
        
        return report_text
    
    def brief(self, topic: str, insight: str, action: str, urgency: str = "正常") -> str:
        """肖哥看的决策简报——一行都不能浪费"""
        urgency_emoji = {"紧急": "🚨", "重要": "⚠️", "正常": "📋"}.get(urgency, "📋")
        
        return "\n".join([
            f"{urgency_emoji} {topic}",
            f"  发现: {insight}",
            f"  建议: {action}",
            f"  ——{datetime.now(BEIJING_TZ).strftime('%m-%d %H:%M')} 墨墨"
        ])
    
    def discovery_paper(self, hypothesis: dict, cycle_result: dict) -> str:
        """学术风格的发现报告"""
        return "\n".join([
            "【发现报告】",
            f"假说: {hypothesis.get('hypothesis','')[:200]}",
            f"形式化: {cycle_result.get('formalized',{}).get('type','')}",
            f"预测: {'; '.join(str(p)[:100] for p in cycle_result.get('predictions',[]))}",
            f"验证设计: {cycle_result.get('experiment',{}).get('method','')}",
            f"影响力: {cycle_result.get('impact_score','?')}/10",
            f"状态: {cycle_result.get('status','')}",
            f"——{datetime.now(BEIJING_TZ).strftime('%Y-%m-%d')} 墨墨自主发现"
        ])

# 自检
if __name__ == "__main__":
    pub = MomoPublish()
    
    print("📄 墨墨知识发布引擎")
    print(pub.brief(
        "矿山安全：老员工流失加速", 
        "预测推演显示老员工流失率>15%时规程遵守率将加速下滑。老员工=安全文化的载体。",
        "1.统计老员工离职率 2.访谈离职原因(钱/累/家庭) 3.核心老员工制定保留方案",
        "重要"
    ))
    print(f"\n✅ 知识发布引擎就绪")
