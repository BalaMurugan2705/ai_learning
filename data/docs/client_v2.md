# Client API

The Acme SDK Client provides methods for communicating with the Acme API.

## Client.send()

Sends an HTTP request to the Acme API.

### Parameters

| Name             | Type | Default |
|------------------|------|---------|
| timeout          | int  | 60      |
| retry_backoff_ms | int  | 1000    |
| max_retries      | int  | 2       |

The `retry_backoff_ms` parameter specifies the delay between retry attempts.

### Example

```python
client.send(
    timeout=60,
    retry_backoff_ms=1000,
    max_retries=2
)