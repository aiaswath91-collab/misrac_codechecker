# MISRA C:2012 Analysis Web Application

A professional, self-hosted web application for MISRA C:2012 static analysis of C/C++ source code. Built with open-source analysis engines and providing market-comparable features with comprehensive HTML reporting.

## 🎯 Features

### Core Functionality
- **ZIP Upload**: Upload C/C++ source code in ZIP format
- **Automated Analysis**: Multi-engine static analysis with:
  - Cppcheck (with MISRA addon)
  - Clang-Tidy
- **MISRA C:2012 Compliance**: Rule coverage and severity classification
- **Professional HTML Reports**: Standalone, downloadable reports matching industry standards
- **Real-time Status Tracking**: Monitor analysis progress (pending → running → completed)
- **Analysis History**: View and download previous analysis reports

### Analysis Features
✅ **MISRA Rule Coverage**: Mapped to MISRA C:2012 rules  
✅ **Severity Classification**: Mandatory / Required / Advisory  
✅ **Violation Normalization**: Deduplicated findings from multiple tools  
✅ **File-wise Statistics**: Violations grouped by source file  
✅ **Detailed Reports**: Line numbers, rule IDs, code snippets  
✅ **Summary Dashboard**: Files analyzed, lines of code, total violations  

### Report Structure
- **Header**: Project info, analysis date, tool version
- **Summary Statistics**: Files, lines, violations by severity
- **File-wise Summary**: Violation counts per file
- **Detailed Violations**: Complete breakdown with:
  - Line numbers
  - MISRA rule IDs
  - Severity levels
  - Violation descriptions
  - Code snippets

## 🏗️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: MongoDB (for analysis tracking)
- **Analysis Engines**:
  - Cppcheck (C/C++ static analyzer)
  - Clang-Tidy (LLVM-based linter)
- **Report Generation**: Jinja2 templates
- **File Processing**: Python multipart, aiofiles

### Frontend
- **Framework**: React 19
- **UI Library**: Lucide React icons
- **Styling**: Custom CSS with gradient design
- **HTTP Client**: Axios

### Analysis Tools
- **Cppcheck**: Open-source static analyzer with MISRA addon
- **Clang-Tidy**: LLVM/Clang-based static analysis

## 📁 Project Structure

```
/app/
├── backend/
│   ├── server.py                  # FastAPI main application
│   ├── analysis/
│   │   └── analyzer.py            # MISRA analysis engine
│   ├── report/
│   │   ├── html_generator.py     # Report generation
│   │   └── templates/
│   │       └── misra_report.html.j2  # HTML template
│   ├── uploads/                   # Uploaded ZIP files
│   └── output/
│       └── reports/               # Generated HTML reports
├── frontend/
│   └── src/
│       ├── App.js                 # Main React component
│       └── App.css                # Application styles
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- MongoDB
- Cppcheck
- Clang-Tidy

### Installation

1. **Install Analysis Tools**:
```bash
apt-get update
apt-get install -y cppcheck clang-tidy
```

2. **Backend Setup**:
```bash
cd /app/backend
pip install -r requirements.txt
```

3. **Frontend Setup**:
```bash
cd /app/frontend
yarn install
```

### Running the Application

The application runs on:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001/api

Services are managed by supervisor and start automatically.

## 📊 API Endpoints

### Upload Code
```
POST /api/upload
Content-Type: multipart/form-data
Body: { file: <ZIP file> }

Response: {
  "analysis_id": "uuid",
  "status": "pending",
  "message": "Analysis started"
}
```

### Check Analysis Status
```
GET /api/analysis/{analysis_id}

Response: {
  "id": "uuid",
  "status": "completed",
  "filename": "code.zip",
  "files_analyzed": 10,
  "total_violations": 45,
  "created_at": "2026-02-03T12:00:00Z",
  "completed_at": "2026-02-03T12:00:15Z"
}
```

### Download Report
```
GET /api/report/{analysis_id}

Response: HTML file download
```

### List All Analyses
```
GET /api/analyses

Response: [{
  "id": "uuid",
  "status": "completed",
  "filename": "code.zip",
  "files_analyzed": 10,
  "total_violations": 45
}, ...]
```

## 🔍 Usage Workflow

1. **Prepare Your Code**:
   - Package C/C++ source files into a ZIP archive
   - Include all .c, .cpp, .h, .hpp files

2. **Upload**:
   - Navigate to the web interface
   - Click "Choose ZIP file"
   - Select your archive
   - Click "Start Analysis"

3. **Monitor Progress**:
   - Analysis status updates automatically
   - Statuses: pending → running → completed

4. **Download Report**:
   - Click "Download HTML Report" button
   - Open the standalone HTML file in any browser
   - Report includes full violation details

## 📈 MISRA Rule Coverage

The analyzer maps detected issues to MISRA C:2012 rules including:
- **Rule 2.1**: Unused code
- **Rule 2.3**: Unused type declarations
- **Rule 2.7**: Unused parameters
- **Rule 8.7**: Could be declared static
- **Rule 8.13**: Pointer to const
- **Rule 9.1**: Uninitialized variables
- **Rule 10.8**: Composite expression casting
- **Rule 11.3**: Pointer type casting
- **Rule 11.4**: Pointer-integer conversion
- **Rule 14.3**: Controlling expression
- **Rule 14.4**: Boolean type
- **Rule 17.4**: Missing return
- **Rule 17.7**: Unused return value
- **Rule 18.1**: Array bounds
- **Rule 21.6**: Standard I/O functions
- **Rule 22.1**: Memory/resource leaks

## ⚠️ Disclaimers

### Legal & Certification
- This tool uses **open-source static analysis engines**
- MISRA coverage is **partial and non-certified**
- This report **cannot be used** for:
  - SIL-3/4 certification
  - EN 50128 compliance
  - ISO 26262 certification
- For certification purposes, use commercial certified tools (PC-lint, QAC, Polyspace)

### Tool Limitations
- Rule coverage depends on open-source engine capabilities
- Some MISRA rules require manual review
- Results should be validated by experienced developers
- False positives may occur and require investigation

## 🎨 UI Features

### Professional Design
- Modern gradient background
- Clean, intuitive interface
- Real-time status updates
- Responsive layout
- Professional typography (Inter font)

### User Experience
- Drag-and-drop file upload (styled input)
- Visual status indicators with icons
- Analysis history with download buttons
- Error handling and validation
- Loading states and animations

## 🔧 Configuration

### Environment Variables

**Backend** (`/app/backend/.env`):
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=misra_analyzer
CORS_ORIGINS=*
```

**Frontend** (`/app/frontend/.env`):
```
REACT_APP_BACKEND_URL=<your-backend-url>
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
python /app/backend_test.py
```

Test coverage:
- ✅ File upload validation
- ✅ Analysis execution
- ✅ Report generation
- ✅ API endpoints
- ✅ Frontend workflows
- ✅ Error handling

## 📝 Sample Output

### Summary Statistics
- Files Analyzed: 19
- Lines Analyzed: 2,833
- Total Violations: 288
- Severity Breakdown:
  - Mandatory: 0
  - Required: 180
  - Advisory: 108

### Detailed Violations
Each violation includes:
- Source file and line number
- MISRA rule ID (e.g., MISRA C:2012 Rule 21.6)
- Severity level (Mandatory/Required/Advisory)
- Issue type (error/warning/info/note)
- Description and code snippet

## 🚀 Future Enhancements

Potential improvements:
- Docker containerization for complete sandbox execution
- User authentication and project management
- Historical trend analysis and compliance tracking
- Suppression file support (inline and external)
- Custom rule configuration
- CI/CD pipeline integration
- Export formats: CSV, JSON, Excel
- Rule-wise statistics and hot-spots
- Compliance percentage calculations

## 📄 License

This project uses open-source tools and libraries. Please check individual component licenses:
- Cppcheck: GPL-3.0
- Clang-Tidy: Apache-2.0
- FastAPI: MIT
- React: MIT

---

**Built with ❤️ for Safety-Critical C Development**
