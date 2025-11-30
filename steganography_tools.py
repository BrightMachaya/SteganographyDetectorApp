"""Steganography detection and analysis tools"""
import os
import hashlib
import struct
from pathlib import Path
from typing import Dict, Any
import numpy as np
from collections import Counter
import tempfile
import shutil
from config import logger

class SimpleSteganography:
    """Steganography implementation"""
    
    @staticmethod
    def extract_file(encoded_path, output_dir):
        """Extract hidden file from encoded file"""
        try:
            with open(encoded_path, 'rb') as f:
                data = f.read()
            
            marker = b'STEG_MARKER_v2_'
            if marker not in data:
                return None, None, "No hidden file found - invalid marker"
            
            marker_pos = data.index(marker)
            original_cover_data = data[:marker_pos]
            secret_section = data[marker_pos + len(marker):]
            
            header_size = struct.unpack('<I', secret_section[:4])[0]
            header_data = secret_section[4:4 + header_size]
            secret_data = secret_section[4 + header_size:]
            
            filename_size = struct.unpack('<I', header_data[:4])[0]
            secret_filename = header_data[4:4 + filename_size].decode('utf-8')
            expected_size = struct.unpack('<Q', header_data[4 + filename_size:12 + filename_size])[0]
            checksum = header_data[12 + filename_size:44 + filename_size]
            
            if len(secret_data) != expected_size:
                return None, None, f"Size mismatch: expected {expected_size} bytes, got {len(secret_data)} bytes"
            
            actual_checksum = hashlib.md5(secret_data).digest()
            if actual_checksum != checksum:
                return None, None, "File corrupted - checksum mismatch"
            
            secret_output_path = os.path.join(output_dir, secret_filename)
            with open(secret_output_path, 'wb') as f:
                f.write(secret_data)
            
            cover_output_path = os.path.join(output_dir, f"original_{os.path.basename(encoded_path)}")
            with open(cover_output_path, 'wb') as f:
                f.write(original_cover_data)
            
            return secret_output_path, cover_output_path, f"Successfully extracted {secret_filename}"
            
        except Exception as e:
            return None, None, f"Extraction failed: {str(e)}"

class SteganographyDetectionTools:
    """Tool collection for steganography detection and analysis"""
    
    @staticmethod
    def file_entropy_analysis(file_path: str) -> Dict[str, Any]:
        """Calculate file entropy and detect anomalies"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            if len(data) == 0:
                return {"error": "Empty file"}
            
            byte_counts = Counter(data)
            file_size = len(data)
            entropy = 0.0
            
            for count in byte_counts.values():
                p_x = count / file_size
                if p_x > 0:
                    entropy += -p_x * np.log2(p_x)
            
            normalized_entropy = entropy / 8.0
            
            suspicion_level = "low"
            if normalized_entropy > 0.95:
                suspicion_level = "high"
            elif normalized_entropy > 0.85:
                suspicion_level = "medium"
            
            return {
                "file_path": file_path,
                "file_size": file_size,
                "entropy": entropy,
                "normalized_entropy": normalized_entropy,
                "suspicion_level": suspicion_level,
                "byte_distribution": dict(byte_counts.most_common(10))
            }
        except Exception as e:
            return {"error": f"Entropy analysis failed: {str(e)}"}
    
    @staticmethod
    def signature_based_detection(file_path: str) -> Dict[str, Any]:
        """Detect known steganography signatures and markers"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            signatures = {
                "simple_steg_marker": b'STEG_MARKER_v2_',
                "zip_header": b'PK\x03\x04',
                "pdf_header": b'%PDF',
            }
            
            detected_signatures = []
            
            if signatures["simple_steg_marker"] in data:
                detected_signatures.append({
                    "type": "simple_steg_marker",
                    "confidence": "high",
                    "description": "Detected custom steganography marker"
                })
            
            for sig_name, signature in signatures.items():
                if signature in data and sig_name != "simple_steg_marker":
                    detected_signatures.append({
                        "type": "embedded_file",
                        "confidence": "medium",
                        "description": f"Detected {sig_name.upper()} signature"
                    })
            
            file_size = len(data)
            expected_size = len(data)
            if expected_size > 0:
                size_discrepancy = abs(file_size - expected_size) / expected_size
                if size_discrepancy > 0.1:
                    detected_signatures.append({
                        "type": "size_anomaly",
                        "confidence": "medium",
                        "description": f"File size anomaly: {size_discrepancy:.2%} discrepancy"
                    })
            
            return {
                "file_path": file_path,
                "detected_signatures": detected_signatures,
                "signature_count": len(detected_signatures),
                "overall_confidence": "high" if detected_signatures else "low"
            }
            
        except Exception as e:
            return {"error": f"Signature detection failed: {str(e)}"}
    
    @staticmethod
    def extract_simple_steg_payload(file_path: str, output_dir: str = None) -> Dict[str, Any]:
        """Extract payload using the custom steganography method"""
        try:
            if output_dir is None:
                temp_dir = tempfile.mkdtemp()
                extract_dir = temp_dir
                is_temp = True
            else:
                extract_dir = output_dir
                is_temp = False
            
            secret_path, cover_path, message = SimpleSteganography.extract_file(file_path, extract_dir)
            extracted_files = []
            
            if secret_path and os.path.exists(secret_path):
                with open(secret_path, 'rb') as f:
                    payload_data = f.read()
                
                secret_filename = os.path.basename(secret_path)
                
                payload_info = {
                    "success": True,
                    "method": "simple_steganography",
                    "payload_size": len(payload_data),
                    "payload_preview": payload_data[:100].hex(),
                    "payload_hash": hashlib.md5(payload_data).hexdigest(),
                    "file_extension": Path(secret_path).suffix,
                    "filename": secret_filename,
                    "extracted_path": secret_path,
                    "message": message
                }
                
                extracted_files.append({
                    "type": "hidden_file",
                    "path": secret_path,
                    "filename": secret_filename,
                    "size": len(payload_data)
                })
                
                if payload_data.startswith(b'PK'):
                    payload_info["content_type"] = "ZIP Archive"
                elif payload_data.startswith(b'%PDF'):
                    payload_info["content_type"] = "PDF Document"
                elif payload_data.startswith(b'\x89PNG'):
                    payload_info["content_type"] = "PNG Image"
                elif payload_data.startswith(b'\xFF\xD8'):
                    payload_info["content_type"] = "JPEG Image"
                else:
                    try:
                        text_content = payload_data[:500].decode('utf-8', errors='ignore')
                        if any(keyword in text_content.lower() for keyword in ['the', 'and', 'is', 'to']):
                            payload_info["content_type"] = "Text Content"
                    except:
                        payload_info["content_type"] = "Binary Data"
            
            if cover_path and os.path.exists(cover_path):
                cover_stats = os.stat(cover_path)
                extracted_files.append({
                    "type": "original_cover",
                    "path": cover_path,
                    "filename": os.path.basename(cover_path),
                    "size": cover_stats.st_size
                })
            
            if is_temp and temp_dir:
                shutil.rmtree(temp_dir)
            
            payload_info["extracted_files"] = extracted_files
            return payload_info
                    
        except Exception as e:
            return {
                "success": False,
                "method": "simple_steganography",
                "error": str(e)
            }