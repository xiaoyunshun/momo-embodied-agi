"""
预测引擎 v2 · 模型校准闭环
不是跑一遍就完——校准→预测→对比→修正。
"""
import json, math, random
from pathlib import Path
from momo_predict import MomoPredict

class MomoPredictV2(MomoPredict):
    """预测引擎 v2——带模型校准和自我修正。
    
    闭环：假设参数→跑推演→对比历史数据→调整参数→再推演
    """
    
    def calibrate(self, variables: dict, rules: list, history: list, steps: int = 200) -> dict:
        """校准模型参数——让推演拟合历史数据。
        
        history: [{"step": 1, "A": 100, "B": 50}, {"step": 2, "A": 95, "B": 48}, ...]
        """
        best_params = None
        best_error = float('inf')
        
        # 简单网格搜索——尝试不同的rate值
        for trial in range(50):
            # 给每个rule的rate加随机扰动
            test_rules = []
            for rule in rules:
                r = {**rule}
                if "rate" in r:
                    r["rate"] *= random.uniform(0.5, 2.0)
                test_rules.append(r)
            
            # 跑推演
            result = self.system_dynamics(variables, test_rules, len(history)-1)
            
            # 计算跟历史数据的误差
            error = self._compute_error(result["history"], history)
            
            if error < best_error:
                best_error = error
                best_params = {"rules": test_rules, "error": error}
        
        # 用最佳参数跑完整推演
        if best_params:
            calibrated_result = self.system_dynamics(variables, best_params["rules"], steps)
            
            # 生成预测区间
            forecast = self._generate_forecast(calibrated_result, history)
            
            return {
                "calibration_error": round(best_error, 2),
                "trials": 50,
                "history_fit": "良好" if best_error < 10 else ("一般" if best_error < 50 else "差"),
                "calibrated_forecast": forecast,
                "墨墨的判断": self._calibration_insight(best_error, calibrated_result)
            }
        
        return {"error": "校准失败"}
    
    def _compute_error(self, simulated: list, actual: list) -> float:
        """计算模拟和实际之间的误差"""
        if len(simulated) != len(actual):
            return float('inf')
        
        total_error = 0
        for s, a in zip(simulated, actual):
            for var in a:
                if var in s and var != "step":
                    actual_val = a[var]
                    sim_val = s[var]
                    if actual_val > 0:
                        total_error += abs(sim_val - actual_val) / actual_val
        
        return (total_error / (len(simulated) * max(1, len(actual[0])-1))) * 100
    
    def _generate_forecast(self, result: dict, history: list) -> dict:
        """基于校准模型生成预测"""
        forecast = {}
        history_steps = len(history)
        
        for var in result["final"]:
            if var == "step": continue
            current = result["final"][var]
            history_trend = self._trend_from_history(history, var)
            
            forecast[var] = {
                "current": current,
                "history_trend": history_trend,
                "confidence": "高" if history_trend in ("上升", "下降") else "中"
            }
        
        return forecast
    
    def _trend_from_history(self, history: list, var: str) -> str:
        """从历史数据提取趋势"""
        vals = [h.get(var, 0) for h in history if var in h]
        if len(vals) < 3: return "数据不足"
        
        first_half = sum(vals[:len(vals)//2]) / max(1, len(vals)//2)
        second_half = sum(vals[len(vals)//2:]) / max(1, len(vals) - len(vals)//2)
        
        diff = (second_half - first_half) / max(1, abs(first_half)) * 100
        if diff > 5: return "上升"
        if diff < -5: return "下降"
        return "稳定"
    
    def _calibration_insight(self, error: float, result: dict) -> str:
        if error < 10:
            return f"模型拟合良好(误差{error:.1f}%)——推演可靠。关键变量趋势：{result.get('trends',{})}"
        elif error < 50:
            return f"模型拟合一般(误差{error:.1f}%)——趋势方向可靠但幅度可能偏差。建议收集更多数据后重新校准。"
        return f"模型拟合差(误差{error:.1f}%)——系统可能存在模型未包含的关键变量。建议重新检查系统结构。"


# 自检
if __name__ == "__main__":
    mp = MomoPredictV2()
    
    print("=" * 60)
    print("🔮 预测引擎 v2 · 闭环校准")
    print("=" * 60)
    
    # 模拟历史数据
    history = [
        {"step": 0, "安全": 100, "事故": 0},
        {"step": 1, "安全": 95, "事故": 5},
        {"step": 2, "安全": 88, "事故": 9},
        {"step": 3, "安全": 79, "事故": 15},
        {"step": 4, "安全": 68, "事故": 22},
        {"step": 5, "安全": 55, "事故": 30},
    ]
    
    result = mp.calibrate(
        {"安全": 100, "事故": 0},
        [{"from": "事故", "to": "安全", "effect": "消耗", "rate": 0.2}],
        history,
        10
    )
    
    print(f"\n📊 校准结果: {result['calibration_error']}% ({result['history_fit']})")
    print(f"\n{result['墨墨的判断'][:120]}...")
    print(f"\n✅ 预测引擎 v2 闭环就绪")
