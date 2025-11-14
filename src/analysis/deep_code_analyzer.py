import ast
import re
from typing import Dict, List, Any
from collections import defaultdict

class DeepCodeAnalyzer:
    def __init__(self):
        pass
    
    def analyze_code_file(self, file_path: str, content: str, language: str) -> Dict[str, Any]:
        if not content or not content.strip():
            return {}
        analysis = {
            'file_path': file_path,
            'language': language,
            'oop_principles': {},
            'data_structures': {},
            'complexity_analysis': {},
            'optimization_evidence': [],
            'code_quality': {}
        }
        if language == 'Python':
            analysis.update(self._analyze_python_code(content, file_path))
        elif language == 'Java':
            analysis.update(self._analyze_java_code(content, file_path))
        elif language in ['JavaScript', 'TypeScript', 'React JSX', 'React TypeScript']:
            analysis.update(self._analyze_javascript_code(content, file_path))
        elif language == 'C++':
            analysis.update(self._analyze_cpp_code(content, file_path))
        analysis['data_structures'].update(self._detect_data_structures(content, language))
        analysis['complexity_analysis'].update(self._analyze_complexity_patterns(content))
        analysis['optimization_evidence'].extend(self._detect_optimizations(content))
        analysis['code_quality'].update(self._assess_code_quality(content, language))
        return analysis
    
    def _analyze_python_code(self, content: str, file_path: str) -> Dict[str, Any]:
        results = {
            'oop_principles': {
                'abstraction': [],
                'encapsulation': [],
                'polymorphism': [],
                'inheritance': []
            },
            'design_patterns': []
        }
        try:
            tree = ast.parse(content, filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    has_abstract = any(
                        isinstance(base, ast.Name) and 'Abstract' in base.id
                        for base in node.bases
                    ) or any(
                        isinstance(dec, ast.Name) and dec.id == 'abstractmethod'
                        for dec in node.decorator_list
                    )
                    if has_abstract:
                        results['oop_principles']['abstraction'].append({
                            'class': node.name,
                            'evidence': 'Abstract base class or abstract methods',
                            'line': node.lineno
                        })
                    private_attrs = [
                        n.name for n in ast.walk(node)
                        if isinstance(n, ast.Name) and n.name.startswith('_')
                    ]
                    if private_attrs:
                        results['oop_principles']['encapsulation'].append({
                            'class': node.name,
                            'private_members': len(private_attrs),
                            'evidence': f'Uses name mangling for {len(private_attrs)} private members',
                            'line': node.lineno
                        })
                    if node.bases:
                        results['oop_principles']['inheritance'].append({
                            'class': node.name,
                            'parent_classes': [self._get_base_name(b) for b in node.bases],
                            'evidence': f'Inherits from {len(node.bases)} class(es)',
                            'line': node.lineno
                        })
                    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                    if methods and node.bases:
                        results['oop_principles']['polymorphism'].append({
                            'class': node.name,
                            'methods': len(methods),
                            'evidence': 'Method definitions in inherited class (potential overriding)',
                            'line': node.lineno
                        })
                if isinstance(node, ast.FunctionDef):
                    if any(isinstance(d, ast.Name) and d.id in ['singleton', 'lru_cache'] 
                           for d in node.decorator_list):
                        results['design_patterns'].append({
                            'pattern': 'Singleton/Caching',
                            'location': node.name,
                            'line': node.lineno
                        })
        except SyntaxError:
            pass
        except Exception:
            pass
        return results
    
    def _analyze_java_code(self, content: str, file_path: str) -> Dict[str, Any]:
        results = {
            'oop_principles': {
                'abstraction': [],
                'encapsulation': [],
                'polymorphism': [],
                'inheritance': []
            }
        }
        abstract_class_pattern = r'\babstract\s+class\s+(\w+)'
        for match in re.finditer(abstract_class_pattern, content):
            results['oop_principles']['abstraction'].append({
                'class': match.group(1),
                'evidence': 'Abstract class declaration',
                'line': content[:match.start()].count('\n') + 1
            })
        interface_pattern = r'\binterface\s+(\w+)'
        for match in re.finditer(interface_pattern, content):
            results['oop_principles']['abstraction'].append({
                'interface': match.group(1),
                'evidence': 'Interface declaration (abstraction)',
                'line': content[:match.start()].count('\n') + 1
            })
        private_pattern = r'\bprivate\s+\w+\s+(\w+)'
        protected_pattern = r'\bprotected\s+\w+\s+(\w+)'
        private_count = len(re.findall(private_pattern, content))
        protected_count = len(re.findall(protected_pattern, content))
        if private_count > 0 or protected_count > 0:
            results['oop_principles']['encapsulation'].append({
                'evidence': f'Uses access modifiers: {private_count} private, {protected_count} protected',
                'count': private_count + protected_count
            })
        extends_pattern = r'class\s+(\w+)\s+extends\s+(\w+)'
        for match in re.finditer(extends_pattern, content):
            results['oop_principles']['inheritance'].append({
                'class': match.group(1),
                'parent': match.group(2),
                'evidence': f'Inherits from {match.group(2)}',
                'line': content[:match.start()].count('\n') + 1
            })
        override_count = len(re.findall(r'@Override', content))
        if override_count > 0:
            results['oop_principles']['polymorphism'].append({
                'evidence': f'Uses @Override annotation ({override_count} times)',
                'count': override_count
            })
        return results
    
    def _analyze_javascript_code(self, content: str, file_path: str) -> Dict[str, Any]:
        results = {
            'oop_principles': {
                'abstraction': [],
                'encapsulation': [],
                'polymorphism': [],
                'inheritance': []
            }
        }
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            parent = match.group(2)
            if parent:
                results['oop_principles']['inheritance'].append({
                    'class': class_name,
                    'parent': parent,
                    'evidence': f'ES6 class extends {parent}',
                    'line': content[:match.start()].count('\n') + 1
                })
        private_field_pattern = r'#\w+|this\._\w+'
        private_count = len(re.findall(private_field_pattern, content))
        if private_count > 0:
            results['oop_principles']['encapsulation'].append({
                'evidence': f'Uses private fields ({private_count} instances)',
                'count': private_count
            })
        interface_pattern = r'interface\s+(\w+)'
        for match in re.finditer(interface_pattern, content):
            results['oop_principles']['abstraction'].append({
                'interface': match.group(1),
                'evidence': 'TypeScript interface (abstraction)',
                'line': content[:match.start()].count('\n') + 1
            })
        abstract_pattern = r'abstract\s+class\s+(\w+)'
        for match in re.finditer(abstract_pattern, content):
            results['oop_principles']['abstraction'].append({
                'class': match.group(1),
                'evidence': 'Abstract class declaration',
                'line': content[:match.start()].count('\n') + 1
            })
        return results
    
    def _analyze_cpp_code(self, content: str, file_path: str) -> Dict[str, Any]:
        results = {
            'oop_principles': {
                'abstraction': [],
                'encapsulation': [],
                'polymorphism': [],
                'inheritance': []
            }
        }
        pure_virtual_pattern = r'virtual\s+\w+\s+\w+\s*\([^)]*\)\s*=\s*0'
        if re.search(pure_virtual_pattern, content):
            results['oop_principles']['abstraction'].append({
                'evidence': 'Pure virtual functions (abstract class)',
                'count': len(re.findall(pure_virtual_pattern, content))
            })
        private_section = len(re.findall(r'private:', content))
        protected_section = len(re.findall(r'protected:', content))
        if private_section > 0 or protected_section > 0:
            results['oop_principles']['encapsulation'].append({
                'evidence': f'Uses access specifiers: {private_section} private, {protected_section} protected',
                'count': private_section + protected_section
            })
        inheritance_pattern = r'class\s+(\w+)\s*:\s*(?:public|private|protected)\s+(\w+)'
        for match in re.finditer(inheritance_pattern, content):
            results['oop_principles']['inheritance'].append({
                'class': match.group(1),
                'parent': match.group(2),
                'evidence': f'Inherits from {match.group(2)}',
                'line': content[:match.start()].count('\n') + 1
            })
        virtual_pattern = r'virtual\s+\w+'
        virtual_count = len(re.findall(virtual_pattern, content))
        if virtual_count > 0:
            results['oop_principles']['polymorphism'].append({
                'evidence': f'Uses virtual functions ({virtual_count} instances)',
                'count': virtual_count
            })
        return results
    
    def _detect_data_structures(self, content: str, language: str) -> Dict[str, Any]:
        structures = {
            'hash_map': {'count': 0, 'evidence': [], 'performance_note': 'O(1) average lookup'},
            'list': {'count': 0, 'evidence': [], 'performance_note': 'O(n) search, O(1) append'},
            'set': {'count': 0, 'evidence': [], 'performance_note': 'O(1) average membership test'},
            'tree': {'count': 0, 'evidence': [], 'performance_note': 'O(log n) search'},
            'array': {'count': 0, 'evidence': [], 'performance_note': 'O(1) access, O(n) search'}
        }
        if language == 'Python':
            dict_patterns = [
                r'\bdict\s*\(', r'\{\s*\}', r'\.get\s*\(', r'\[.*\]\s*=\s*',
                r'from\s+collections\s+import\s+(defaultdict|OrderedDict|Counter)'
            ]
            for pattern in dict_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    structures['hash_map']['count'] += len(matches)
                    structures['hash_map']['evidence'].append(f'Dictionary/hash map usage: {pattern}')
            set_patterns = [r'\bset\s*\(', r'\{[^}]*\}', r'\.add\s*\(', r'\.discard\s*\(']
            for pattern in set_patterns:
                if re.search(pattern, content):
                    structures['set']['count'] += 1
                    structures['set']['evidence'].append('Set data structure')
            list_patterns = [r'\.append\s*\(', r'\.extend\s*\(', r'\[.*\]\s*=\s*\[', r'list\s*\(']
            for pattern in list_patterns:
                if re.search(pattern, content):
                    structures['list']['count'] += 1
        elif language in ['Java', 'C++']:
            hash_map_patterns = [
                r'HashMap\s*<', r'HashTable\s*<', r'HashSet\s*<',
                r'std::unordered_map', r'std::map\s*<'
            ]
            for pattern in hash_map_patterns:
                if re.search(pattern, content):
                    structures['hash_map']['count'] += 1
                    structures['hash_map']['evidence'].append(f'Hash map: {pattern}')
            list_patterns = [r'ArrayList\s*<', r'LinkedList\s*<', r'std::vector\s*<', r'std::list\s*<']
            for pattern in list_patterns:
                if re.search(pattern, content):
                    structures['list']['count'] += 1
        elif language in ['JavaScript', 'TypeScript']:
            if re.search(r'new\s+Map\s*\(', content) or re.search(r'Map\s*<', content):
                structures['hash_map']['count'] += 1
                structures['hash_map']['evidence'].append('JavaScript Map (hash map)')
            if re.search(r'new\s+Set\s*\(', content) or re.search(r'Set\s*<', content):
                structures['set']['count'] += 1
                structures['set']['evidence'].append('JavaScript Set')
        performance_insights = []
        if structures['hash_map']['count'] > structures['list']['count'] * 2:
            performance_insights.append({
                'observation': 'Prefers hash maps over lists for lookups',
                'implication': 'Demonstrates awareness of O(1) vs O(n) tradeoffs'
            })
        if structures['set']['count'] > 0:
            performance_insights.append({
                'observation': 'Uses sets for membership testing',
                'implication': 'Shows understanding of efficient data structures for unique collections'
            })
        return {
            'structures_detected': {k: v for k, v in structures.items() if v['count'] > 0},
            'performance_insights': performance_insights,
            'total_structures': sum(s['count'] for s in structures.values())
        }
    
    def _analyze_complexity_patterns(self, content: str) -> Dict[str, Any]:
        complexity = {
            'nested_loops': [],
            'recursive_functions': [],
            'complexity_indicators': [],
            'optimization_opportunities': []
        }
        lines = content.split('\n')
        loop_depth = 0
        for i, line in enumerate(lines, 1):
            loop_keywords = ['for', 'while', 'foreach', 'each', 'map', 'filter', 'reduce']
            line_loops = sum(1 for keyword in loop_keywords if re.search(rf'\b{keyword}\b', line, re.IGNORECASE))
            if line_loops > 0:
                loop_depth += line_loops
                if loop_depth >= 2:
                    complexity['nested_loops'].append({
                        'line': i,
                        'depth': loop_depth,
                        'potential_complexity': f'O(n^{loop_depth})',
                        'evidence': 'Nested loops detected'
                    })
            else:
                if '{' not in line and '}' not in line:
                    loop_depth = max(0, loop_depth - 1)
        recursive_patterns = [
            r'def\s+\w+.*:\s*.*\w+\s*\(',
            r'function\s+\w+.*\{[^}]*\w+\s*\(',
            r'\w+\s*\([^)]*\)\s*\{[^}]*\w+\s*\(',
        ]
        for pattern in recursive_patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                func_name = match.group(0).split('(')[0].split()[-1] if match.group(0) else 'unknown'
                if func_name in content[match.end():match.end()+200]:
                    complexity['recursive_functions'].append({
                        'function': func_name,
                        'evidence': 'Recursive function call detected',
                        'line': content[:match.start()].count('\n') + 1
                    })
        complexity_comments = re.findall(
            r'#.*[Oo]\([^)]+\)|//.*[Oo]\([^)]+\)|/\*.*[Oo]\([^)]+\).*\*/',
            content
        )
        if complexity_comments:
            complexity['complexity_indicators'].append({
                'evidence': 'Code includes complexity annotations',
                'count': len(complexity_comments),
                'examples': complexity_comments[:3]
            })
        sort_patterns = [r'\.sort\s*\(', r'sorted\s*\(', r'Arrays\.sort', r'std::sort']
        if any(re.search(p, content) for p in sort_patterns):
            complexity['complexity_indicators'].append({
                'evidence': 'Uses sorting algorithms (typically O(n log n))',
                'implication': 'Awareness of efficient sorting'
            })
        binary_search_patterns = [
            r'bisect\s*\.', r'BinarySearch', r'std::binary_search',
            r'left\s*=\s*mid|right\s*=\s*mid'
        ]
        if any(re.search(p, content) for p in binary_search_patterns):
            complexity['complexity_indicators'].append({
                'evidence': 'Binary search pattern (O(log n))',
                'implication': 'Demonstrates knowledge of efficient search algorithms'
            })
        return complexity
    
    def _detect_optimizations(self, content: str) -> List[Dict[str, Any]]:
        optimizations = []
        cache_patterns = [
            r'@lru_cache', r'@cache', r'memoize', r'cache\s*=', r'Memoization',
            r'std::unordered_map.*cache'
        ]
        if any(re.search(p, content, re.IGNORECASE) for p in cache_patterns):
            optimizations.append({
                'type': 'Caching/Memoization',
                'evidence': 'Uses caching to avoid redundant computations',
                'skill_indicator': 'Performance optimization awareness'
            })
        lazy_patterns = [r'lazy\s+load', r'defer', r'async\s+def', r'Promise\.']
        if any(re.search(p, content, re.IGNORECASE) for p in lazy_patterns):
            optimizations.append({
                'type': 'Lazy Loading/Async',
                'evidence': 'Uses lazy loading or asynchronous patterns',
                'skill_indicator': 'Resource optimization'
            })
        early_return_count = len(re.findall(r'if\s+.*:\s*return', content))
        if early_return_count > 3:
            optimizations.append({
                'type': 'Early Returns',
                'evidence': f'Uses early returns ({early_return_count} instances)',
                'skill_indicator': 'Code efficiency awareness'
            })
        if re.search(r'\.join\s*\(', content) and 'Python' in content:
            optimizations.append({
                'type': 'String Optimization',
                'evidence': 'Uses join() instead of string concatenation',
                'skill_indicator': 'Awareness of Python string performance'
            })
        return optimizations
    
    def _assess_code_quality(self, content: str, language: str) -> Dict[str, Any]:
        quality = {
            'error_handling': 0,
            'documentation': 0,
            'type_hints': 0,
            'testing': 0,
            'modularity': 0
        }
        error_patterns = {
            'Python': [r'try\s*:', r'except\s+', r'raise\s+', r'assert\s+'],
            'Java': [r'try\s*\{', r'catch\s*\(', r'throws\s+', r'assert\s+'],
            'JavaScript': [r'try\s*\{', r'catch\s*\(', r'throw\s+', r'\.catch\s*\('],
            'C++': [r'try\s*\{', r'catch\s*\(', r'throw\s+', r'assert\s*\(']
        }
        patterns = error_patterns.get(language, error_patterns['Python'])
        quality['error_handling'] = sum(len(re.findall(p, content)) for p in patterns)
        doc_patterns = [
            r'""".*"""', r"'''.*'''",
            r'/\*\*.*\*/', r'//.*',
            r'///.*'
        ]
        quality['documentation'] = sum(len(re.findall(p, content, re.DOTALL)) for p in doc_patterns)
        if language in ['Python', 'TypeScript']:
            type_hint_patterns = [
                r'->\s*\w+', r':\s*\w+',
                r':\s*\w+\s*[<{]', r'<\w+>'
            ]
            quality['type_hints'] = sum(len(re.findall(p, content)) for p in type_hint_patterns)
        test_patterns = [r'def\s+test_', r'@Test', r'describe\s*\(', r'it\s*\(']
        quality['testing'] = sum(len(re.findall(p, content, re.IGNORECASE)) for p in test_patterns)
        import_patterns = [r'import\s+', r'from\s+.*\s+import', r'#include', r'using\s+']
        quality['modularity'] = sum(len(re.findall(p, content)) for p in import_patterns)
        total_indicators = sum(quality.values())
        quality['overall_score'] = min(100, total_indicators * 2)
        return quality
    
    def _get_base_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_base_name(node.value)}.{node.attr}"
        return "unknown"
    
    def aggregate_analysis(self, file_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not file_analyses:
            return {}
        aggregated = {
            'oop_principles_summary': {
                'abstraction': {'count': 0, 'examples': []},
                'encapsulation': {'count': 0, 'examples': []},
                'polymorphism': {'count': 0, 'examples': []},
                'inheritance': {'count': 0, 'examples': []}
            },
            'data_structure_summary': defaultdict(int),
            'complexity_summary': {
                'nested_loops': 0,
                'recursive_functions': 0,
                'complexity_awareness': False
            },
            'optimization_summary': [],
            'code_quality_summary': {
                'average_quality_score': 0,
                'strengths': [],
                'areas_for_improvement': []
            }
        }
        total_quality = 0
        quality_count = 0
        for analysis in file_analyses:
            oop = analysis.get('oop_principles', {})
            for principle in ['abstraction', 'encapsulation', 'polymorphism', 'inheritance']:
                if principle in oop and oop[principle]:
                    aggregated['oop_principles_summary'][principle]['count'] += len(oop[principle])
                    aggregated['oop_principles_summary'][principle]['examples'].extend(
                        oop[principle][:2]
                    )
            ds = analysis.get('data_structures', {}).get('structures_detected', {})
            for struct_name, struct_data in ds.items():
                if isinstance(struct_data, dict) and 'count' in struct_data:
                    aggregated['data_structure_summary'][struct_name] += struct_data['count']
            complexity = analysis.get('complexity_analysis', {})
            aggregated['complexity_summary']['nested_loops'] += len(complexity.get('nested_loops', []))
            aggregated['complexity_summary']['recursive_functions'] += len(complexity.get('recursive_functions', []))
            if complexity.get('complexity_indicators'):
                aggregated['complexity_summary']['complexity_awareness'] = True
            optimizations = analysis.get('optimization_evidence', [])
            aggregated['optimization_summary'].extend(optimizations)
            quality = analysis.get('code_quality', {})
            if 'overall_score' in quality:
                total_quality += quality['overall_score']
                quality_count += 1
        if quality_count > 0:
            aggregated['code_quality_summary']['average_quality_score'] = total_quality / quality_count
        if aggregated['oop_principles_summary']['abstraction']['count'] > 0:
            aggregated['code_quality_summary']['strengths'].append('Uses abstraction')
        if aggregated['oop_principles_summary']['encapsulation']['count'] > 0:
            aggregated['code_quality_summary']['strengths'].append('Demonstrates encapsulation')
        if aggregated['complexity_summary']['complexity_awareness']:
            aggregated['code_quality_summary']['strengths'].append('Shows complexity awareness')
        if aggregated['optimization_summary']:
            aggregated['code_quality_summary']['strengths'].append('Implements optimizations')
        return aggregated
