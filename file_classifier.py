import os
import json
from pathlib import Path

class FileClassifier:
    """文件分类器"""
    
    def __init__(self):
        self.categories = {
            "发票类": {
                "keywords": ["发票", "税票", "收据", "开票", "税额", "金额", "购买方", "销售方"],
                "description": "包含发票、税票、收据等财务相关文档"
            },
            "合同类": {
                "keywords": ["合同", "协议", "结算", "审定书", "建设", "施工", "甲方", "乙方"],
                "description": "包含合同、协议、结算书等法律文档"
            },
            "证书类": {
                "keywords": ["证书", "资质", "许可", "认证", "等保", "测评", "资格"],
                "description": "包含各类证书、资质、许可证等证明文档"
            },
            "其他类": {
                "keywords": [],
                "description": "无法明确分类的其他文档"
            }
        }
    
    def analyze_sample_files(self, output_dir="output"):
        """分析样例文件"""
        if not os.path.exists(output_dir):
            print(f"输出目录不存在: {output_dir}")
            return
        
        analysis_result = {
            "total_files": 0,
            "categories": {cat: [] for cat in self.categories.keys()},
            "classification_details": []
        }
        
        print("=== 文件分类分析 ===\n")
        
        for folder_name in os.listdir(output_dir):
            folder_path = os.path.join(output_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue
            
            # 查找markdown文件
            md_files = list(Path(folder_path).glob("*.md"))
            if not md_files:
                continue
            
            md_file = md_files[0]
            analysis_result["total_files"] += 1
            
            # 分析文件内容
            category, confidence, details = self.classify_file(folder_name, md_file)
            
            analysis_result["categories"][category].append({
                "folder": folder_name,
                "file": md_file.name,
                "confidence": confidence
            })
            
            analysis_result["classification_details"].append({
                "folder": folder_name,
                "category": category,
                "confidence": confidence,
                "details": details
            })
            
            print(f"文件夹: {folder_name}")
            print(f"分类: {category} (置信度: {confidence:.2f})")
            print(f"关键特征: {', '.join(details['matched_keywords'])}")
            print("-" * 50)
        
        # 打印分类统计
        self.print_classification_summary(analysis_result)
        
        # 保存分析结果
        self.save_analysis_result(analysis_result)
        
        return analysis_result
    
    def classify_file(self, folder_name, md_file):
        """分类单个文件"""
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
        except:
            content = ""
        
        # 将文件夹名也包含在分析中
        full_text = (folder_name + " " + content).lower()
        
        best_category = "其他类"
        best_score = 0
        best_details = {"matched_keywords": [], "keyword_count": 0}
        
        for category, info in self.categories.items():
            if category == "其他类":
                continue
                
            matched_keywords = []
            score = 0
            
            for keyword in info["keywords"]:
                if keyword in full_text:
                    matched_keywords.append(keyword)
                    score += 1
            
            # 计算置信度
            confidence = score / len(info["keywords"]) if info["keywords"] else 0
            
            if confidence > best_score:
                best_score = confidence
                best_category = category
                best_details = {
                    "matched_keywords": matched_keywords,
                    "keyword_count": score
                }
        
        # 如果没有匹配到任何关键词，归为其他类
        if best_score == 0:
            best_category = "其他类"
            best_score = 1.0  # 其他类的置信度设为1.0
        
        return best_category, best_score, best_details
    
    def print_classification_summary(self, analysis_result):
        """打印分类汇总"""
        print("\n=== 分类汇总 ===")
        total = analysis_result["total_files"]
        
        for category, files in analysis_result["categories"].items():
            count = len(files)
            percentage = (count / total * 100) if total > 0 else 0
            print(f"{category}: {count}个文件 ({percentage:.1f}%)")
            
            if files:
                print(f"  描述: {self.categories[category]['description']}")
                for file_info in files:
                    print(f"  - {file_info['folder']} (置信度: {file_info['confidence']:.2f})")
            print()
    
    def save_analysis_result(self, analysis_result, filename="file_classification_analysis.json"):
        """保存分析结果"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)
            print(f"分析结果已保存到: {filename}")
        except Exception as e:
            print(f"保存分析结果失败: {e}")
    
    def get_category_examples(self):
        """获取分类示例"""
        examples = {}
        for category, info in self.categories.items():
            examples[category] = {
                "description": info["description"],
                "keywords": info["keywords"],
                "example_prompt": self.generate_example_prompt(category)
            }
        return examples
    
    def generate_example_prompt(self, category):
        """生成示例提示语"""
        prompts = {
            "发票类": "请识别这张发票的关键信息，包括开票日期、金额、购买方和销售方信息",
            "合同类": "请提取合同中的甲乙双方信息、合同金额和主要条款",
            "证书类": "请识别证书的类型、颁发机构、有效期和相关资质信息",
            "其他类": "请识别文档中的所有重要文字内容和关键信息"
        }
        return prompts.get(category, "请识别文档内容")

def main():
    classifier = FileClassifier()
    
    print("文件分类器 - 分析output文件夹中的样例文件\n")
    
    # 分析样例文件
    result = classifier.analyze_sample_files()
    
    # 显示分类示例
    print("\n=== 分类提示语示例 ===")
    examples = classifier.get_category_examples()
    for category, info in examples.items():
        print(f"\n{category}:")
        print(f"  描述: {info['description']}")
        print(f"  关键词: {', '.join(info['keywords']) if info['keywords'] else '无特定关键词'}")
        print(f"  音频提示语示例: {info['example_prompt']}")

if __name__ == "__main__":
    main()
