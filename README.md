
## ⚡ Quick Start 

### 1. Clone & Setup Environment
```
python -m venv .venv
```
```
\.venv\Scripts\activate
```
```
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./{name}.db
```

### 3. Start Server
```
uvicorn app.main:app --reload 
```

**Server: http://127.0.0.1:8000**  
**API: http://127.0.0.1:8000/docs**
