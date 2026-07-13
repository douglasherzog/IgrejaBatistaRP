import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware para Rate Limiting"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # Obter IP do cliente
        client_ip = self.get_client_ip(request)
        current_time = time.time()
        
        # Limpar requisições antigas (mais de 1 minuto)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < 60
        ]
        
        # Verificar se excedeu o limite
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Muitas requisições. Tente novamente em alguns minutos."
            )
        
        # Adicionar requisição atual
        self.requests[client_ip].append(current_time)
        
        return await call_next(request)
    
    def get_client_ip(self, request: Request) -> str:
        """Obtém o IP real do cliente"""
        # Verificar headers comuns de proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback para IP direto
        return request.client.host if request.client else "unknown"

class SlowAttackProtection(BaseHTTPMiddleware):
    """Middleware para proteção contra ataques lentos"""
    
    def __init__(self, app, max_delay_seconds: int = 10):
        super().__init__(app)
        self.max_delay_seconds = max_delay_seconds
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Se a requisição demorar muito, pode ser um ataque
            if time.time() - start_time > self.max_delay_seconds:
                raise HTTPException(
                    status_code=408,
                    detail="Request timeout"
                )
            raise e
