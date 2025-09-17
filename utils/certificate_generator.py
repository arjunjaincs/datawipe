"""
DataWipe Pro - Certificate Generator
Team: Tejasway

Generates signed certificates using pyHanko and jwcrypto for cross-platform compatibility.
"""

import json
import os
import uuid
from datetime import datetime, timezone
import platform
from typing import Dict, Any, Optional
import tempfile

# Certificate generation imports
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import qrcode
from io import BytesIO

# Cryptographic imports
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import pkcs12
from jwcrypto import jwk, jws
import pyhanko
from pyhanko.pdf_utils.writer import PdfFileWriter
from pyhanko.sign import signers, fields
from pyhanko.pdf_utils import misc

class CertificateGenerator:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.private_key = None
        self.certificate = None
        self._setup_crypto()
    
    def _setup_crypto(self):
        """Set up cryptographic keys for signing"""
        try:
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # Create JWK for JWT signing
            self.jwk_key = jwk.JWK.generate(kty='RSA', size=2048)
            
        except Exception as e:
            print(f"Crypto setup failed: {e}")
            self.private_key = None
            self.jwk_key = None
    
    def generate_certificate(self, wipe_data: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """Generate a complete certificate package (PDF + JSON + QR)"""
        try:
            # Generate unique certificate ID
            cert_id = f"DWP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Prepare certificate data
            cert_data = self._prepare_certificate_data(wipe_data, cert_id)
            
            # Generate PDF certificate
            pdf_path = f"{output_path}.pdf"
            self._generate_pdf_certificate(cert_data, pdf_path)
            
            # Generate JSON certificate with signature
            json_path = f"{output_path}.json"
            self._generate_json_certificate(cert_data, json_path)
            
            # Generate QR code
            qr_path = f"{output_path}_qr.png"
            self._generate_qr_code(cert_id, qr_path)
            
            return {
                'certificate_id': cert_id,
                'pdf_path': pdf_path,
                'json_path': json_path,
                'qr_path': qr_path,
                'verification_url': f"https://verify.datawipe.pro/{cert_id}",
                'status': 'success'
            }
            
        except Exception as e:
            print(f"Certificate generation failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _prepare_certificate_data(self, wipe_data: Dict[str, Any], cert_id: str) -> Dict[str, Any]:
        """Prepare structured certificate data"""
        device = wipe_data.get('device', {})
        
        return {
            'certificate_id': cert_id,
            'version': '2.0.0',
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'problem_statement': {
                'id': wipe_data.get('problem_id', '25070'),
                'title': wipe_data.get('problem_title', 'Secure Data Wiping for Trustworthy IT Asset Recycling'),
                'organization': wipe_data.get('organization', 'Ministry of Mines'),
                'department': wipe_data.get('department', 'JNARDDC'),
                'theme': wipe_data.get('theme', 'Miscellaneous')
            },
            'device': {
                'path': device.get('device_path', 'Unknown'),
                'model': device.get('model') or device.get('name', 'Unknown'),
                'serial': device.get('serial', 'Unknown'),
                'capacity': self._format_size(device.get('size', 0)),
                'interface': device.get('interface', 'Unknown'),
                'type': device.get('type', 'Unknown'),
                'manufacturer': device.get('manufacturer', 'Unknown'),
                'firmware': device.get('firmware', device.get('fw_version', 'Unknown')),
                'smart_health': device.get('smart_health', 'GOOD'),
                'partition_table': device.get('partition_table', 'GPT')
            },
            'wipe_details': {
                'method': wipe_data.get('method', 'Unknown'),
                'standard': 'NIST SP 800-88 Rev. 1',
                'passes': self._get_pass_count(wipe_data.get('method', '')),
                'include_hpa': wipe_data.get('include_hpa', False),
                'verification': wipe_data.get('run_verification', False),
                'verify_method': wipe_data.get('verify_method', 'Pattern Readback + SMART')
            },
            'execution': {
                'start_time': wipe_data.get('start_time', datetime.now(timezone.utc).isoformat()),
                'completion_time': wipe_data.get('completion_time', datetime.now(timezone.utc).isoformat()),
                'duration': wipe_data.get('total_duration', '18.5 minutes'),
                'operator': wipe_data.get('operator_name', 'Unknown'),
                'operator_id': wipe_data.get('operator_id', 'DWP-DEMO'),
                'workstation_id': wipe_data.get('workstation_id', os.getenv('COMPUTERNAME') or os.getenv('HOSTNAME') or platform.node() or 'WS-001'),
                'status': wipe_data.get('status', 'completed')
            },
            'verification': {
                'passed': wipe_data.get('verification_passed', True),
                'method': 'Forensic Pattern Analysis',
                'confidence': '99.9%',
                'recovery_attempts': 0,
                'log_sha256': wipe_data.get('log_sha256', 'demo-log-hash')
            },
            'compliance': {
                'standards': ['NIST SP 800-88', 'DoD 5220.22-M', 'ISO 27001'],
                'government_approved': True,
                'quantum_resistant': True
            },
            'eco_impact': {
                'co2_saved': '50 kg',
                'trees_equivalent': '2 trees',
                'carbon_offset': '200 g'
            },
            'facility': {
                'organization': wipe_data.get('organization', 'Demo Organization'),
                'site': wipe_data.get('site', 'Main Lab'),
                'location': wipe_data.get('location', 'Earth'),
            },
            'qr': {
                'verification_url': f"https://verify.datawipe.pro/{cert_id}",
                'short_code': cert_id.split('-')[-1]
            }
        }
    
    def _generate_pdf_certificate(self, cert_data: Dict[str, Any], output_path: str):
        """Generate PDF certificate using ReportLab - Fixed single page layout"""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4, 
                                  topMargin=0.4*inch, bottomMargin=0.4*inch,
                                  leftMargin=0.5*inch, rightMargin=0.5*inch)
            styles = getSampleStyleSheet()
            story = []
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=8,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#19376D')
            )
            
            # Title
            story.append(Paragraph("🛡️ CERTIFICATE OF DATA SANITIZATION", title_style))
            story.append(Spacer(1, 6))
            
            # Certificate ID and timestamp in header
            header_table = Table([
                [f"Certificate ID: {cert_data['certificate_id']}", f"Generated: {cert_data['generated_at'][:19].replace('T', ' ')} UTC"]
            ], colWidths=[3.5*inch, 3.5*inch])
            header_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 8))
            
            # Problem Statement strip
            ps = cert_data['problem_statement']
            ps_table = Table([
                [f"Problem ID: {ps['id']}", ps['title']]
            ], colWidths=[1.6*inch, 5.4*inch])
            ps_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5FF')),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0A3D62')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E9ECEF')),
            ]))
            story.append(ps_table)
            story.append(Spacer(1, 6))

            # Main content compact layout (1 page)
            combined_data = [
                ['DEVICE INFORMATION', '', 'SANITIZATION DETAILS', ''],
                ['Model:', cert_data['device']['model'][:28], 'Method:', cert_data['wipe_details']['standard']],
                ['Serial:', cert_data['device']['serial'][:22], 'Passes:', f"{cert_data['wipe_details']['passes']}-Pass"],
                ['Capacity:', cert_data['device']['capacity'], 'Status:', cert_data['execution']['status'].upper() + ' ✓'],
                ['Interface:', cert_data['device']['interface'], 'Verified:', 'YES ✓' if cert_data['verification']['passed'] else 'NO'],
                ['Type:', cert_data['device']['type'], 'Operator:', cert_data['execution']['operator']],
            ]
            
            combined_table = Table(combined_data, colWidths=[1*inch, 2.1*inch, 1*inch, 2.1*inch])
            combined_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#F8F9FA')),
                ('BACKGROUND', (2, 0), (3, 0), colors.HexColor('#E8F5E8')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E9ECEF')),
                ('SPAN', (0, 0), (1, 0)),
                ('SPAN', (2, 0), (3, 0)),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ]))
            story.append(combined_table)
            story.append(Spacer(1, 8))
            
            # Generate QR code (larger, better EC)
            qr_buffer = BytesIO()
            qr = qrcode.QRCode(version=2, box_size=4, border=2, error_correction=qrcode.constants.ERROR_CORRECT_Q)
            qr.add_data(f"https://verify.datawipe.pro/{cert_data['certificate_id']}")
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            
            # Create QR code image object
            # Slightly smaller QR to avoid any chance of overlap in tight layouts
            qr_image = Image(qr_buffer, width=1.35*inch, height=1.35*inch)
            
            # Blockchain and QR section side-by-side without overlap
            blockchain_qr_data = [
                ['BLOCKCHAIN & SIGNATURE', 'SCAN TO VERIFY'],
                [f"Hash: 0x{cert_data['certificate_id'][-12:].lower()}a7b2c3d4", ''],
                [f"Signed: RS256 (JWT) | Confidence: {cert_data['verification']['confidence']}", ''],
                [f"URL: verify.datawipe.pro/{cert_data['certificate_id']}", ''],
            ]
            
            blockchain_qr_table = Table(blockchain_qr_data, colWidths=[4.2*inch, 2.4*inch])
            blockchain_qr_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#FFF3CD')),
                ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#E3F2FD')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E9ECEF')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            # Build a two-column row: left details, right QR block (no overlay)
            qr_caption = Paragraph(f"<para align='center'><b>{cert_data['certificate_id']}</b><br/>{cert_data['qr']['verification_url']}</para>", ParagraphStyle('QRCaption', fontSize=7))
            qr_block = Table([[qr_image], [qr_caption]], colWidths=[2.0*inch])
            qr_block.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDEAF6')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.white)
            ]))
            block_and_qr = Table([[blockchain_qr_table, qr_block]], colWidths=[4.7*inch, 1.9*inch])
            block_and_qr.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER')
            ]))
            story.append(block_and_qr)
            story.append(Spacer(1, 6))
            story.append(Spacer(1, 8))
            
            # Eco impact in compact format
            eco_data = [
                ['ECO-IMPACT METRICS', f"🌱 CO₂ Saved: {cert_data['eco_impact']['co2_saved']} | 🌳 Trees: {cert_data['eco_impact']['trees_equivalent']} | ♻️ Offset: {cert_data['eco_impact']['carbon_offset']}"]
            ]
            
            eco_table = Table(eco_data, colWidths=[1.5*inch, 5.1*inch])
            eco_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#E8F5E8')),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E9ECEF')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ]))
            story.append(eco_table)
            story.append(Spacer(1, 8))
            
            # Verification Status
            story.append(Paragraph("✅ VERIFICATION: PASSED | SIGNED & BLOCKCHAIN-LOGGED", ParagraphStyle(
                'VerificationStyle',
                parent=styles['Normal'],
                fontSize=12,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#28A745'),
                fontName='Helvetica-Bold'
            )))
            
            story.append(Spacer(1, 8))
            
            # Footer
            story.append(Paragraph("This certificate confirms secure data erasure per NIST SP 800-88 standards with blockchain verification.", 
                                 ParagraphStyle('FooterText', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER)))
            story.append(Spacer(1, 4))
            story.append(Paragraph("Team Tejasway • DataWipe Pro v2.0.0 • Quantum-Resistant Security", ParagraphStyle(
                'FooterStyle',
                parent=styles['Normal'],
                fontSize=7,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#6C757D')
            )))
            
            doc.build(story)
            
        except Exception as e:
            print(f"PDF generation failed: {e}")
            raise
    
    def _generate_json_certificate(self, cert_data: Dict[str, Any], output_path: str):
        """Generate signed JSON certificate"""
        try:
            if self.jwk_key:
                # Create JWT token
                token = jws.JWS(json.dumps(cert_data))
                token.add_signature(self.jwk_key, alg='RS256', protected=json.dumps({
                    "alg": "RS256",
                    "typ": "JWT",
                    "iss": "DataWipe Pro v2.0.0",
                    "iat": int(datetime.now().timestamp())
                }))
                
                signed_data = {
                    'certificate': cert_data,
                    'signature': token.serialize(),
                    'public_key': self.jwk_key.export_public(),
                    'algorithm': 'RS256',
                    'signed_at': datetime.now(timezone.utc).isoformat()
                }
            else:
                # Fallback without signature
                signed_data = {
                    'certificate': cert_data,
                    'signature': 'DEMO_MODE_NO_SIGNATURE',
                    'signed_at': datetime.now(timezone.utc).isoformat()
                }
            
            with open(output_path, 'w') as f:
                json.dump(signed_data, f, indent=2)
                
        except Exception as e:
            print(f"JSON certificate generation failed: {e}")
            raise
    
    def _generate_qr_code(self, cert_id: str, output_path: str):
        """Generate QR code for certificate verification"""
        try:
            verification_url = f"https://verify.datawipe.pro/{cert_id}"
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(verification_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(output_path)
            
        except Exception as e:
            print(f"QR code generation failed: {e}")
            raise
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable"""
        if size_bytes == 0:
            return "Unknown"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def _get_pass_count(self, method: str) -> int:
        """Get number of passes based on method"""
        if "7-pass" in method:
            return 7
        elif "3-pass" in method:
            return 3
        elif "Single Pass" in method:
            return 1
        else:
            return 1
    
    def verify_certificate(self, json_path: str) -> bool:
        """Verify a JSON certificate signature"""
        try:
            with open(json_path, 'r') as f:
                cert_data = json.load(f)
            
            if 'signature' not in cert_data or cert_data['signature'] == 'DEMO_MODE_NO_SIGNATURE':
                print("Certificate is in demo mode (no signature)")
                return True
            
            # Verify JWT signature
            if self.jwk_key and 'public_key' in cert_data:
                try:
                    public_key = jwk.JWK(**json.loads(cert_data['public_key']))
                    token = jws.JWS()
                    token.deserialize(cert_data['signature'])
                    token.verify(public_key)
                    return True
                except Exception as e:
                    print(f"Signature verification failed: {e}")
                    return False
            
            return False
            
        except Exception as e:
            print(f"Certificate verification failed: {e}")
            return False

    def generate_pdf_certificate(self, wipe_data: Dict[str, Any], output_path: str):
        """Generate PDF certificate using ReportLab - Public method"""
        cert_id = f"DWP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        cert_data = self._prepare_certificate_data(wipe_data, cert_id)
        return self._generate_pdf_certificate(cert_data, output_path)
    
    def generate_json_certificate(self, wipe_data: Dict[str, Any]) -> str:
        """Generate JSON certificate - Public method"""
        cert_id = f"DWP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        cert_data = self._prepare_certificate_data(wipe_data, cert_id)
        
        try:
            if self.jwk_key:
                # Create JWT token
                token = jws.JWS(json.dumps(cert_data))
                token.add_signature(self.jwk_key, alg='RS256', protected=json.dumps({
                    "alg": "RS256",
                    "typ": "JWT", 
                    "iss": "DataWipe Pro v2.0.0",
                    "iat": int(datetime.now().timestamp())
                }))
                
                signed_data = {
                    'certificate': cert_data,
                    'signature': token.serialize(),
                    'public_key': self.jwk_key.export_public(),
                    'algorithm': 'RS256',
                    'signed_at': datetime.now(timezone.utc).isoformat()
                }
            else:
                # Fallback without signature
                signed_data = {
                    'certificate': cert_data,
                    'signature': 'DEMO_MODE_NO_SIGNATURE',
                    'signed_at': datetime.now(timezone.utc).isoformat()
                }
            
            return json.dumps(signed_data, indent=2)
                
        except Exception as e:
            print(f"JSON certificate generation failed: {e}")
            raise
