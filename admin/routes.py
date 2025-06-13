"""
Admin routes for database management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from database import get_db, engine
import sqlite3
import os
from typing import Dict, List, Any
import json

router = APIRouter()

@router.get("/docs", response_class=HTMLResponse)
async def get_admin_docs():
    """Generate basic API documentation for admin use"""
    docs_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EcoTrack Ghana API - Admin Documentation</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
            .endpoint { margin: 20px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #007bff; }
            .method { display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; margin-right: 10px; }
            .get { background: #28a745; }
            .post { background: #007bff; }
            .put { background: #ffc107; color: black; }
            .delete { background: #dc3545; }
            code { background: #e9ecef; padding: 2px 4px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌍 EcoTrack Ghana API Documentation</h1>
            <p>Admin access to API endpoints</p>
            
            <h2>📊 Admin Endpoints</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/admin/stats</strong><br>
                Get database statistics and record counts
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/admin/tables</strong><br>
                List all database tables and their structure
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/admin/table/{table_name}</strong><br>
                Get data from a specific table with pagination<br>
                <em>Query parameters: limit (default: 10), offset (default: 0)</em>
            </div>
            
            <h2>🔐 Authentication Endpoints</h2>
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/v1/auth/register</strong><br>
                Register a new user
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/v1/auth/login</strong><br>
                Login with email and password
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/auth/me</strong><br>
                Get current user information (requires authentication)
            </div>
            
            <h2>🎯 Activities Endpoints</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/activities</strong><br>
                Get all activities with optional filters
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/v1/activities</strong><br>
                Create a new activity (requires authentication)
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/activities/my</strong><br>
                Get current user's activities (requires authentication)
            </div>
            
            <h2>🏆 Challenges Endpoints</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/challenges</strong><br>
                Get all challenges with optional filters
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/v1/challenges/{id}/join</strong><br>
                Join a challenge (requires authentication)
            </div>
            
            <h2>👥 Community Endpoints</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/community/leaderboard</strong><br>
                Get community leaderboard
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/community/stats/global</strong><br>
                Get global community statistics
            </div>
            
            <h2>🇬🇭 Ghana Data Endpoints</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/api/v1/ghana/regions</strong><br>
                Get list of Ghana regions with capitals
            </div>
            
            <h2>❤️ Health Check</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <strong>/health</strong><br>
                API health check
            </div>
            
            <h3>🌐 Base URLs</h3>
            <ul>
                <li><strong>Production:</strong> <code>https://ecotrack-online.onrender.com</code></li>
                <li><strong>Development:</strong> <code>http://localhost:8000</code></li>
            </ul>
            
            <h3>📝 Example Usage</h3>
            <pre><code># Get health status
curl https://ecotrack-online.onrender.com/health

# Get global stats
curl https://ecotrack-online.onrender.com/api/v1/community/stats/global

# Get challenges
curl https://ecotrack-online.onrender.com/api/v1/challenges?active_only=true&limit=10

# Get leaderboard
curl https://ecotrack-online.onrender.com/api/v1/community/leaderboard?limit=20</code></pre>
        </div>
    </body>
    </html>
    """
    return docs_html

@router.get("/stats")
async def get_database_stats(db: Session = Depends(get_db)):
    """Get database statistics"""
    try:
        # Get table information
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        stats = {
            "tables": {},
            "total_records": 0,
            "database_info": {
                "type": "SQLite",
                "tables_count": len(tables)
            }
        }
        
        # Count records in each table
        for table in tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                stats["tables"][table] = count
                stats["total_records"] += count
            except Exception as e:
                stats["tables"][table] = f"Error: {str(e)}"
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database stats error: {str(e)}")

@router.get("/tables")
async def list_tables(db: Session = Depends(get_db)):
    """List all database tables"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        table_info = []
        for table in tables:
            columns = inspector.get_columns(table)
            table_info.append({
                "name": table,
                "columns": [{"name": col["name"], "type": str(col["type"])} for col in columns]
            })
        
        return {"tables": table_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tables: {str(e)}")

@router.get("/table/{table_name}")
async def get_table_data(
    table_name: str,
    limit: int = Query(default=10, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """Get data from a specific table"""
    try:
        # Validate table name (security)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if table_name not in tables:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # Get data with pagination
        result = db.execute(text(f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}"))
        columns = result.keys()
        rows = result.fetchall()
        
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        # Get total count
        count_result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        total_count = count_result.scalar()
        
        return {
            "table": table_name,
            "data": data,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing table: {str(e)}")

@router.post("/query")
async def execute_query(
    query_data: Dict[str, str],
    db: Session = Depends(get_db)
):
    """Execute a custom SQL query (READ ONLY)"""
    query = query_data.get("query", "").strip().lower()
    
    # Security: Only allow SELECT queries
    if not query.startswith("select"):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
    
    try:
        result = db.execute(text(query_data["query"]))
        columns = result.keys()
        rows = result.fetchall()
        
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        return {"data": data, "row_count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

@router.get("/backup-info")
async def get_backup_info():
    """Get information about database backups"""
    db_path = "ecotrack_ghana.db"
    
    if not os.path.exists(db_path):
        return {"error": "Database file not found"}
    
    file_size = os.path.getsize(db_path)
    file_size_mb = file_size / (1024 * 1024)
    
    return {
        "database_path": db_path,
        "size_bytes": file_size,
        "size_mb": round(file_size_mb, 2),
        "backup_available": True
    }
