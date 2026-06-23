# Security Notice

## Credential Management

All sensitive credentials have been removed from this repository.

### Configuration

Users must create `config/.env` with their own credentials:

```bash
# Copy template
cp config/.env.example config/.env

# Edit with your credentials
nano config/.env
```

### Important

- **config/.env** is gitignored and will never be committed
- Only **config/.env.example** with placeholders is in the repository
- Never commit API keys, passwords, or secrets

### If Credentials Are Exposed

1. Rotate credentials immediately
2. Delete exposed Elasticsearch API key
3. Create new API key
4. Update config/.env

### Contact

Security issues: uday@elastic.co

**Last Updated:** 2026-06-23
