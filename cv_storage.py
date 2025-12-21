"""
Sharp Recruiter - CV & Transcript Storage Module
=================================================
Handles file uploads, parsing, and storage for CVs and interview transcripts.

Usage:
    from cv_storage import CVStorage, TranscriptStorage
    
    # Upload and parse a CV
    cv_storage = CVStorage(user_id)
    result = cv_storage.upload_and_parse(file_bytes, filename)
    
    # Search CVs
    results = cv_storage.search("python machine learning")
"""

import os
import re
import json
import requests
from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple
from io import BytesIO

# PDF parsing
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

# DOCX parsing
try:
    from docx import Document as DocxDocument
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

# Supabase config
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://qkjtprqgblnfftrotyks.supabase.co")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Storage bucket names
CV_BUCKET = "cv-files"
TRANSCRIPT_BUCKET = "transcript-files"


# ============================================
# TEXT EXTRACTION
# ============================================

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF file."""
    if not HAS_PDFPLUMBER:
        raise ImportError("pdfplumber not installed. Run: pip install pdfplumber")
    
    text_parts = []
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    
    return "\n\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX file."""
    if not HAS_DOCX:
        raise ImportError("python-docx not installed. Run: pip install python-docx")
    
    doc = DocxDocument(BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Extract text from plain text file."""
    try:
        return file_bytes.decode('utf-8')
    except UnicodeDecodeError:
        return file_bytes.decode('latin-1')


def extract_text(file_bytes: bytes, filename: str) -> Tuple[str, str]:
    """
    Extract text from file based on extension.
    Returns: (extracted_text, file_type)
    """
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    if ext == 'pdf':
        return extract_text_from_pdf(file_bytes), 'pdf'
    elif ext in ('docx', 'doc'):
        return extract_text_from_docx(file_bytes), 'docx'
    elif ext == 'txt':
        return extract_text_from_txt(file_bytes), 'txt'
    else:
        # Try to read as text
        try:
            return file_bytes.decode('utf-8'), 'txt'
        except:
            raise ValueError(f"Unsupported file type: {ext}")


# ============================================
# CV PARSING (Extract structured data)
# ============================================

def extract_email(text: str) -> Optional[str]:
    """Extract email address from text."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text."""
    patterns = [
        r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',  # US format
        r'\+?[0-9]{1,3}[-.\s]?[0-9]{2,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}',  # International
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def extract_linkedin(text: str) -> Optional[str]:
    """Extract LinkedIn URL from text."""
    pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else None


def extract_github(text: str) -> Optional[str]:
    """Extract GitHub URL from text."""
    pattern = r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else None


def extract_name(text: str) -> Optional[str]:
    """
    Extract name from CV (usually first line or near contact info).
    This is a simple heuristic - AI parsing would be more accurate.
    """
    lines = text.strip().split('\n')
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        # Skip lines that look like contact info or headers
        if '@' in line or 'http' in line.lower() or len(line) < 3:
            continue
        if line.isupper() or (len(line.split()) <= 4 and not any(c.isdigit() for c in line)):
            return line
    return None


def extract_skills(text: str) -> List[str]:
    """Extract common tech skills from text."""
    # Common skills to look for (expandable)
    skill_patterns = [
        # Programming languages
        r'\b(Python|JavaScript|TypeScript|Java|C\+\+|C#|Ruby|Go|Rust|PHP|Swift|Kotlin)\b',
        # Frameworks
        r'\b(React|Angular|Vue|Node\.js|Django|Flask|FastAPI|Spring|Rails|\.NET)\b',
        # Databases
        r'\b(SQL|PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch|DynamoDB)\b',
        # Cloud
        r'\b(AWS|Azure|GCP|Google Cloud|Kubernetes|Docker|Terraform)\b',
        # Tools
        r'\b(Git|Jenkins|CircleCI|GitHub Actions|Jira|Confluence)\b',
        # Data
        r'\b(Machine Learning|ML|AI|Data Science|Pandas|NumPy|TensorFlow|PyTorch)\b',
    ]
    
    skills = set()
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        skills.update(m if isinstance(m, str) else m[0] for m in matches)
    
    return list(skills)


def estimate_years_experience(text: str) -> Optional[int]:
    """Estimate years of experience from CV text."""
    # Look for explicit mentions
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'experience\s*(?:of\s*)?(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s*in\s*(?:the\s*)?(?:industry|field|software|development)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    # Count years from work history dates
    year_pattern = r'\b(19|20)\d{2}\b'
    years = [int(y) for y in re.findall(year_pattern, text)]
    if years:
        current_year = datetime.now().year
        # Rough estimate: earliest year to now
        earliest = min(y for y in years if y > 1970 and y <= current_year)
        return current_year - earliest
    
    return None


def parse_cv_sections(text: str) -> Dict[str, str]:
    """
    Parse CV into sections (summary, experience, education, skills).
    This is a simple heuristic - AI parsing would be more accurate.
    """
    sections = {
        'summary': '',
        'experience': '',
        'education': '',
        'skills': '',
        'other': ''
    }
    
    # Section headers to look for
    section_patterns = {
        'summary': r'(?:summary|profile|objective|about)',
        'experience': r'(?:experience|employment|work\s*history|professional)',
        'education': r'(?:education|academic|qualifications|degree)',
        'skills': r'(?:skills|technical|technologies|competencies)',
    }
    
    # Split by common section delimiters
    lines = text.split('\n')
    current_section = 'other'
    current_content = []
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Check if this line is a section header
        new_section = None
        for section, pattern in section_patterns.items():
            if re.search(pattern, line_lower) and len(line) < 50:
                new_section = section
                break
        
        if new_section:
            # Save previous section
            if current_content:
                sections[current_section] += '\n'.join(current_content) + '\n'
            current_section = new_section
            current_content = []
        else:
            current_content.append(line)
    
    # Save last section
    if current_content:
        sections[current_section] += '\n'.join(current_content)
    
    return sections


def parse_cv(text: str) -> Dict[str, Any]:
    """
    Parse CV text and extract structured data.
    Returns dict with name, email, phone, linkedin, github, skills, years_experience, sections.
    """
    return {
        'name': extract_name(text),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'linkedin': extract_linkedin(text),
        'github': extract_github(text),
        'skills': extract_skills(text),
        'years_experience': estimate_years_experience(text),
        'sections': parse_cv_sections(text),
    }


# ============================================
# SUPABASE HELPERS
# ============================================

def get_headers(use_service_key: bool = True) -> Dict[str, str]:
    """Get Supabase request headers."""
    key = SUPABASE_SERVICE_KEY if use_service_key else SUPABASE_ANON_KEY
    return {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def supabase_insert(table: str, data: Dict) -> Dict:
    """Insert record into Supabase table."""
    headers = get_headers()
    headers["Prefer"] = "return=representation"
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=headers,
        json=data,
        timeout=30
    )
    
    if r.status_code in (200, 201):
        result = r.json()
        return {"success": True, "data": result[0] if result else data}
    return {"success": False, "error": r.text}


def supabase_update(table: str, id: str, data: Dict) -> Dict:
    """Update record in Supabase table."""
    headers = get_headers()
    headers["Prefer"] = "return=representation"
    
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{id}",
        headers=headers,
        json=data,
        timeout=30
    )
    
    if r.status_code == 200:
        result = r.json()
        return {"success": True, "data": result[0] if result else data}
    return {"success": False, "error": r.text}


def supabase_query(table: str, filters: str = "", limit: int = 100) -> Dict:
    """Query Supabase table."""
    url = f"{SUPABASE_URL}/rest/v1/{table}?{filters}&limit={limit}"
    r = requests.get(url, headers=get_headers(), timeout=30)
    
    if r.status_code == 200:
        return {"success": True, "data": r.json()}
    return {"success": False, "error": r.text}


def upload_to_storage(bucket: str, path: str, file_bytes: bytes, content_type: str) -> Dict:
    """Upload file to Supabase Storage."""
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": content_type,
    }
    
    r = requests.post(
        f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}",
        headers=headers,
        data=file_bytes,
        timeout=60
    )
    
    if r.status_code in (200, 201):
        return {"success": True, "path": path}
    return {"success": False, "error": r.text}


def get_storage_url(bucket: str, path: str) -> str:
    """Get public URL for a storage file."""
    return f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}"


def download_from_storage(bucket: str, path: str) -> Optional[bytes]:
    """Download file from Supabase Storage."""
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    }
    
    r = requests.get(
        f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}",
        headers=headers,
        timeout=60
    )
    
    return r.content if r.status_code == 200 else None


# ============================================
# CV STORAGE CLASS
# ============================================

class CVStorage:
    """Handle CV upload, parsing, and storage."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    def upload_and_parse(
        self, 
        file_bytes: bytes, 
        filename: str,
        candidate_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload CV file, parse it, and store both file and parsed data.
        
        Returns:
            {
                "success": bool,
                "cv_id": str,
                "candidate_id": str,
                "parsed_data": {...},
                "error": str (if failed)
            }
        """
        try:
            # 1. Extract text from file
            parsed_text, file_type = extract_text(file_bytes, filename)
            
            # 2. Parse structured data
            parsed_data = parse_cv(parsed_text)
            
            # 3. Upload file to storage
            storage_path = f"{self.user_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            content_type = {
                'pdf': 'application/pdf',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'txt': 'text/plain'
            }.get(file_type, 'application/octet-stream')
            
            upload_result = upload_to_storage(CV_BUCKET, storage_path, file_bytes, content_type)
            if not upload_result.get("success"):
                return {"success": False, "error": f"Storage upload failed: {upload_result.get('error')}"}
            
            # 4. Create or update candidate record
            if not candidate_id:
                candidate_result = supabase_insert("candidates", {
                    "user_id": self.user_id,
                    "name": parsed_data.get('name'),
                    "email": parsed_data.get('email'),
                    "phone": parsed_data.get('phone'),
                    "linkedin_url": parsed_data.get('linkedin'),
                    "github_url": parsed_data.get('github'),
                    "source": "upload",
                    "stage": "new",
                })
                if not candidate_result.get("success"):
                    return {"success": False, "error": f"Candidate creation failed: {candidate_result.get('error')}"}
                candidate_id = candidate_result["data"]["id"]
            
            # 5. Create CV record
            cv_result = supabase_insert("cvs", {
                "user_id": self.user_id,
                "candidate_id": candidate_id,
                "file_name": filename,
                "file_type": file_type,
                "file_size": len(file_bytes),
                "storage_path": storage_path,
                "parsed_text": parsed_text,
                "parsed_sections": parsed_data.get('sections'),
                "extracted_name": parsed_data.get('name'),
                "extracted_email": parsed_data.get('email'),
                "extracted_phone": parsed_data.get('phone'),
                "extracted_linkedin": parsed_data.get('linkedin'),
                "extracted_github": parsed_data.get('github'),
                "extracted_skills": parsed_data.get('skills'),
                "years_experience": parsed_data.get('years_experience'),
                "parse_status": "parsed",
                "parsed_at": datetime.utcnow().isoformat(),
            })
            
            if not cv_result.get("success"):
                return {"success": False, "error": f"CV record creation failed: {cv_result.get('error')}"}
            
            return {
                "success": True,
                "cv_id": cv_result["data"]["id"],
                "candidate_id": candidate_id,
                "parsed_data": parsed_data,
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_cv(self, cv_id: str) -> Optional[Dict]:
        """Get CV record by ID."""
        result = supabase_query("cvs", f"id=eq.{cv_id}&user_id=eq.{self.user_id}")
        if result.get("success") and result["data"]:
            return result["data"][0]
        return None
    
    def get_candidate_cvs(self, candidate_id: str) -> List[Dict]:
        """Get all CVs for a candidate."""
        result = supabase_query("cvs", f"candidate_id=eq.{candidate_id}&user_id=eq.{self.user_id}")
        return result.get("data", []) if result.get("success") else []
    
    def download_cv_file(self, cv_id: str) -> Optional[bytes]:
        """Download original CV file."""
        cv = self.get_cv(cv_id)
        if cv and cv.get("storage_path"):
            return download_from_storage(CV_BUCKET, cv["storage_path"])
        return None
    
    def search(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Full-text search across CV content.
        Returns candidates with matching CVs.
        """
        # Convert query to tsquery format
        terms = query.strip().split()
        tsquery = ' & '.join(terms)
        
        # Use Supabase RPC for full-text search
        headers = get_headers()
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/search_cvs",
            headers=headers,
            json={
                "search_query": tsquery,
                "user_uuid": self.user_id,
                "result_limit": limit
            },
            timeout=30
        )
        
        if r.status_code == 200:
            return r.json()
        
        # Fallback: simple ILIKE search
        result = supabase_query(
            "cvs",
            f"user_id=eq.{self.user_id}&parsed_text=ilike.*{query}*&hidden_at=is.null",
            limit
        )
        return result.get("data", [])
    
    def list_recent(self, limit: int = 20) -> List[Dict]:
        """List recent CVs."""
        result = supabase_query(
            "cvs",
            f"user_id=eq.{self.user_id}&hidden_at=is.null&order=uploaded_at.desc",
            limit
        )
        return result.get("data", []) if result.get("success") else []
    
    def delete(self, cv_id: str) -> Dict:
        """Delete CV and associated file."""
        cv = self.get_cv(cv_id)
        if not cv:
            return {"success": False, "error": "CV not found"}
        
        # Delete from storage
        if cv.get("storage_path"):
            headers = {
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            }
            requests.delete(
                f"{SUPABASE_URL}/storage/v1/object/{CV_BUCKET}/{cv['storage_path']}",
                headers=headers,
                timeout=30
            )
        
        # Delete from database
        headers = get_headers()
        r = requests.delete(
            f"{SUPABASE_URL}/rest/v1/cvs?id=eq.{cv_id}&user_id=eq.{self.user_id}",
            headers=headers,
            timeout=30
        )
        
        return {"success": r.status_code in (200, 204)}


# ============================================
# TRANSCRIPT STORAGE CLASS
# ============================================

class TranscriptStorage:
    """Handle interview transcript upload and storage."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    def save_transcript(
        self,
        transcript_text: str,
        title: str,
        candidate_id: Optional[str] = None,
        pipeline_id: Optional[str] = None,
        interview_type: str = "phone_screen",
        file_bytes: Optional[bytes] = None,
        filename: Optional[str] = None,
        analysis_result: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Save interview transcript.
        
        Returns:
            {
                "success": bool,
                "transcript_id": str,
                "error": str (if failed)
            }
        """
        try:
            storage_path = None
            
            # Upload original file if provided
            if file_bytes and filename:
                storage_path = f"{self.user_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                upload_result = upload_to_storage(
                    TRANSCRIPT_BUCKET, 
                    storage_path, 
                    file_bytes, 
                    "text/plain"
                )
                if not upload_result.get("success"):
                    return {"success": False, "error": f"Storage upload failed: {upload_result.get('error')}"}
            
            # Create transcript record
            data = {
                "user_id": self.user_id,
                "candidate_id": candidate_id,
                "pipeline_id": pipeline_id,
                "title": title,
                "transcript_text": transcript_text,
                "interview_type": interview_type,
                "interview_date": datetime.utcnow().isoformat(),
            }
            
            if storage_path:
                data["storage_path"] = storage_path
                data["file_name"] = filename
                data["file_type"] = filename.split('.')[-1] if '.' in filename else 'txt'
            
            if analysis_result:
                data["analysis_result"] = analysis_result
                data["overall_score"] = analysis_result.get("overall_score")
                data["analyzed_at"] = datetime.utcnow().isoformat()
            
            result = supabase_insert("interview_transcripts", data)
            
            if not result.get("success"):
                return {"success": False, "error": f"Transcript save failed: {result.get('error')}"}
            
            return {
                "success": True,
                "transcript_id": result["data"]["id"],
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_analysis(self, transcript_id: str, analysis_result: Dict) -> Dict:
        """Update transcript with AI analysis results."""
        return supabase_update("interview_transcripts", transcript_id, {
            "analysis_result": analysis_result,
            "overall_score": analysis_result.get("overall_score"),
            "key_concerns": analysis_result.get("key_concerns", []),
            "analyzed_at": datetime.utcnow().isoformat(),
        })
    
    def get_transcript(self, transcript_id: str) -> Optional[Dict]:
        """Get transcript by ID."""
        result = supabase_query(
            "interview_transcripts", 
            f"id=eq.{transcript_id}&user_id=eq.{self.user_id}"
        )
        if result.get("success") and result["data"]:
            return result["data"][0]
        return None
    
    def get_candidate_transcripts(self, candidate_id: str) -> List[Dict]:
        """Get all transcripts for a candidate."""
        result = supabase_query(
            "interview_transcripts",
            f"candidate_id=eq.{candidate_id}&user_id=eq.{self.user_id}&order=created_at.desc"
        )
        return result.get("data", []) if result.get("success") else []
    
    def list_recent(self, limit: int = 20) -> List[Dict]:
        """List recent transcripts."""
        result = supabase_query(
            "interview_transcripts",
            f"user_id=eq.{self.user_id}&hidden_at=is.null&order=created_at.desc",
            limit
        )
        return result.get("data", []) if result.get("success") else []
    
    def delete(self, transcript_id: str) -> Dict:
        """Delete transcript and associated file."""
        transcript = self.get_transcript(transcript_id)
        if not transcript:
            return {"success": False, "error": "Transcript not found"}
        
        # Delete from storage if exists
        if transcript.get("storage_path"):
            headers = {
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            }
            requests.delete(
                f"{SUPABASE_URL}/storage/v1/object/{TRANSCRIPT_BUCKET}/{transcript['storage_path']}",
                headers=headers,
                timeout=30
            )
        
        # Delete from database
        headers = get_headers()
        r = requests.delete(
            f"{SUPABASE_URL}/rest/v1/interview_transcripts?id=eq.{transcript_id}&user_id=eq.{self.user_id}",
            headers=headers,
            timeout=30
        )
        
        return {"success": r.status_code in (200, 204)}


# ============================================
# CANDIDATE HELPER CLASS
# ============================================

class CandidateManager:
    """Manage candidates and their pipeline stages."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    def create(
        self,
        name: str,
        email: Optional[str] = None,
        pipeline_id: Optional[str] = None,
        source: str = "manual",
        **kwargs
    ) -> Dict:
        """Create a new candidate."""
        data = {
            "user_id": self.user_id,
            "name": name,
            "email": email,
            "pipeline_id": pipeline_id,
            "source": source,
            "stage": "new",
            **kwargs
        }
        return supabase_insert("candidates", data)
    
    def update_stage(self, candidate_id: str, new_stage: str) -> Dict:
        """Update candidate stage and log activity."""
        # Get current stage
        candidate = self.get(candidate_id)
        old_stage = candidate.get("stage") if candidate else None
        
        # Update stage
        result = supabase_update("candidates", candidate_id, {"stage": new_stage})
        
        # Log activity
        if result.get("success"):
            supabase_insert("candidate_activity", {
                "user_id": self.user_id,
                "candidate_id": candidate_id,
                "action": "stage_changed",
                "old_value": old_stage,
                "new_value": new_stage,
            })
        
        return result
    
    def update_screening(self, candidate_id: str, score: int, result: Dict) -> Dict:
        """Update candidate with screening results."""
        update_result = supabase_update("candidates", candidate_id, {
            "screening_score": score,
            "screening_result": result,
            "screening_date": datetime.utcnow().isoformat(),
            "stage": "screened" if score >= 50 else "rejected",
        })
        
        # Log activity
        if update_result.get("success"):
            supabase_insert("candidate_activity", {
                "user_id": self.user_id,
                "candidate_id": candidate_id,
                "action": "screened",
                "new_value": str(score),
                "details": {"score": score},
            })
        
        return update_result
    
    def get(self, candidate_id: str) -> Optional[Dict]:
        """Get candidate by ID."""
        result = supabase_query("candidates", f"id=eq.{candidate_id}&user_id=eq.{self.user_id}")
        if result.get("success") and result["data"]:
            return result["data"][0]
        return None
    
    def list_by_pipeline(self, pipeline_id: str, include_hidden: bool = False) -> List[Dict]:
        """List candidates in a pipeline."""
        filters = f"pipeline_id=eq.{pipeline_id}&user_id=eq.{self.user_id}&order=screening_score.desc.nullslast"
        if not include_hidden:
            filters += "&hidden_at=is.null"
        result = supabase_query("candidates", filters, limit=500)
        return result.get("data", []) if result.get("success") else []
    
    def list_by_stage(self, stage: str) -> List[Dict]:
        """List candidates by stage."""
        result = supabase_query(
            "candidates",
            f"user_id=eq.{self.user_id}&stage=eq.{stage}&hidden_at=is.null&order=updated_at.desc"
        )
        return result.get("data", []) if result.get("success") else []
    
    def search(self, query: str, limit: int = 50) -> List[Dict]:
        """Search candidates by name or email."""
        result = supabase_query(
            "candidates",
            f"user_id=eq.{self.user_id}&or=(name.ilike.*{query}*,email.ilike.*{query}*)&hidden_at=is.null",
            limit
        )
        return result.get("data", []) if result.get("success") else []
    
    def delete(self, candidate_id: str) -> Dict:
        """Delete candidate and associated data."""
        headers = get_headers()
        r = requests.delete(
            f"{SUPABASE_URL}/rest/v1/candidates?id=eq.{candidate_id}&user_id=eq.{self.user_id}",
            headers=headers,
            timeout=30
        )
        return {"success": r.status_code in (200, 204)}
    
    def get_activity(self, candidate_id: str, limit: int = 50) -> List[Dict]:
        """Get activity log for a candidate."""
        result = supabase_query(
            "candidate_activity",
            f"candidate_id=eq.{candidate_id}&order=created_at.desc",
            limit
        )
        return result.get("data", []) if result.get("success") else []


# ============================================
# FULL-TEXT SEARCH FUNCTION (Add to Supabase)
# ============================================

SEARCH_FUNCTION_SQL = """
-- Add this function to Supabase for full-text CV search
CREATE OR REPLACE FUNCTION search_cvs(
    search_query TEXT,
    user_uuid UUID,
    result_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    cv_id UUID,
    candidate_id UUID,
    candidate_name VARCHAR,
    file_name VARCHAR,
    relevance REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cv.id,
        cv.candidate_id,
        c.name,
        cv.file_name,
        ts_rank(to_tsvector('english', cv.parsed_text), plainto_tsquery('english', search_query)) as relevance
    FROM cvs cv
    JOIN candidates c ON c.id = cv.candidate_id
    WHERE cv.user_id = user_uuid
    AND cv.hidden_at IS NULL
    AND to_tsvector('english', cv.parsed_text) @@ plainto_tsquery('english', search_query)
    ORDER BY relevance DESC
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql;
"""
