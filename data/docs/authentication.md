# Authentication API

The Acme SDK uses API keys to authenticate requests.

## Authentication.configure()

Configures authentication credentials for the SDK client.

### Parameters

| Name    | Type   | Default | Required |
|---------|--------|---------|----------|
| api_key | string | none    | yes      |
| timeout | int    | 10      | no       |

The `api_key` parameter contains the API key used to authenticate requests.

### Example

```python
authentication.configure(
    api_key="your-api-key",
    timeout=10
)
```

## Authentication.clear()

Removes the currently configured API credentials.

### Example

```python
authentication.clear()
```