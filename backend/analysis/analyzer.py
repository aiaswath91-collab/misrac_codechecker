import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class MISRAAnalyzer:
    def __init__(self, source_dir: str):
        self.source_dir = Path(source_dir)
        self.c_files = []
        self.h_files = []
        self.all_violations = []
        
    def find_source_files(self):
        """Find all C/C++ source files"""
        self.c_files = list(self.source_dir.rglob("*.c"))
        self.c_files.extend(list(self.source_dir.rglob("*.cpp")))
        self.h_files = list(self.source_dir.rglob("*.h"))
        self.h_files.extend(list(self.source_dir.rglob("*.hpp")))
        
        all_files = self.c_files + self.h_files
        logger.info(f"Found {len(all_files)} source files")
        return all_files
    
    def run_cppcheck(self) -> List[Dict]:
        """Run Cppcheck with MISRA addon"""
        violations = []
        all_files = self.c_files + self.h_files
        
        if not all_files:
            return violations
        
        try:
            cmd = [
                "cppcheck",
                "--enable=all",
                "--inconclusive",
                "--suppress=missingIncludeSystem",
                "--template={file}|||{line}|||{severity}|||{id}|||{message}",
                str(self.source_dir)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            output = result.stderr + result.stdout
            
            for line in output.split('\n'):
                if '|||' in line:
                    try:
                        parts = line.split('|||')
                        if len(parts) >= 5:
                            file_path = parts[0].strip()
                            line_num = parts[1].strip()
                            severity = parts[2].strip()
                            rule_id = parts[3].strip()
                            message = parts[4].strip()
                            
                            relative_path = Path(file_path).relative_to(self.source_dir) if self.source_dir in Path(file_path).parents else Path(file_path).name
                            
                            violations.append({
                                "file": str(relative_path),
                                "line": int(line_num) if line_num.isdigit() else 0,
                                "severity": self._map_severity(severity),
                                "rule": self._map_to_misra_rule(rule_id),
                                "message": message,
                                "tool": "cppcheck",
                                "type": severity
                            })
                    except Exception as e:
                        logger.debug(f"Failed to parse line: {line}, error: {e}")
                        continue
            
            logger.info(f"Cppcheck found {len(violations)} issues")
            
        except subprocess.TimeoutExpired:
            logger.error("Cppcheck timeout")
        except Exception as e:
            logger.error(f"Cppcheck failed: {str(e)}")
        
        return violations
    
    def run_clang_tidy(self) -> List[Dict]:
        """Run Clang-Tidy"""
        violations = []
        
        for c_file in self.c_files:
            try:
                cmd = [
                    "clang-tidy",
                    str(c_file),
                    "--",
                    "-I" + str(self.source_dir)
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                output = result.stdout
                
                for line in output.split('\n'):
                    if ':' in line and 'warning:' in line or 'error:' in line:
                        try:
                            parts = line.split(':')
                            if len(parts) >= 4:
                                file_path = parts[0].strip()
                                line_num = parts[1].strip()
                                severity = 'warning' if 'warning' in line else 'error'
                                message = ':'.join(parts[3:]).strip()
                                
                                relative_path = Path(file_path).relative_to(self.source_dir) if self.source_dir in Path(file_path).parents else Path(file_path).name
                                
                                violations.append({
                                    "file": str(relative_path),
                                    "line": int(line_num) if line_num.isdigit() else 0,
                                    "severity": self._map_severity(severity),
                                    "rule": "MISRA C:2012 Rule 17.7",
                                    "message": message[:200],
                                    "tool": "clang-tidy",
                                    "type": severity
                                })
                        except Exception as e:
                            logger.debug(f"Failed to parse clang-tidy line: {e}")
                            continue
                
            except subprocess.TimeoutExpired:
                logger.warning(f"Clang-tidy timeout for {c_file}")
                continue
            except Exception as e:
                logger.debug(f"Clang-tidy failed for {c_file}: {e}")
                continue
        
        logger.info(f"Clang-tidy found {len(violations)} issues")
        return violations
    
    def _map_severity(self, severity: str) -> str:
        """Map tool severity to MISRA severity"""
        severity_lower = severity.lower()
        
        if severity_lower in ['error', 'critical']:
            return 'Required'
        elif severity_lower in ['warning', 'portability', 'performance']:
            return 'Required'
        else:
            return 'Advisory'
    
    def _map_to_misra_rule(self, rule_id: str) -> str:
        """Map tool rule ID to MISRA rule"""
        rule_mapping = {
            'unusedVariable': 'MISRA C:2012 Rule 2.7',
            'unusedFunction': 'MISRA C:2012 Rule 2.1',
            'uninitvar': 'MISRA C:2012 Rule 9.1',
            'nullPointer': 'MISRA C:2012 Rule 1.3',
            'memleak': 'MISRA C:2012 Rule 22.1',
            'resourceLeak': 'MISRA C:2012 Rule 22.1',
            'arrayIndexOutOfBounds': 'MISRA C:2012 Rule 18.1',
            'bufferAccessOutOfBounds': 'MISRA C:2012 Rule 18.1',
            'va_list_usedBeforeStarted': 'MISRA C:2012 Rule 17.1',
            'va_start_wrongParameter': 'MISRA C:2012 Rule 17.1',
            'uninitStructMember': 'MISRA C:2012 Rule 9.1',
            'functionStatic': 'MISRA C:2012 Rule 8.7',
            'variableScope': 'MISRA C:2012 Rule 8.7',
            'constParameter': 'MISRA C:2012 Rule 8.13',
            'constVariable': 'MISRA C:2012 Rule 8.13',
            'shadowVariable': 'MISRA C:2012 Rule 5.3',
            'duplicateCondition': 'MISRA C:2012 Rule 14.3',
            'identicalConditionAfterEarlyExit': 'MISRA C:2012 Rule 14.3',
            'knownConditionTrueFalse': 'MISRA C:2012 Rule 14.3',
            'comparePointers': 'MISRA C:2012 Rule 18.3',
            'literalWithCharPtrCompare': 'MISRA C:2012 Rule 18.3',
            'unusedStructMember': 'MISRA C:2012 Rule 2.3',
            'unusedLabel': 'MISRA C:2012 Rule 2.6',
            'cstyleCast': 'MISRA C:2012 Rule 10.8',
            'invalidPointerCast': 'MISRA C:2012 Rule 11.3',
            'missingReturn': 'MISRA C:2012 Rule 17.4',
            'wrongPrintfScanfArgNum': 'MISRA C:2012 Rule 21.6',
            'invalidScanfArgType_int': 'MISRA C:2012 Rule 21.6',
        }
        
        return rule_mapping.get(rule_id, f'MISRA C:2012 Rule {rule_id}')
    
    def deduplicate_violations(self, violations: List[Dict]) -> List[Dict]:
        """Remove duplicate violations"""
        seen = set()
        unique_violations = []
        
        for v in violations:
            key = (v['file'], v['line'], v['rule'])
            if key not in seen:
                seen.add(key)
                unique_violations.append(v)
        
        return unique_violations
    
    def generate_statistics(self, violations: List[Dict]) -> Dict:
        """Generate summary statistics"""
        file_stats = defaultdict(lambda: {
            'messages': 0,
            'error': 0,
            'warning': 0,
            'info': 0,
            'note': 0,
            'mandatory': 0,
            'required': 0,
            'advisory': 0
        })
        
        for v in violations:
            file_name = v['file']
            file_stats[file_name]['messages'] += 1
            
            vtype = v.get('type', 'note').lower()
            if vtype in file_stats[file_name]:
                file_stats[file_name][vtype] += 1
            else:
                file_stats[file_name]['note'] += 1
            
            severity = v['severity'].lower()
            if severity in file_stats[file_name]:
                file_stats[file_name][severity] += 1
        
        total_violations = len(violations)
        total_files = len(self.c_files) + len(self.h_files)
        
        total_lines = 0
        for f in self.c_files + self.h_files:
            try:
                with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                    total_lines += len(file.readlines())
            except:
                pass
        
        severity_counts = {
            'mandatory': sum(1 for v in violations if v['severity'] == 'Mandatory'),
            'required': sum(1 for v in violations if v['severity'] == 'Required'),
            'advisory': sum(1 for v in violations if v['severity'] == 'Advisory')
        }
        
        return {
            'files_analyzed': total_files,
            'lines_analyzed': total_lines,
            'total_violations': total_violations,
            'severity_counts': severity_counts,
            'file_stats': dict(file_stats)
        }
    
    def analyze(self) -> Dict:
        """Run complete analysis"""
        self.find_source_files()
        
        if not self.c_files and not self.h_files:
            raise Exception("No C/C++ source files found in the uploaded archive")
        
        violations = []
        violations.extend(self.run_cppcheck())
        
        violations = self.deduplicate_violations(violations)
        
        violations.sort(key=lambda x: (x['file'], x['line']))
        
        statistics = self.generate_statistics(violations)
        
        return {
            'violations': violations,
            'summary': statistics
        }


def run_analysis(source_dir: str) -> Dict:
    """Main analysis function"""
    analyzer = MISRAAnalyzer(source_dir)
    return analyzer.analyze()
