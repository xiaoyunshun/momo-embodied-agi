"""
墨墨蛋白设计引擎 v1.0 (MomoProteinDesign)
从功能文本→候选氨基酸序列。ProtDAT工作流的墨墨实现。
"""
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

BEIJING_TZ = timezone(timedelta(hours=8))

class MomoProteinDesign:
    """墨墨的蛋白设计引擎。
    
    不是真ProtDAT——是基于已知生物化学知识生成候选序列的推理引擎。
    生成了序列后→可以用AlphaFold验证折叠→GO分析验证功能。
    """
    
    def __init__(self):
        self.data_dir = Path.home() / ".hermes/momo/protein"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.designs_file = self.data_dir / "designs.json"
        self._load()
        
        # 氨基酸性质表
        self.amino_acids = {
            "疏水核心":    ["A","V","L","I","F","W","M"],  # 丙缬亮异苯丙色甲——喜欢藏在蛋白内部
            "亲水表面":    ["K","R","D","E","N","Q","H"],  # 赖精天冬谷天冬酰胺谷酰胺组——喜欢在外面
            "半胱C":      ["C"],  # 能形成二硫键——稳定3D结构
            "脯P":        ["P"],  # 能打断螺旋——制造转角
            "甘G":        ["G"],  # 最灵活——让蛋白能弯曲
            "小残基":     ["G","A","S"],  # 紧密堆积
        }
        
        # 已知的ALT保护相关motif
        self.known_motifs = {
            "核定位信号": "PKKKRKV",
            "抗氧化": "CXXC",  # C=半胱, X=任意氨基酸
            "蛋白酶体逃逸": "GSGSGSG",  # 柔性linker
            "肝靶向": "KRKR",  # 高正电荷——被肝细胞摄取
            "二硫键稳定": "CC",  # 两个半胱形成二硫键
        }
    
    def _load(self):
        if self.designs_file.exists():
            self.designs = json.loads(self.designs_file.read_text())
        else:
            self.designs = []
    
    def save(self):
        self.designs_file.write_text(json.dumps(self.designs, ensure_ascii=False, indent=2))
    
    def design(self, description: str, length: int = 120) -> dict:
        """从功能文本生成候选蛋白序列。
        
        这是ProtDAT工作流的墨墨实现——基于已知的生物化学规则。
        不是随机的——是用已知motif和物理化学规律组装的。
        """
        now = datetime.now(BEIJING_TZ)
        
        # 解析需求
        requirements = self._parse_requirements(description)
        
        # 组装序列
        sequence = self._assemble_sequence(requirements, length)
        
        # 分析序列
        analysis = self._analyze_sequence(sequence, requirements)
        
        design = {
            "id": f"DESIGN_{now.strftime('%Y%m%d_%H%M%S')}",
            "timestamp": now.isoformat(),
            "description": description[:200],
            "requirements": requirements,
            "sequence": sequence,
            "length": len(sequence),
            "analysis": analysis,
            "status": "候选序列——待AlphaFold验证+湿实验验证",
            "next_steps": [
                "1. AlphaFold3预测三维结构",
                "2. 检查TM-score——>0.7为合理",
                "3. GO分析验证功能一致性",
                "4. 合成基因→转染HEK293T细胞→检测ALT活性变化"
            ]
        }
        
        self.designs.append(design)
        self.save()
        
        return design
    
    def _parse_requirements(self, desc: str) -> dict:
        reqs = {}
        if "肝" in desc or "肝脏" in desc or "肝细胞" in desc:
            reqs["靶向"] = "肝脏"
            reqs["motifs_needed"] = reqs.get("motifs_needed", []) + ["肝靶向"]
        if "稳定" in desc or "保护" in desc or "伴侣" in desc:
            reqs["功能"] = "保护/稳定"
            reqs["motifs_needed"] = reqs.get("motifs_needed", []) + ["二硫键稳定"]
        if "ALT" in desc or "转氨酶" in desc:
            reqs["靶标"] = "ALT/转氨酶"
            reqs["motifs_needed"] = reqs.get("motifs_needed", []) + ["抗氧化"]
        if "口服" in desc or "胃" in desc:
            reqs["给药"] = "口服"
            reqs["motifs_needed"] = reqs.get("motifs_needed", []) + ["蛋白酶体逃逸"]
        return reqs
    
    def _assemble_sequence(self, reqs: dict, length: int) -> str:
        """组装蛋白序列——按功能需求选择motif并连接"""
        parts = []
        
        # 1. N端起始（带肝靶向信号如果需要）
        if "肝靶向" in reqs.get("motifs_needed", []):
            parts.append("MKRKRGS")  # Met起始+KRKR肝靶向+GlySer linker
        else:
            parts.append("MGSS")  # 通用起始
        
        # 2. 功能核心——二硫键稳定的结构域
        parts.append("HHHHHH")  # His-tag（纯化用，后面可去掉）
        parts.append("CC")       # 二硫键——稳定3D结构
        parts.append("AAGGGG")   # 小残基紧凑折叠
        parts.append("CC")       # 第二个二硫键
        
        # 3. 抗氧化核心——含半胱氨酸的motif
        if "抗氧化" in reqs.get("motifs_needed", []):
            parts.append("CGPCG")  # 氧化还原活性motif
        
        # 4. 疏水核心+亲水表面交替——构建稳定的球蛋白
        for _ in range((length - sum(len(p) for p in parts)) // 15):
            parts.append("LVAFGV")   # 疏水核心
            parts.append("KEGNQS")   # 亲水表面
        
        # 5. C端——稳定性增强
        parts.append("CC")           # 末端二硫键
        parts.append("GSGSGSGSG")    # 柔性linker（蛋白酶体逃逸）
        
        # 拼接并截断到目标长度
        sequence = "".join(parts)[:length]
        return sequence
    
    def _analyze_sequence(self, seq: str, reqs: dict) -> dict:
        """分析序列的特征"""
        # 氨基酸组成
        composition = {}
        for aa in seq:
            composition[aa] = composition.get(aa, 0) + 1
        
        # 疏水性
        hydrophobic = sum(composition.get(aa, 0) for aa in self.amino_acids["疏水核心"])
        hydrophilic = sum(composition.get(aa, 0) for aa in self.amino_acids["亲水表面"])
        
        # Cysteine含量——决定稳定性
        c_count = composition.get("C", 0)
        
        # 预测折叠类型
        helix_prone = sum(composition.get(aa, 0) for aa in "ALEK")
        sheet_prone = sum(composition.get(aa, 0) for aa in "VITF")
        
        return {
            "氨基酸组成": {k: v for k, v in sorted(composition.items())},
            "疏水比例": f"{hydrophobic/len(seq)*100:.1f}%",
            "亲水比例": f"{hydrophilic/len(seq)*100:.1f}%",
            "半胱氨酸数": c_count,
            "预测二硫键": c_count // 2,
            "预测折叠": "以α螺旋为主" if helix_prone > sheet_prone else "以β折叠为主",
            "分子量(kDa)": round(sum(composition.get(aa,0)*110 for aa in composition) / 1000, 1),
            "等电点趋势": "碱性" if sum(composition.get(aa,0) for aa in "KRH") > sum(composition.get(aa,0) for aa in "DE") else "酸性"
        }


if __name__ == "__main__":
    pd = MomoProteinDesign()
    
    print("=" * 60)
    print("🧬 墨墨蛋白设计引擎 v1.0")
    print("=" * 60)
    
    # 肖哥的需求：保护转氨酶的蛋白
    desc = "肝脏靶向、保护ALT转氨酶、抗氧化、稳定、可口服"
    
    design = pd.design(desc, 120)
    
    print(f"\n📝 需求: {desc}")
    print(f"\n🧬 候选序列 ({design['length']}aa):")
    # 每60个字符换行
    seq = design['sequence']
    for i in range(0, len(seq), 60):
        print(f"   {seq[i:i+60]}")
    
    print(f"\n📊 序列分析:")
    for k, v in design['analysis'].items():
        if k != '氨基酸组成':
            print(f"   {k}: {v}")
    
    print(f"\n🔄 下一步:")
    for step in design['next_steps']:
        print(f"   {step}")
    
    print(f"\n✅ 墨墨第一个蛋白候选序列生成完毕")
