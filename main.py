"""Main application GUI"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
import time
import subprocess
import webbrowser

from config import (
    BACKGROUND, SURFACE, PRIMARY, SECONDARY, ERROR, SUCCESS, WARNING,
    TEXT_PRIMARY, TEXT_SECONDARY, BUTTON_NORMAL, BUTTON_HOVER, BUTTON_TEXT,
    BUTTON_HOVER_TEXT, INPUT_BG, INPUT_TEXT, PDF_AVAILABLE, logger
)
from steganography_tools import SteganographyDetectionTools
from ai_components import OllamaManager, CrewAISteganographyDetector
from report_generator import PDFReportGenerator

class SteganographyDetectorApp:
    """Main application for AI-based steganography detection"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Steganography Detection System with Crew AI")
        self.root.geometry("1100x900")
        self.root.configure(bg=BACKGROUND)
        
        self.tools = SteganographyDetectionTools()
        self.ollama = OllamaManager()
        self.detector = CrewAISteganographyDetector(self.tools, self.ollama)
        self.current_analysis = None
        self.extraction_output_dir = None
        self.pdf_report_path = None
        
        self.setup_ui()
        self.check_ollama_status()
    
    def check_ollama_status(self):
        """Check and display Ollama status"""
        if self.detector.ollama.is_available:
            self.status_label.config(text="✅ Ollama Connected - AI Analysis Enabled", foreground=SUCCESS)
        else:
            self.status_label.config(text="⚠️ Ollama Not Available - Using Basic Analysis", foreground=WARNING)
    
    def safe_gui_update(self, func, *args, **kwargs):
        """Safely update GUI from thread"""
        try:
            if args and kwargs:
                self.root.after(0, lambda: func(*args, **kwargs))
            elif args:
                self.root.after(0, lambda: func(*args))
            elif kwargs:
                self.root.after(0, lambda: func(**kwargs))
            else:
                self.root.after(0, func)
        except Exception as e:
            logger.error(f"GUI update failed: {e}")
    
    def setup_ui(self):
        """Setup the user interface"""
        main_frame = tk.Frame(self.root, bg=BACKGROUND, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(main_frame, 
                               text="Steganography Detection System with Crew AI", 
                               font=('Arial', 16, 'bold'),
                               bg=BACKGROUND, fg=TEXT_PRIMARY)
        title_label.pack(pady=(0, 10))
        
        desc_text = ("Multi-Agent AI System with Ollama Integration\n"
                    "3 Specialized Agents: Scanner → Analyzer → Reporter\n"
                    "Automatic Payload Extraction to Output Folder")
        desc_label = tk.Label(main_frame, text=desc_text,
                              font=('Arial', 10), justify=tk.CENTER,
                              bg=BACKGROUND, fg=TEXT_PRIMARY)
        desc_label.pack(pady=(0, 20))
        
        source_frame = tk.LabelFrame(main_frame, text="Source Folder (Files to Scan)", 
                                    bg=BACKGROUND, fg=TEXT_PRIMARY,
                                    padx=10, pady=10)
        source_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.source_folder_path = tk.StringVar()
        tk.Label(source_frame, text="Source Folder:", 
                bg=BACKGROUND, fg=TEXT_PRIMARY).pack(side=tk.LEFT)
        
        source_entry = tk.Entry(source_frame, textvariable=self.source_folder_path, width=50,
                               bg=INPUT_BG, fg=INPUT_TEXT,
                               insertbackground=INPUT_TEXT)
        source_entry.pack(side=tk.LEFT, padx=(5, 5))
        
        browse_source_btn = tk.Button(source_frame, text="Browse", command=self.browse_source_folder,
                                     bg=BUTTON_NORMAL, fg=BUTTON_TEXT,
                                     activebackground=BUTTON_HOVER,
                                     activeforeground=BUTTON_HOVER_TEXT)
        browse_source_btn.pack(side=tk.LEFT)
        
        output_frame = tk.LabelFrame(main_frame, text="Output Folder (Extracted Files)",
                                    bg=BACKGROUND, fg=TEXT_PRIMARY,
                                    padx=10, pady=10)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.output_folder_path = tk.StringVar()
        tk.Label(output_frame, text="Output Folder:", 
                bg=BACKGROUND, fg=TEXT_PRIMARY).pack(side=tk.LEFT)
        
        output_entry = tk.Entry(output_frame, textvariable=self.output_folder_path, width=50,
                               bg=INPUT_BG, fg=INPUT_TEXT,
                               insertbackground=INPUT_TEXT)
        output_entry.pack(side=tk.LEFT, padx=(5, 5))
        
        browse_output_btn = tk.Button(output_frame, text="Browse", command=self.browse_output_folder,
                                     bg=BUTTON_NORMAL, fg=BUTTON_TEXT,
                                     activebackground=BUTTON_HOVER,
                                     activeforeground=BUTTON_HOVER_TEXT)
        browse_output_btn.pack(side=tk.LEFT)
        
        create_folder_btn = tk.Button(output_frame, text="Create New Folder", command=self.create_output_folder,
                                     bg=BUTTON_NORMAL, fg=BUTTON_TEXT,
                                     activebackground=BUTTON_HOVER,
                                     activeforeground=BUTTON_HOVER_TEXT)
        create_folder_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        control_frame = tk.Frame(main_frame, bg=BACKGROUND)
        control_frame.pack(pady=10)
        
        self.analyze_button = tk.Button(control_frame, text="Start CrewAI Analysis & Extraction", 
                                       command=self.start_analysis,
                                       bg=BUTTON_NORMAL, fg=BUTTON_TEXT,
                                       activebackground=BUTTON_HOVER,
                                       activeforeground=BUTTON_HOVER_TEXT)
        self.analyze_button.pack(side=tk.LEFT, padx=(0, 10))
        
        open_folder_btn = tk.Button(control_frame, text="Open Output Folder", command=self.open_output_folder,
                                   bg=BUTTON_NORMAL, fg=BUTTON_TEXT,
                                   activebackground=BUTTON_HOVER,
                                   activeforeground=BUTTON_HOVER_TEXT)
        open_folder_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.pdf_button = tk.Button(control_frame, text="Generate PDF Report", 
                                   command=self.generate_pdf_report, state=tk.DISABLED,
                                   bg=BUTTON_NORMAL, fg=BUTTON_TEXT,
                                   activebackground=BUTTON_HOVER,
                                   activeforeground=BUTTON_HOVER_TEXT)
        self.pdf_button.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = tk.Button(control_frame, text="Clear Results", command=self.clear_results,
                             bg=BUTTON_NORMAL, fg=BUTTON_TEXT,
                             activebackground=BUTTON_HOVER,
                             activeforeground=BUTTON_HOVER_TEXT)
        clear_btn.pack(side=tk.LEFT)
        
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(10, 5))
        
        self.status_label = tk.Label(main_frame, text="Select source and output folders to begin analysis",
                                    bg=BACKGROUND, fg=TEXT_PRIMARY)
        self.status_label.pack(pady=(5, 0))
        
        results_frame = tk.LabelFrame(main_frame, text="CrewAI Analysis Results",
                                     bg=BACKGROUND, fg=TEXT_PRIMARY,
                                     padx=10, pady=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.summary_tab = tk.Frame(self.notebook, bg=SURFACE)
        self.notebook.add(self.summary_tab, text="📊 Summary")
        
        self.summary_text = scrolledtext.ScrolledText(self.summary_tab, height=12, width=100, 
                                                     bg=SURFACE, fg=TEXT_PRIMARY,
                                                     insertbackground=TEXT_PRIMARY)
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.workflow_tab = tk.Frame(self.notebook, bg=SURFACE)
        self.notebook.add(self.workflow_tab, text="🤖 Agent Workflow")
        
        self.workflow_text = scrolledtext.ScrolledText(self.workflow_tab, height=12, width=100,
                                                      bg=SURFACE, fg=TEXT_PRIMARY,
                                                      insertbackground=TEXT_PRIMARY)
        self.workflow_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.extracted_tab = tk.Frame(self.notebook, bg=SURFACE)
        self.notebook.add(self.extracted_tab, text="📁 Extracted Files")
        
        self.extracted_text = scrolledtext.ScrolledText(self.extracted_tab, height=12, width=100,
                                                       bg=SURFACE, fg=TEXT_PRIMARY,
                                                       insertbackground=TEXT_PRIMARY)
        self.extracted_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def browse_source_folder(self):
        """Browse for source folder to scan"""
        folder = filedialog.askdirectory(title="Select source folder to scan for steganography")
        if folder:
            self.source_folder_path.set(folder)
            self.status_label.config(text=f"Source folder: {folder}")
    
    def browse_output_folder(self):
        """Browse for output folder"""
        folder = filedialog.askdirectory(title="Select output folder for extracted files")
        if folder:
            self.output_folder_path.set(folder)
            self.status_label.config(text=f"Output folder: {folder}")
    
    def create_output_folder(self):
        """Create a new output folder"""
        folder = filedialog.askdirectory(title="Select parent directory for new output folder")
        if folder:
            new_folder = filedialog.askstring("New Folder", "Enter folder name:")
            if new_folder:
                full_path = os.path.join(folder, new_folder)
                try:
                    os.makedirs(full_path, exist_ok=True)
                    self.output_folder_path.set(full_path)
                    self.status_label.config(text=f"Created output folder: {full_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not create folder: {e}")
    
    def open_output_folder(self):
        """Open the output folder in file explorer"""
        if self.output_folder_path.get() and os.path.exists(self.output_folder_path.get()):
            try:
                if sys.platform == "win32":
                    os.startfile(self.output_folder_path.get())
                elif sys.platform == "darwin":
                    subprocess.run(["open", self.output_folder_path.get()])
                else:
                    subprocess.run(["xdg-open", self.output_folder_path.get()])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder: {e}")
        else:
            messagebox.showwarning("Warning", "Please select a valid output folder first")
    
    def generate_pdf_report(self):
        """Generate and open PDF report"""
        if not self.current_analysis:
            messagebox.showwarning("Warning", "No analysis results available. Please run analysis first.")
            return
        
        if not PDF_AVAILABLE:
            messagebox.showerror("PDF Error", "PDF generation not available. Please install: pip install reportlab")
            return
        
        try:
            pdf_path = PDFReportGenerator.generate_pdf_report(
                self.current_analysis, 
                self.extraction_output_dir,
                self.source_folder_path.get()
            )
            
            if pdf_path and os.path.exists(pdf_path):
                self.pdf_report_path = pdf_path
                webbrowser.open(pdf_path)
                messagebox.showinfo("PDF Report", f"PDF report generated successfully!\n\nLocation: {pdf_path}")
            else:
                messagebox.showerror("PDF Error", f"Failed to generate PDF report: {pdf_path}")
                
        except Exception as e:
            messagebox.showerror("PDF Error", f"Failed to generate PDF: {str(e)}")
    
    def start_analysis(self):
        """Start the analysis process"""
        if not self.source_folder_path.get():
            messagebox.showerror("Error", "Please select a source folder to scan")
            return
        
        if not self.output_folder_path.get():
            messagebox.showerror("Error", "Please select an output folder for extracted files")
            return
        
        if not os.path.isdir(self.source_folder_path.get()):
            messagebox.showerror("Error", "Selected source folder does not exist")
            return
        
        if not os.path.exists(self.output_folder_path.get()):
            try:
                os.makedirs(self.output_folder_path.get())
            except Exception as e:
                messagebox.showerror("Error", f"Could not create output folder: {e}")
                return
        
        thread = threading.Thread(target=self.analyze_folder)
        thread.daemon = True
        thread.start()
    
    def analyze_folder(self):
        """Analyze all files in the selected folder using CrewAI orchestration"""
        try:
            self.safe_gui_update(self.analyze_button.config, state=tk.DISABLED)
            self.safe_gui_update(self.pdf_button.config, state=tk.DISABLED)
            self.safe_gui_update(self.progress.config, mode='determinate')
            
            source_folder = self.source_folder_path.get()
            output_folder = self.output_folder_path.get()
            all_files = []
            
            for root_dir, dirs, files in os.walk(source_folder):
                for file in files:
                    full_path = os.path.join(root_dir, file)
                    all_files.append(full_path)
            
            total_files = len(all_files)
            self.safe_gui_update(self.progress.config, maximum=total_files)
            
            results = {
                "clean_files": [],
                "suspicious_files": [],
                "confirmed_steg_files": [],
                "errors": [],
                "agent_workflow": [],
                "all_extracted_files": []
            }
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            analysis_output_dir = os.path.join(output_folder, f"steg_analysis_{timestamp}")
            os.makedirs(analysis_output_dir, exist_ok=True)
            
            for i, file_path in enumerate(all_files):
                self.safe_gui_update(self.status_label.config, 
                                   text=f"CrewAI Analyzing: {os.path.basename(file_path)} ({i+1}/{total_files})")
                
                try:
                    analysis_result = self.detector.analyze_file(file_path, analysis_output_dir)
                    results["agent_workflow"].append(analysis_result)
                    
                    verdict = analysis_result["final_report"]["final_verdict"]
                    
                    if verdict == "CONFIRMED":
                        results["confirmed_steg_files"].append(analysis_result)
                        extracted_files = analysis_result["analyzer_results"].get("extracted_files", [])
                        results["all_extracted_files"].extend(extracted_files)
                    elif verdict == "SUSPICIOUS":
                        results["suspicious_files"].append(analysis_result)
                    else:
                        results["clean_files"].append(analysis_result)
                
                except Exception as e:
                    results["errors"].append({
                        "file": file_path,
                        "error": str(e)
                    })
                
                self.safe_gui_update(self.progress.config, value=i + 1)
            
            self.save_analysis_report(results, analysis_output_dir)
            
            self.current_analysis = results
            self.extraction_output_dir = analysis_output_dir
            self.safe_gui_update(self.display_results, results, analysis_output_dir)
            self.safe_gui_update(self.status_label.config, 
                               text=f"CrewAI Analysis Complete: {total_files} files processed, {len(results['all_extracted_files'])} files extracted")
            self.safe_gui_update(self.pdf_button.config, state=tk.NORMAL)
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            error_msg = str(e)
            self.safe_gui_update(lambda: messagebox.showerror("Analysis Error", f"CrewAI analysis failed: {error_msg}"))
            self.safe_gui_update(lambda: self.status_label.config(text="Analysis failed"))
        finally:
            self.safe_gui_update(lambda: self.analyze_button.config(state=tk.NORMAL))
    
    def save_analysis_report(self, results: dict, output_dir: str):
        """Save detailed analysis report to file"""
        try:
            report_path = os.path.join(output_dir, "analysis_report.json")
            
            simplified_results = {
                "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "source_folder": self.source_folder_path.get(),
                "output_folder": output_dir,
                "summary": {
                    "total_files": len(results['clean_files']) + len(results['suspicious_files']) + len(results['confirmed_steg_files']),
                    "clean_files": len(results['clean_files']),
                    "suspicious_files": len(results['suspicious_files']),
                    "confirmed_steg_files": len(results['confirmed_steg_files']),
                    "errors": len(results['errors']),
                    "extracted_files": len(results['all_extracted_files'])
                },
                "extracted_files": [
                    {
                        "filename": f["filename"],
                        "type": f["type"],
                        "size": f["size"],
                        "path": f["path"]
                    }
                    for f in results['all_extracted_files']
                ],
                "confirmed_cases": [
                    {
                        "file": result['file_analyzed'],
                        "payload_size": result['analyzer_results']['extraction_results'].get('payload_size'),
                        "content_type": result['analyzer_results']['extraction_results'].get('content_type'),
                        "method": result['analyzer_results']['extraction_results'].get('method')
                    }
                    for result in results['confirmed_steg_files']
                ]
            }
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(simplified_results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Analysis report saved to: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to save analysis report: {e}")
    
    def display_results(self, results: dict, output_dir: str):
        """Display analysis results in the UI"""
        self.summary_text.delete(1.0, tk.END)
        
        self.summary_text.tag_configure("danger", foreground=ERROR, font=('Arial', 10, 'bold'))
        self.summary_text.tag_configure("warning", foreground=WARNING, font=('Arial', 10, 'bold'))
        self.summary_text.tag_configure("success", foreground=SUCCESS, font=('Arial', 10, 'bold'))
        self.summary_text.tag_configure("primary", foreground=TEXT_PRIMARY, font=('Arial', 10))
        self.summary_text.tag_configure("secondary", foreground=TEXT_SECONDARY, font=('Arial', 10))
        
        summary_content = f"""=== CREWAI STEGANOGRAPHY DETECTION REPORT ===
Analysis Date: {time.strftime("%Y-%m-%d %H:%M:%S")}
Source Folder: {self.source_folder_path.get()}
Output Folder: {output_dir}
AI System: CrewAI with {'Ollama' if self.detector.ollama.is_available else 'Basic Analysis'}

EXECUTIVE SUMMARY:
------------------
Total Files Processed: {len(results['clean_files']) + len(results['suspicious_files']) + len(results['confirmed_steg_files'])}
"""
        
        self.summary_text.insert(tk.END, summary_content, "primary")
        self.summary_text.insert(tk.END, f"Clean Files: {len(results['clean_files'])}\n", "success")
        self.summary_text.insert(tk.END, f"Suspicious Files: {len(results['suspicious_files'])}\n", "warning")
        self.summary_text.insert(tk.END, f"🚨 Confirmed Steganography: {len(results['confirmed_steg_files'])}\n", "danger")
        self.summary_text.insert(tk.END, f"Files Extracted: {len(results['all_extracted_files'])}\n", "primary")
        self.summary_text.insert(tk.END, f"Analysis Errors: {len(results['errors'])}\n\n", "primary")
        
        if results['confirmed_steg_files']:
            self.summary_text.insert(tk.END, "🚨 CONFIRMED STEGANOGRAPHY CASES:\n", "danger")
            for result in results['confirmed_steg_files']:
                file_path = result['file_analyzed']
                payload_info = result['analyzer_results']['extraction_results']
                self.summary_text.insert(tk.END, f"• {os.path.basename(file_path)}\n", "danger")
                self.summary_text.insert(tk.END, f"  📦 Payload: {payload_info.get('payload_size', 0)} bytes\n", "primary")
                self.summary_text.insert(tk.END, f"  📄 Type: {payload_info.get('content_type', 'Unknown')}\n", "primary")
                self.summary_text.insert(tk.END, f"  🔧 Method: {payload_info.get('method', 'Unknown')}\n", "primary")
                self.summary_text.insert(tk.END, f"  ✅ Extracted to: {output_dir}\n\n", "primary")
        
        self.summary_text.insert(tk.END, f"💾 All extracted files saved to: {output_dir}", "primary")
        
        self.workflow_text.delete(1.0, tk.END)
        workflow_info = "CREWAI AGENT WORKFLOW EXECUTION:\n\n"
        
        for i, workflow in enumerate(results["agent_workflow"][:10]):
            workflow_info += f"File: {os.path.basename(workflow['file_analyzed'])}\n"
            verdict = workflow['final_report']['final_verdict']
            workflow_info += f"Final Verdict: {verdict}\n"
            workflow_info += f"Agents Used: {', '.join(workflow['agents_used'])}\n"
            
            if workflow['final_report'].get('comprehensive_report'):
                report_preview = workflow['final_report']['comprehensive_report'][:200] + "..."
                workflow_info += f"AI Report: {report_preview}\n"
            
            workflow_info += "-" * 50 + "\n\n"
        
        self.workflow_text.insert(1.0, workflow_info)
        
        self.extracted_text.delete(1.0, tk.END)
        extracted_info = "EXTRACTED FILES DETAILS:\n\n"
        
        if results['all_extracted_files']:
            extracted_info += f"Output Directory: {output_dir}\n"
            extracted_info += f"Total Files Extracted: {len(results['all_extracted_files'])}\n\n"
            
            for file_info in results['all_extracted_files']:
                extracted_info += f"📄 {file_info['filename']}\n"
                extracted_info += f"   Type: {file_info['type']}\n"
                extracted_info += f"   Size: {file_info['size']:,} bytes\n"
                extracted_info += f"   Path: {file_info['path']}\n"
                extracted_info += "-" * 40 + "\n"
        else:
            extracted_info += "No files were extracted during this analysis.\n"
            extracted_info += "This could mean:\n"
            extracted_info += "• No steganography was detected\n"
            extracted_info += "• Files were suspicious but extraction failed\n"
            extracted_info += "• All files were clean\n"
        
        self.extracted_text.insert(1.0, extracted_info)
    
    def clear_results(self):
        """Clear all results"""
        self.summary_text.delete(1.0, tk.END)
        self.workflow_text.delete(1.0, tk.END)
        self.extracted_text.delete(1.0, tk.END)
        self.current_analysis = None
        self.pdf_report_path = None
        self.pdf_button.config(state=tk.DISABLED)
        self.status_label.config(text="Results cleared - select folders to analyze")

def main():
    """Main function to run the application"""
    try:
        # Check for required packages
        try:
            import requests
            import numpy as np
            from PIL import Image
        except ImportError as e:
            print(f"Missing required package: {e}")
            print("Please install: pip install requests numpy pillow")
            input("Press Enter to exit...")
            sys.exit(1)
        
        root = tk.Tk()
        app = SteganographyDetectorApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
