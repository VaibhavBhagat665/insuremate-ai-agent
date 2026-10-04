from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    api_title: str = "InsureMate AI Agent"
    api_version: str = "2.0.0"
    api_description: str = "AI-powered document processing and query system"
    
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 1
    
    max_file_size: int = 500 * 1024 * 1024  # 500MB
    allowed_extensions: list = [".pdf", ".docx", ".txt"]
    chunk_size: int = 2000
    chunk_overlap: int = 200
    max_context_chunks: int = 20
    
    # Primary LLM Configuration - OpenRouter (optional — graceful degradation)
    llm_provider: str = "openrouter"
    openrouter_api_key: Optional[str] = None
    openrouter_model: str = "mistralai/codestral-2508"
    openrouter_base_url: str = "https://openrouter.ai/api/v1/chat/completions"
    openrouter_http_referer: str = "https://insuremate-ai.com"
    openrouter_x_title: str = "InsureMate AI Agent"
    
    # Rate Limiting Configuration
    openrouter_requests_per_minute: int = 20
    groq_requests_per_minute: int = 30
    gemini_requests_per_minute: int = 60
    
    # Retry and Error Handling Configuration
    max_retries: int = 5
    base_delay: float = 1.0
    max_delay: float = 120.0
    enable_exponential_backoff: bool = True
    respect_retry_after_header: bool = True
    
    # First Fallback - Groq
    groq_api_key: Optional[str] = None
    groq_model: Optional[str] = "openai/gpt-oss-120b"
    groq_base_url: Optional[str] = "https://api.groq.com/openai/v1/chat/completions"
    groq_retry_attempts: Optional[int] = 2
    groq_retry_delay: Optional[float] = 1.0
    
    # Second Fallback - Google Gemini
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = "gemini-2.0-flash-exp"
    gemini_base_url: Optional[str] = "https://generativelanguage.googleapis.com/v1beta/models"

    # Legacy OpenAI configuration
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = "gpt-4o"
    openai_base_url: Optional[str] = "https://api.openai.com/v1/chat/completions"
    openai_requests_per_minute: int = 60
    
    # LLM Parameters
    confidence_threshold: float = 0.8
    max_tokens: Optional[int] = None
    temperature: float = 0.1
    top_p: float = 0.9
    request_timeout: int = 300
    
    # Processing Parameters
    max_pages_per_document: int = 1000
    processing_timeout_per_page: float = 1.0
    parallel_processing: bool = True
    
    # Embedding Configuration - aligned to MiniLM-L6-v2
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    embedding_batch_size: int = 128
    
    # Vector Database Configuration
    pinecone_api_key: Optional[str] = None
    pinecone_env: Optional[str] = None
    pinecone_index_name: str = "document-embeddings-v2"
    
    # Enhanced Local Vector Storage
    vector_storage_path: str = "data/vectors"
    cache_size: int = 10000
    enable_compression: bool = True
    
    # Search Configuration
    similarity_threshold: float = 0.05  # Very low to ensure document chunks are always returned
    max_search_results: int = 50
    rerank_enabled: bool = True
    hybrid_search_enabled: bool = True
    semantic_search_weight: float = 0.7
    keyword_search_weight: float = 0.3
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    log_rotation: str = "1 day"
    log_retention: str = "30 days"
    enable_detailed_logging: bool = True
    
    # CORS Configuration
    cors_origins: list = ["*"]
    cors_methods: list = ["GET", "POST", "PUT", "DELETE"]
    cors_headers: list = ["*"]
    
    # Performance Configuration
    api_request_timeout: int = 600
    batch_size: int = 500
    max_concurrent_requests: int = 50
    enable_response_caching: bool = True
    cache_ttl: int = 7200
    
    # Rate Limiting Monitoring
    enable_rate_limit_monitoring: bool = True
    log_rate_limit_events: bool = True
    rate_limit_alert_threshold: int = 10
    
    # Circuit Breaker Configuration
    enable_circuit_breaker: bool = False
    circuit_breaker_failure_threshold: int = 10
    circuit_breaker_timeout: int = 120
    circuit_breaker_recovery_timeout: int = 60
    
    # Webhook Configuration
    webhook_secret: Optional[str] = None
    webhook_timeout: int = 60
    
    # Development Settings
    debug: bool = False
    reload: bool = False
    enable_metrics: bool = True
    
    # Unlimited Mode Flags
    unlimited_mode: bool = True
    remove_token_limits: bool = True
    remove_time_limits: bool = True
    comprehensive_answers: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def get_active_api_key(self) -> Optional[str]:
        """Return the first available API key across all providers"""
        if self.openrouter_api_key:
            return self.openrouter_api_key
        if self.groq_api_key:
            return self.groq_api_key
        if self.gemini_api_key:
            return self.gemini_api_key
        if self.openai_api_key:
            return self.openai_api_key
        return None

    def get_active_provider(self) -> str:
        """Auto-detect the active provider based on available keys"""
        if self.openrouter_api_key:
            return "openrouter"
        if self.groq_api_key:
            return "groq"
        if self.gemini_api_key:
            return "gemini"
        if self.openai_api_key:
            return "openai"
        return self.llm_provider
        
    def get_llm_config(self) -> dict:
        """Get LLM configuration dictionary"""
        # Auto-detect provider based on available keys
        provider = self.get_active_provider()
        
        base_config = {
            "max_tokens": None,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "timeout": self.request_timeout,
            "unlimited_mode": True
        }
        
        if provider == "openrouter":
            return {
                "provider": "openrouter",
                "api_key": self.openrouter_api_key,
                "model": self.openrouter_model,
                "base_url": self.openrouter_base_url,
                "http_referer": self.openrouter_http_referer,
                "x_title": self.openrouter_x_title,
                **base_config
            }
        elif provider == "groq":
            return {
                "provider": "groq",
                "api_key": self.groq_api_key,
                "model": self.groq_model,
                "base_url": self.groq_base_url,
                "retry_attempts": self.groq_retry_attempts,
                "retry_delay": self.groq_retry_delay,
                **base_config
            }
        elif provider == "gemini":
            return {
                "provider": "gemini",
                "api_key": self.gemini_api_key,
                "model": self.gemini_model,
                "base_url": self.gemini_base_url,
                **base_config
            }
        else:
            return {
                "provider": "openai",
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "base_url": self.openai_base_url,
                **base_config
            }
    
    def get_rate_limit_config(self) -> dict:
        """Get rate limiting configuration"""
        return {
            "openrouter_rpm": self.openrouter_requests_per_minute,
            "groq_rpm": self.groq_requests_per_minute,
            "gemini_rpm": self.gemini_requests_per_minute,
            "openai_rpm": self.openai_requests_per_minute,
            "max_retries": self.max_retries,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay,
            "exponential_backoff": self.enable_exponential_backoff,
            "respect_retry_after": self.respect_retry_after_header,
            "monitoring_enabled": self.enable_rate_limit_monitoring,
            "unlimited_mode": self.unlimited_mode
        }
    
    def get_embedding_config(self) -> dict:
        """Get embedding configuration"""
        return {
            "model": self.embedding_model,
            "dimension": self.embedding_dimension,
            "batch_size": self.embedding_batch_size,
            "unlimited_mode": self.unlimited_mode
        }
    
    def get_vector_config(self) -> dict:
        """Get vector database configuration"""
        return {
            "pinecone_api_key": self.pinecone_api_key,
            "pinecone_env": self.pinecone_env,
            "index_name": self.pinecone_index_name,
            "storage_path": self.vector_storage_path,
            "similarity_threshold": self.similarity_threshold,
            "enable_compression": self.enable_compression,
            "unlimited_results": True,
            "max_results": self.max_search_results
        }
     
# Initialize settings instance
settings = Settings()

# Create necessary directories
os.makedirs("data/vectors", exist_ok=True)
os.makedirs("data/indexes", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("temp", exist_ok=True)
os.makedirs("cache", exist_ok=True)

def validate_config():
    """Validate configuration settings — called at startup, not at import"""
    provider = settings.get_active_provider()
    api_key = settings.get_active_api_key()
    
    if not api_key:
        print("WARNING: No LLM API key configured. Set one of:")
        print("   OPENROUTER_API_KEY, GROQ_API_KEY, GEMINI_API_KEY, or OPENAI_API_KEY")
        print("   The app will start but LLM queries will use fallback answers.")
        return
    
    print(f"Configuration validated successfully")
    print(f"   LLM Provider: {provider}")
    print(f"   Embedding Model: {settings.embedding_model}")
    print(f"   Embedding Dimension: {settings.embedding_dimension}")
    print(f"   Max Context Chunks: {settings.max_context_chunks}")
    print(f"   Hybrid Search: {'Enabled' if settings.hybrid_search_enabled else 'Disabled'}")