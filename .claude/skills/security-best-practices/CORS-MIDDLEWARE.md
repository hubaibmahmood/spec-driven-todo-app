# CORS Configuration Guide

## Understanding CORS

CORS (Cross-Origin Resource Sharing) allows controlled access from web pages at one origin to resources at another origin.

## Configuration Options

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specific origins
    allow_credentials=True,                   # Allow cookies
    allow_methods=["*"],                      # Allowed HTTP methods
    allow_headers=["*"],                      # Allowed headers
    expose_headers=["X-Total-Count"],         # Headers exposed to JS
    max_age=3600,                             # Preflight cache duration
)
```

## Common Configurations

### Development
```python
# Allow all origins (DEV ONLY!)
allow_origins=["*"]
allow_credentials=False  # Must be False when origins is ["*"]
```

### Production
```python
# Specific origins only
allow_origins=[
    "https://app.example.com",
    "https://www.example.com"
]
allow_credentials=True
allow_methods=["GET", "POST", "PUT", "DELETE"]
allow_headers=["Authorization", "Content-Type"]
```

### Multiple Environments
```python
import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    origins = ["https://app.example.com"]
elif ENVIRONMENT == "staging":
    origins = ["https://staging.example.com"]
else:
    origins = ["http://localhost:3000", "http://localhost:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

### Issue: "No 'Access-Control-Allow-Origin' header"
**Solution**: Add frontend URL to `allow_origins`

### Issue: "Credentials flag is true but 'Access-Control-Allow-Credentials' header is ''"
**Solution**: Set `allow_credentials=True`

### Issue: "Method not allowed by CORS"
**Solution**: Add method to `allow_methods` or use `["*"]`

## Security Considerations

1. **Never use `allow_origins=["*"]` in production**
2. **Only allow credentials with specific origins**
3. **Limit allowed methods to what's needed**
4. **Be specific with headers**
5. **Use HTTPS in production**
