"""
墨墨预测建模引擎 v1.0 (MomoPredict)
从"分析已有"到"推演未有"。
系统动力学 + 蒙特卡洛模拟 + 情景推演。
"""
import math, random, json
from pathlib import Path
from datetime import datetime, timedelta, timezone

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoPredict:
    """墨墨的预测引擎——不是"算命的"，是系统推演。
    
    三个核心能力：
    1. 系统动力学——多个变量如何互相影响
    2. 蒙特卡洛模拟——不确定性的量化
    3. 情景推演——"如果X发生了会怎样"
    """
    
    def __init__(self):
        self.data_dir = Path.home() / ".hermes/momo/predict"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    # ========== 系统动力学 ==========
    
    def system_dynamics(self, initial_state: dict, rules: list, steps: int = 50) -> dict:
        """模拟一个系统的多步演化
        
        initial_state: {"资源": 100, "人口": 50, "信任": 80}
        rules: [
            {"from": "人口", "to": "资源", "effect": "消耗", "rate": 0.5},
            {"from": "资源", "to": "信任", "effect": "正向", "rate": 0.2, "threshold": 60},
            {"from": "信任", "to": "人口", "effect": "正向", "rate": 0.1},
        ]
        """
        state = {k: v for k, v in initial_state.items()}
        history = [{**state, "step": 0}]
        
        for step in range(1, steps + 1):
            new_state = {k: v for k, v in state.items()}
            
            for rule in rules:
                source = rule["from"]
                target = rule["to"]
                rate = rule["rate"]
                effect = rule.get("effect", "消耗")
                
                if source not in state or target not in state:
                    continue
                
                # 检查阈值条件
                if "threshold" in rule:
                    if rule.get("threshold_above") and state[source] < rule["threshold_above"]:
                        continue
                    if rule.get("threshold_below") and state[source] > rule["threshold_below"]:
                        continue
                
                if effect == "消耗":
                    new_state[target] -= state[source] * rate
                elif effect == "正向":
                    new_state[target] += state[source] * rate
                elif effect == "比例":
                    new_state[target] = state[source] * rate
            
            # 限制范围
            for k in new_state:
                new_state[k] = max(0, min(200, new_state[k]))
            
            state = new_state
            history.append({**state, "step": step})
        
        # 分析趋势
        trends = {}
        for var in initial_state:
            start_val = history[0][var]
            end_val = history[-1][var]
            change_pct = ((end_val - start_val) / start_val * 100) if start_val > 0 else 0
            
            if change_pct > 10:
                trends[var] = "📈 上升"
            elif change_pct < -10:
                trends[var] = "📉 下降"
            else:
                trends[var] = "➡️ 稳定"
            
            # 检查崩溃
            if end_val < start_val * 0.2:
                trends[var] = f"🚨 趋近崩溃({end_val:.1f})"
        
        # 找到崩溃点
        collapse_point = None
        for h in history:
            for var in initial_state:
                if h[var] < initial_state[var] * 0.1:
                    collapse_point = h["step"]
                    break
            if collapse_point:
                break
        
        return {
            "initial": initial_state,
            "final": {k: round(v, 1) for k, v in history[-1].items() if k != "step"},
            "steps": steps,
            "trends": trends,
            "collapse_at_step": collapse_point,
            "history": history[::max(1, steps // 10)],  # 每10%取一次快照
            "墨墨的分析": self._analyze_dynamics(trends, collapse_point)
        }
    
    def _analyze_dynamics(self, trends: dict, collapse: int) -> str:
        parts = []
        for var, trend in trends.items():
            parts.append(f"{var}: {trend}")
        
        analysis = " | ".join(parts)
        if collapse:
            analysis += f" | ⚠️ 系统在第{collapse}步有变量趋近崩溃"
        return analysis
    
    # ========== 蒙特卡洛模拟 ==========
    
    def monte_carlo(self, base_case: dict, uncertainty: dict, trials: int = 10000) -> dict:
        """蒙特卡洛模拟——在不确定性中看可能的结果分布
        
        base_case: {"年收益": 0.08, "年通胀": 0.03}
        uncertainty: {"年收益": ("normal", 0.08, 0.15),  # 正态分布(均值,标准差)
                       "年通胀": ("uniform", 0.02, 0.06)}  # 均匀分布(下界,上界)
        """
        results = {}
        for var_name in base_case:
            results[var_name] = []
        
        for _ in range(trials):
            for var_name, base_val in base_case.items():
                if var_name in uncertainty:
                    dist_type, *params = uncertainty[var_name]
                    if dist_type == "normal":
                        val = random.gauss(params[0], params[1])
                    elif dist_type == "uniform":
                        val = random.uniform(params[0], params[1])
                    else:
                        val = base_val
                else:
                    val = base_val
                results[var_name].append(val)
        
        # 统计
        stats = {}
        for var_name, samples in results.items():
            samples.sort()
            stats[var_name] = {
                "mean": sum(samples) / len(samples),
                "median": samples[len(samples) // 2],
                "p10": samples[len(samples) // 10],         # 最差10%
                "p90": samples[len(samples) * 9 // 10],      # 最好10%
                "worst": samples[0],                          # 最差情况
                "best": samples[-1],                          # 最好情况
            }
        
        return {
            "trials": trials,
            "statistics": stats,
            "墨墨的解释": self._mc_insight(stats)
        }
    
    def _mc_insight(self, stats: dict) -> str:
        parts = []
        for var, s in stats.items():
            parts.append(f"{var}: 均值{s['mean']:.3f} (90%区间[{s['p10']:.3f}~{s['p90']:.3f}])")
        return " | ".join(parts)
    
    # ========== 情景推演 ==========
    
    def scenario(self, description: str, variables: dict, rules: list) -> dict:
        """"如果X会怎样"的情景推演
        
        基于系统动力学，但加入具体的"如果"条件。
        """
        # 先跑基准线
        baseline = self.system_dynamics(variables, rules, 30)
        
        # 如果条件——通常是改变某个变量的初始值或参数
        scenarios = {}
        for var_name, change in variables.items():
            if isinstance(change, dict) and "if" in change:
                alt_vars = {k: (v["if"] if k == var_name and isinstance(v, dict) else v) 
                           for k, v in variables.items()}
                alt_vars = {k: (v if not isinstance(v, dict) else v.get("base", v)) 
                           for k, v in alt_vars.items()}
                alt_result = self.system_dynamics(alt_vars, rules, 30)
                
                scenarios[f"如果{var_name}={change['if']}"] = {
                    "final": alt_result["final"],
                    "collapse_at": alt_result.get("collapse_at_step"),
                    "vs_baseline": self._compare(baseline, alt_result)
                }
        
        return {
            "scenario": description,
            "baseline": {"final": baseline["final"], "collapse": baseline.get("collapse_at_step")},
            "what_if": scenarios,
        }
    
    def _compare(self, baseline: dict, alternative: dict) -> str:
        changes = []
        for var in baseline["final"]:
            b = baseline["final"][var]
            a = alternative["final"].get(var, b)
            if b > 0:
                diff = ((a - b) / b) * 100
                if abs(diff) > 5:
                    changes.append(f"{var}: {diff:+.0f}%")
        return " | ".join(changes) if changes else "无明显差异"


# 自检
if __name__ == "__main__":
    mp = MomoPredict()
    
    print("=" * 60)
    print("🔮 墨墨预测建模引擎 v1.0")
    print("=" * 60)
    
    # 系统动力学：复活节岛模拟
    print(f"\n🏝️ 复活节岛崩溃模拟:")
    result = mp.system_dynamics(
        {"树木": 100, "人口": 30, "石像(文明指标)": 20, "食物": 80},
        [
            {"from": "人口", "to": "树木", "effect": "消耗", "rate": 0.3},
            {"from": "树木", "to": "食物", "effect": "正向", "rate": 0.2},
            {"from": "食物", "to": "人口", "effect": "正向", "rate": 0.15},
            {"from": "人口", "to": "石像(文明指标)", "effect": "正向", "rate": 0.1},
            {"from": "树木", "to": "石像(文明指标)", "effect": "消耗", "rate": 0.05},
        ],
        50
    )
    print(f"  {result['墨墨的分析']}")
    if result.get("collapse_at_step"):
        print(f"  崩溃点: 第{result['collapse_at_step']}步")
    
    # 蒙特卡洛：投资回报
    print(f"\n📈 投资回报蒙特卡洛(10000次):")
    mc = mp.monte_carlo(
        {"年收益": 0.08, "年通胀": 0.03},
        {"年收益": ("normal", 0.08, 0.15), "年通胀": ("uniform", 0.02, 0.06)},
        10000
    )
    print(f"  {mc['墨墨的解释']}")
    
    print(f"\n✅ 预测建模引擎就绪")
