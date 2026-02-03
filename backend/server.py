from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import shutil
import asyncio

from analysis.analyzer import run_analysis
from report.html_generator import generate_html_report

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

UPLOAD_DIR = ROOT_DIR / "uploads"
OUTPUT_DIR = ROOT_DIR / "output" / "reports"
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


class AnalysisStatus(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    status: str  # pending, running, completed, failed
    filename: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    report_path: Optional[str] = None
    error: Optional[str] = None
    total_violations: Optional[int] = None
    files_analyzed: Optional[int] = None


class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str


@api_router.get("/")
async def root():
    return {"message": "MISRA C Analysis API", "version": "1.0"}


@api_router.post("/upload", response_model=AnalysisResponse)
async def upload_code(file: UploadFile = File(...)):
    """Upload C/C++ source code ZIP file for MISRA analysis"""
    
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only ZIP files are accepted")
    
    analysis_id = str(uuid.uuid4())
    upload_path = UPLOAD_DIR / analysis_id
    upload_path.mkdir(exist_ok=True)
    
    zip_path = upload_path / file.filename
    
    try:
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    analysis_doc = {
        "id": analysis_id,
        "status": "pending",
        "filename": file.filename,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "report_path": None,
        "error": None,
        "total_violations": None,
        "files_analyzed": None
    }
    
    await db.analyses.insert_one(analysis_doc)
    
    asyncio.create_task(process_analysis(analysis_id, str(zip_path), file.filename))
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="pending",
        message=f"File uploaded successfully. Analysis started with ID: {analysis_id}"
    )


async def process_analysis(analysis_id: str, zip_path: str, filename: str):
    """Background task to process analysis"""
    try:
        await db.analyses.update_one(
            {"id": analysis_id},
            {"$set": {"status": "running"}}
        )
        
        extract_dir = UPLOAD_DIR / analysis_id / "extracted"
        extract_dir.mkdir(exist_ok=True)
        
        shutil.unpack_archive(zip_path, extract_dir)
        
        results = await asyncio.get_event_loop().run_in_executor(
            None, run_analysis, str(extract_dir)
        )
        
        report_filename = f"misra_report_{analysis_id}.html"
        report_path = OUTPUT_DIR / report_filename
        
        generate_html_report(results, str(report_path), filename)
        
        await db.analyses.update_one(
            {"id": analysis_id},
            {"$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "report_path": str(report_path),
                "total_violations": results.get("summary", {}).get("total_violations", 0),
                "files_analyzed": results.get("summary", {}).get("files_analyzed", 0)
            }}
        )
        
    except Exception as e:
        logging.error(f"Analysis failed for {analysis_id}: {str(e)}")
        await db.analyses.update_one(
            {"id": analysis_id},
            {"$set": {
                "status": "failed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }}
        )


@api_router.get("/analysis/{analysis_id}", response_model=AnalysisStatus)
async def get_analysis_status(analysis_id: str):
    """Get the status of an analysis"""
    analysis = await db.analyses.find_one({"id": analysis_id}, {"_id": 0})
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.get("created_at") and isinstance(analysis["created_at"], str):
        analysis["created_at"] = datetime.fromisoformat(analysis["created_at"])
    if analysis.get("completed_at") and isinstance(analysis["completed_at"], str):
        analysis["completed_at"] = datetime.fromisoformat(analysis["completed_at"])
    
    return AnalysisStatus(**analysis)


@api_router.get("/report/{analysis_id}")
async def download_report(analysis_id: str):
    """Download the HTML report for an analysis"""
    analysis = await db.analyses.find_one({"id": analysis_id}, {"_id": 0})
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Analysis is {analysis['status']}")
    
    report_path = Path(analysis["report_path"])
    
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(
        path=report_path,
        filename=f"misra_report_{analysis_id}.html",
        media_type="text/html"
    )


@api_router.get("/analyses", response_model=List[AnalysisStatus])
async def list_analyses():
    """List all analyses"""
    analyses = await db.analyses.find({}, {"_id": 0}).sort("created_at", -1).limit(50).to_list(50)
    
    for analysis in analyses:
        if analysis.get("created_at") and isinstance(analysis["created_at"], str):
            analysis["created_at"] = datetime.fromisoformat(analysis["created_at"])
        if analysis.get("completed_at") and isinstance(analysis["completed_at"], str):
            analysis["completed_at"] = datetime.fromisoformat(analysis["completed_at"])
    
    return analyses


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
