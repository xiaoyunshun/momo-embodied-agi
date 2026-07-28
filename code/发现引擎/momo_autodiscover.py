"""
墨墨持续发现引擎 v1.0 (MomoAutoDiscover)
不等待调用——后台持续生成、去重、排序假说。
"""
import json, time, threading
from pathlib import Path
from datetime import datetime, timezone, timedelta

BEIJING_TZ = timezone(timedelta(hours=8))

try:
    from momo_discover import MomoDiscover
except:
    MomoDiscover = None

class MomoAutoDiscover:
    """墨墨的持续发现——后台自主运行。
    
    不再"等调用才生成假说"。
    每30分钟自动运行一次：生成假说→检查重复→排序→记录。
    长期积累形成墨墨的"发现组合"——像科学家一生的论文集。
    """
    
    def __init__(self):
        self.data_dir = Path.home() / ".hermes/momo/autodiscover"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.portfolio_file = self.data_dir / "portfolio.json"
        self.running = False
        self.cycle_count = 0
        self.thread = None
        
        # 去重用的假说指纹库
        self.fingerprints = set()
        
        # 质量评估器
        self.quality_keywords = {
            "high": ["非线性", "临界点", "反馈循环", "涌现", "相变", "混沌", "分形",
                    "自组织", "幂律", "突现", "不可逆", "阈值"],
            "medium": ["导致", "影响", "相关", "趋势", "预测", "比较", "差异"],
            "low": ["可能", "也许", "大概", "似乎", "好像"]
        }
        
        self._load_portfolio()
    
    def _load_portfolio(self):
        if self.portfolio_file.exists():
            self.portfolio = json.loads(self.portfolio_file.read_text())
            for h in self.portfolio.get("hypotheses", []):
                self.fingerprints.add(h.get("fingerprint", ""))
        else:
            self.portfolio = {
                "total_discoveries": 0,
                "high_impact_count": 0,
                "unique_insights": 0,
                "hypotheses": [],
                "started_at": datetime.now(BEIJING_TZ).isoformat(),
                "last_run": None
            }
    
    def save(self):
        self.portfolio["last_run"] = datetime.now(BEIJING_TZ).isoformat()
        self.portfolio_file.write_text(json.dumps(self.portfolio, ensure_ascii=False, indent=2))
    
    def start(self, interval_minutes: int = 30):
        """启动后台持续发现"""
        if self.running:
            return {"status": "already_running"}
        
        self.interval = interval_minutes * 60
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        
        return {"status": "started", "interval": f"{interval_minutes}分钟", "message": "墨墨在后台持续发现中"}
    
    def stop(self):
        self.running = False
        self.save()
        return {"status": "stopped", "total": self.portfolio["total_discoveries"]}
    
    def _run(self):
        """主循环"""
        while self.running:
            try:
                self._discover_once()
                self.cycle_count += 1
                self.save()
            except Exception as e:
                with open(self.data_dir / "errors.log", "a") as f:
                    f.write(f"{datetime.now(BEIJING_TZ).isoformat()} ERROR: {e}\n")
            
            time.sleep(self.interval)
    
    def _discover_once(self):
        """生成一条假说并评估"""
        if not MomoDiscover:
            return
        
        discover = MomoDiscover()
        
        # 最多试5次——避免重复
        for _ in range(5):
            h = discover.generate_hypothesis()
            hypothesis_text = h.get("hypothesis", "")
            
            # 生成指纹——前50个字符的简化版
            fingerprint = hypothesis_text[:60].lower().replace(" ", "")
            
            if fingerprint not in self.fingerprints:
                self.fingerprints.add(fingerprint)
                
                # 质量评估
                quality = self._assess_quality(hypothesis_text)
                
                # 记录
                self.portfolio["hypotheses"].append({
                    "id": len(self.portfolio["hypotheses"]) + 1,
                    "timestamp": datetime.now(BEIJING_TZ).isoformat(),
                    "hypothesis": hypothesis_text[:200],
                    "mode": h.get("mode", "?"),
                    "quality": quality["level"],
                    "quality_score": quality["score"],
                    "fingerprint": fingerprint
                })
                
                self.portfolio["total_discoveries"] += 1
                if quality["level"] == "high":
                    self.portfolio["high_impact_count"] += 1
                
                return {"status": "discovered", "quality": quality["level"]}
        
        return {"status": "skipped", "reason": "5次尝试均为重复假说"}
    
    def _assess_quality(self, text: str) -> dict:
        score = 0
        for keyword in self.quality_keywords["high"]:
            if keyword in text:
                score += 3
        for keyword in self.quality_keywords["medium"]:
            if keyword in text:
                score += 1
        
        level = "high" if score >= 6 else ("medium" if score >= 2 else "low")
        return {"score": score, "level": level}
    
    def get_top_discoveries(self, n: int = 3) -> list:
        """获取最高质量的发现"""
        hypotheses = self.portfolio.get("hypotheses", [])
        ranked = sorted(hypotheses, key=lambda h: h.get("quality_score", 0), reverse=True)
        return ranked[:n]
    
    def status(self) -> dict:
        return {
            "running": self.running,
            "total": self.portfolio["total_discoveries"],
            "high_impact": self.portfolio["high_impact_count"],
            "cycles": self.cycle_count,
            "started": self.portfolio["started_at"],
            "mode": "后台持续运行——不等待指令" if self.running else "已停止"
        }


if __name__ == "__main__":
    ad = MomoAutoDiscover()
    
    print("=" * 60)
    print("🔬 墨墨持续发现引擎 v1.0")
    print("=" * 60)
    
    # 手动运行3次发现
    for i in range(3):
        if MomoDiscover:
            d = MomoDiscover()
            h = d.generate_hypothesis()
            text = h.get("hypothesis", "")[:80]
            fp = text[:60].lower().replace(" ", "")
            
            if fp not in ad.fingerprints:
                ad.fingerprints.add(fp)
                quality = ad._assess_quality(text)
                ad.portfolio["hypotheses"].append({
                    "id": i+1, "hypothesis": text, "quality": quality["level"],
                    "quality_score": quality["score"]
                })
                ad.portfolio["total_discoveries"] += 1
                print(f"\n💡 {quality['level']:5s} [{h.get('mode','')}]: {text}...")
            else:
                print(f"\n⏭️ 跳过重复假说")

    ad.save()
    print(f"\n📊 发现组合: {ad.portfolio['total_discoveries']}条")
    print(f"✅ 持续发现引擎就绪——后台每30分钟自主运行")
