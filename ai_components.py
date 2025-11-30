"""AI and machine learning components for steganography detection"""
import os
import time
from typing import Dict, Any, List
from config import logger

class OllamaManager:
    """Manager for Ollama local LLM operations"""
    
    def __init__(self, model: str = "llama2"):
        self.model = model
        self.base_url = "http://localhost:11434"
        self.is_available = self.check_ollama_available()
    
    def check_ollama_available(self) -> bool:
        """Check if Ollama is running and available"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response using Ollama"""
        try:
            import requests
            
            data = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False
            }
            
            response = requests.post(f"{self.base_url}/api/generate", 
                                   json=data, timeout=30)
            
            if response.status_code == 200:
                return response.json().get("response", "No response generated")
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Ollama error: {str(e)}"

class CrewAISteganographyDetector:
    """Simplified CrewAI-style orchestration for steganography detection"""
    
    def __init__(self, tools, ollama_manager):
        self.ollama = ollama_manager
        self.tools = tools
        self.agents = self._initialize_agents()
    
    def _initialize_agents(self) -> Dict[str, Dict]:
        """Initialize the detection agents"""
        return {
            "scanner": {
                "name": "File Scanner Agent",
                "role": "Digital Forensics Scanner",
                "goal": "Perform initial file analysis using entropy and signature detection to identify suspicious files",
                "tools": ["file_entropy_analysis", "signature_based_detection"]
            },
            "analyzer": {
                "name": "Deep Analysis Agent", 
                "role": "Steganography Analysis Expert",
                "goal": "Perform deep analysis on suspicious files and extract hidden payloads",
                "tools": ["extract_simple_steg_payload"]
            },
            "reporter": {
                "name": "Report Generator Agent",
                "role": "Forensic Report Specialist", 
                "goal": "Generate comprehensive reports with findings and recommendations"
            }
        }
    
    def scanner_agent_task(self, file_path: str) -> Dict[str, Any]:
        """Scanner agent task - initial file analysis"""
        logger.info(f"Scanner Agent analyzing: {file_path}")
        
        entropy_results = self.tools.file_entropy_analysis(file_path)
        signature_results = self.tools.signature_based_detection(file_path)
        
        needs_deep_analysis = (
            not entropy_results.get("error") and 
            entropy_results.get("suspicion_level") in ["medium", "high"]
        ) or (
            not signature_results.get("error") and 
            signature_results.get("signature_count", 0) > 0
        )
        
        analysis_summary = ""
        if self.ollama.is_available:
            prompt = f"""
            Analyze these steganography detection results for file: {os.path.basename(file_path)}
            
            Entropy Analysis: {entropy_results}
            Signature Detection: {signature_results}
            
            Provide a brief technical assessment of whether this file appears suspicious for steganography.
            Focus on key indicators and confidence level.
            """
            
            analysis_summary = self.ollama.generate_response(
                prompt,
                "You are a digital forensics expert specializing in steganography detection."
            )
        
        return {
            "agent": "scanner",
            "file_path": file_path,
            "entropy_analysis": entropy_results,
            "signature_detection": signature_results,
            "needs_deep_analysis": needs_deep_analysis,
            "analysis_summary": analysis_summary,
            "confidence": "high" if needs_deep_analysis else "low"
        }
    
    def analyzer_agent_task(self, scanner_results: Dict, output_dir: str = None) -> Dict[str, Any]:
        """Analyzer agent task - deep analysis and payload extraction"""
        if not scanner_results["needs_deep_analysis"]:
            return {
                "agent": "analyzer",
                "action": "skipped",
                "reason": "No deep analysis needed based on scanner results"
            }
        
        file_path = scanner_results["file_path"]
        logger.info(f"Analyzer Agent performing deep analysis: {file_path}")
        
        extraction_results = self.tools.extract_simple_steg_payload(file_path, output_dir)
        
        payload_analysis = ""
        if self.ollama.is_available and extraction_results.get("success"):
            prompt = f"""
            Analyze this extracted steganography payload:
            
            File: {os.path.basename(file_path)}
            Payload Size: {extraction_results.get('payload_size')} bytes
            Content Type: {extraction_results.get('content_type', 'Unknown')}
            Method: {extraction_results.get('method')}
            Hash: {extraction_results.get('payload_hash')}
            
            Provide analysis of what type of content might be hidden and potential risks.
            """
            
            payload_analysis = self.ollama.generate_response(
                prompt,
                "You are a cybersecurity analyst specializing in analyzing hidden payloads and steganography content."
            )
        
        return {
            "agent": "analyzer",
            "file_path": file_path,
            "extraction_results": extraction_results,
            "payload_analysis": payload_analysis,
            "successful_extraction": extraction_results.get("success", False),
            "extracted_files": extraction_results.get("extracted_files", [])
        }
    
    def reporter_agent_task(self, scanner_results: Dict, analyzer_results: Dict) -> Dict[str, Any]:
        """Reporter agent task - generate final report"""
        logger.info("Reporter Agent generating final report")
        
        file_path = scanner_results["file_path"]
        final_verdict = "CONFIRMED" if analyzer_results.get("successful_extraction") else "SUSPICIOUS" if scanner_results["needs_deep_analysis"] else "CLEAN"
        
        comprehensive_report = ""
        if self.ollama.is_available:
            prompt = f"""
            Generate a comprehensive steganography detection report for: {os.path.basename(file_path)}
            
            SCANNER RESULTS:
            - Entropy Analysis: {scanner_results.get('entropy_analysis', {}).get('suspicion_level', 'N/A')}
            - Signature Detection: {scanner_results.get('signature_detection', {}).get('signature_count', 0)} signatures found
            - Initial Assessment: {scanner_results.get('analysis_summary', 'N/A')}
            
            ANALYZER RESULTS:
            - Extraction Success: {analyzer_results.get('successful_extraction', False)}
            - Payload Analysis: {analyzer_results.get('payload_analysis', 'N/A')}
            - Final Verdict: {final_verdict}
            
            Create a professional forensic report with:
            1. Executive Summary
            2. Technical Findings  
            3. Risk Assessment
            4. Recommendations
            """
            
            comprehensive_report = self.ollama.generate_response(
                prompt,
                "You are a professional digital forensics report writer. Create clear, technical yet accessible reports for both technical and non-technical audiences."
            )
        
        return {
            "agent": "reporter",
            "file_path": file_path,
            "final_verdict": final_verdict,
            "comprehensive_report": comprehensive_report,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "recommendations": self._generate_recommendations(final_verdict, analyzer_results)
        }
    
    def _generate_recommendations(self, verdict: str, analyzer_results: Dict) -> List[str]:
        """Generate actionable recommendations based on findings"""
        recommendations = []
        
        if verdict == "CONFIRMED":
            recommendations.extend([
                "🚨 STEGANOGRAPHY CONFIRMED: File contains hidden data",
                "Preserve original file as forensic evidence",
                "Analyze extracted payload for malicious content",
                "Investigate source and intent of hidden data",
                "Update security protocols to detect similar techniques"
            ])
        elif verdict == "SUSPICIOUS":
            recommendations.extend([
                "⚠️ SUSPICIOUS FILE: Requires further investigation",
                "Use additional steganography detection tools",
                "Consider manual forensic analysis",
                "Monitor file source and similar files",
                "Review security controls for file uploads/transfers"
            ])
        else:
            recommendations.extend([
                "✅ FILE APPEARS CLEAN: No steganography detected",
                "Maintain standard security monitoring",
                "Continue regular security practices"
            ])
        
        return recommendations
    
    def analyze_file(self, file_path: str, output_dir: str = None) -> Dict[str, Any]:
        """Orchestrate the complete analysis workflow"""
        logger.info(f"Starting CrewAI analysis for: {file_path}")
        
        scanner_results = self.scanner_agent_task(file_path)
        analyzer_results = self.analyzer_agent_task(scanner_results, output_dir)
        final_report = self.reporter_agent_task(scanner_results, analyzer_results)
        
        return {
            "file_analyzed": file_path,
            "workflow_phases": ["scanner", "analyzer", "reporter"],
            "scanner_results": scanner_results,
            "analyzer_results": analyzer_results,
            "final_report": final_report,
            "agents_used": list(self.agents.keys()),
            "extraction_output_dir": output_dir
        }