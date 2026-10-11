from abc import ABC, abstractmethod


class BaseAgent(ABC):
    def __init__(self, name, rag):
        self.name = name
        self.rag = rag
        self.results = {}

    @abstractmethod
    def analyze(self, context):
        pass

    def run(self, queries):
        print(f"\n🤖 Running: {self.name}")
        parts = [self.rag.get_context(q, top_k=3) for q in queries]
        context = "\n\n".join(parts)
        self.results = self.analyze(context)
        print(f"✅ {self.name} done")
        return self.results

    def show(self):
        print(f"\n📊 {self.name}")
        print("-" * 50)
        for key, val in self.results.items():
            if isinstance(val, list):
                print(f"\n{key} ({len(val)}):")
                for item in val[:8]:
                    if isinstance(item, dict):
                        print("  •", " | ".join(f"{k}: {v}" for k, v in item.items()))
                    else:
                        print("  •", item)
            elif isinstance(val, dict):
                print(f"\n{key}:")
                for k, v in val.items():
                    print(f"  • {k}: {v}")
            else:
                print(f"\n{key}: {val}")
