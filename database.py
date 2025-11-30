"""
SQLite Database module for storing SEO analysis results.
Replaces MongoDB with SQLite for a free, local database solution.
"""

import sqlite3
import json
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

import config

logger = logging.getLogger(__name__)


class DatabaseClient:
    """SQLite database client for SEO analysis storage."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path or config.DATABASE_PATH
        self._init_db()
        logger.info(f"Database initialized at: {self.db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create analysis_requests table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    unique_identifier TEXT UNIQUE NOT NULL,
                    website_url TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    analysis_result TEXT,
                    report_markdown TEXT,
                    error_message TEXT
                )
            ''')
            
            # Create session_states table for ADK session management
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    agent_name TEXT NOT NULL,
                    state_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create analysis_logs table for observability
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT,
                    agent_name TEXT,
                    action TEXT,
                    details TEXT,
                    duration_ms INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            logger.info("Database tables initialized successfully")
    
    def create_analysis_request(self, website_url: str) -> Dict[str, Any]:
        """Create a new SEO analysis request."""
        unique_identifier = str(uuid.uuid4())[:8]
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analysis_requests (unique_identifier, website_url, status)
                VALUES (?, ?, 'pending')
            ''', (unique_identifier, website_url))
            
        logger.info(f"Created analysis request: {unique_identifier} for {website_url}")
        return {
            'unique_identifier': unique_identifier,
            'website_url': website_url,
            'status': 'pending'
        }
    
    def get_request_by_identifier(self, unique_identifier: str) -> Optional[Dict[str, Any]]:
        """Get analysis request by unique identifier."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM analysis_requests WHERE unique_identifier = ?
            ''', (unique_identifier,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
        return None
    
    def update_request_status(
        self, 
        unique_identifier: str, 
        status: str,
        analysis_result: Dict[str, Any] = None,
        report_markdown: str = None,
        error_message: str = None
    ) -> bool:
        """Update analysis request status and results."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            updates = ['status = ?', 'updated_at = CURRENT_TIMESTAMP']
            params = [status]
            
            if status == 'completed':
                updates.append('completed_at = CURRENT_TIMESTAMP')
            
            if analysis_result:
                updates.append('analysis_result = ?')
                params.append(json.dumps(analysis_result))
            
            if report_markdown:
                updates.append('report_markdown = ?')
                params.append(report_markdown)
            
            if error_message:
                updates.append('error_message = ?')
                params.append(error_message)
            
            params.append(unique_identifier)
            
            cursor.execute(f'''
                UPDATE analysis_requests 
                SET {', '.join(updates)}
                WHERE unique_identifier = ?
            ''', params)
            
            logger.info(f"Updated request {unique_identifier} status to: {status}")
            return cursor.rowcount > 0
    
    def log_agent_action(
        self,
        request_id: str,
        agent_name: str,
        action: str,
        details: Dict[str, Any] = None,
        duration_ms: int = None
    ):
        """Log agent action for observability."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analysis_logs (request_id, agent_name, action, details, duration_ms)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                request_id,
                agent_name,
                action,
                json.dumps(details) if details else None,
                duration_ms
            ))
    
    def get_analysis_logs(self, request_id: str) -> List[Dict[str, Any]]:
        """Get all logs for a specific analysis request."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM analysis_logs 
                WHERE request_id = ? 
                ORDER BY created_at ASC
            ''', (request_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def save_session_state(
        self,
        session_id: str,
        agent_name: str,
        state_data: Dict[str, Any]
    ) -> bool:
        """Save or update session state for an agent."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO session_states (session_id, agent_name, state_data)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    state_data = excluded.state_data,
                    updated_at = CURRENT_TIMESTAMP
            ''', (session_id, agent_name, json.dumps(state_data)))
            
            logger.debug(f"Saved session state for {agent_name}: {session_id}")
            return True
    
    def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session state by session ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM session_states WHERE session_id = ?
            ''', (session_id,))
            row = cursor.fetchone()
            
            if row:
                result = dict(row)
                if result.get('state_data'):
                    result['state_data'] = json.loads(result['state_data'])
                return result
        return None
    
    def get_all_requests(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all analysis requests."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, unique_identifier, website_url, status, created_at, completed_at
                FROM analysis_requests 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]


# Global database client instance
_db_client: Optional[DatabaseClient] = None


def get_db_client() -> DatabaseClient:
    """Get or create the global database client."""
    global _db_client
    if _db_client is None:
        _db_client = DatabaseClient()
    return _db_client
