## Steganography Detection System with Crew AI

A sophisticated Python-based steganography detection system that uses multi-agent AI orchestration to identify and extract hidden data from files. The system employs three specialized AI agents (Scanner, Analyzer, and Reporter) working together to provide comprehensive digital forensics analysis.

#### Features

###### Core Capabilities

* Multi-Agent AI System: Three specialized agents working in orchestration
* Advanced Detection: Entropy analysis and signature-based detection
* Payload Extraction: Automatic extraction of hidden files and data
* AI-Powered Analysis: Integration with Ollama for intelligent analysis
* Comprehensive Reporting: Detailed PDF reports with risk assessment
* User-Friendly GUI: Modern interface with real-time progress tracking

##### Detection Methods

* Entropy Analysis: Detect anomalies in file byte distribution
* Signature Detection: Identify known steganography markers
* Size Anomaly Detection: Spot file size discrepancies
* Custom Steganography: Support for custom marker-based steganography

#### Installation

###### Prerequisites

* Python 3.8 or higher
* Ollama (optional, for AI analysis)

###### Required Packages

*pip install requests numpy pillow reportlab*

###### Optional AI Integration

*# Install Ollama for AI-powered analysis*

*# Download from: https://ollama.ai/*

*ollama pull llama2*

#### Usage

###### Running the Application

1. Start the GUI Application:

&nbsp;	*python main.py*

2\. Configure Analysis:

* Select source folder containing files to scan
* Choose output folder for extracted files
* Click "Start CrewAI Analysis \& Extraction"

3\. Review Results:

* View summary in the Summary tab
* Monitor agent workflow in Agent Workflow tab
* Check extracted files in Extracted Files tab
* Generate PDF reports with detailed findings

##### Command Line Usage (Optional)

The system can also be used programmatically:



*from main import CrewAISteganographyDetector*

*# Initialize detector*

*detector = CrewAISteganographyDetector()*
*# Analyze single file*
*results = detector.analyze\_file("suspicious\_file.jpg", "output\_folder")*
*# Analyze entire directory*
*for file\_path in folder\_files:*

    *analysis = detector.analyze\_file(file\_path, "output\_folder")*





#### Configuration

###### AI Agent Configuration

The system uses three specialized agents:

1. Scanner Agent: Performs initial file analysis using entropy and signature detection
2. Analyzer Agent: Conducts deep analysis and payload extraction
3. Reporter Agent: Generates comprehensive reports and recommendations



###### Ollama Integration

To enable AI-powered analysis:

1. Install Ollama from https://ollama.ai/
2. Pull a model: ollama pull llama2
3. The system will automatically detect and use Ollama when available

#### Output

###### Generated Files

* Extracted Payloads: Hidden files recovered during analysis
* JSON Reports: Detailed analysis results in JSON format
* PDF Reports: Professional forensic reports with risk assessment
* Original Cover Files: Recovered original files when applicable

###### Report Contents

* Executive summary with risk assessment
* Technical findings and analysis
* Extracted file details
* AI-generated recommendations
* Timestamped analysis records

#### Supported File Types

The system can analyze various file types including:

* Images (JPEG, PNG, BMP)
* Documents (PDF, DOCX)
* Archives (ZIP)
* Generic binary files
* Custom steganography formats

#### Detection Techniques

###### Entropy Analysis

* Calculates Shannon entropy of file bytes
* Identifies encrypted or compressed content
* Normalized scoring (0-1 scale)

###### Signature Detection

* Custom steganography markers (STEG\_MARKER\_v2\_)
* Embedded file signatures (ZIP, PDF, etc.)
* File size anomaly detection

###### Payload Extraction

* Automatic extraction of hidden files
* Checksum verification
* Content type identification

#### GUI Features

###### Modern Interface

* Light theme with optimal contrast
* Real-time progress tracking
* Tabbed results organization
* One-click folder operations

###### Interactive Elements

* Source and output folder selection
* Progress bars for long operations
* PDF report generation
* Direct folder access buttons

#### Performance

* Multi-threaded analysis for large directories
* Progress tracking for each file
* Memory-efficient processing
* Configurable output locations

#### Security Features

* Checksum verification for extracted files
* Secure temporary file handling
* Comprehensive error logging
* Safe GUI updates from background threads

#### Future Enhancements

* Additional steganography algorithm support
* Network-based analysis capabilities
* Enhanced AI model integration
* Batch processing optimizations
* Cloud storage integration

#### Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:

* New detection algorithms
* UI/UX improvements
* Performance optimizations
* Additional file format support

#### License

This project is open source and available under the MIT License.

#### Disclaimer

This tool is intended for educational, research, and authorized security testing purposes only. Users are responsible for complying with all applicable laws and regulations regarding digital forensics and data privacy.

**Note:** Always ensure you have proper authorization before analyzing files that you do not own or have explicit permission to examine.

**Author: Bright Machaya**

If you find this project useful, please give it a star ⭐

