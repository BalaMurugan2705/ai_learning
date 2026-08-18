# Client API

The Acme SDK Client provides methods for communicating with the Acme API.

## Client.send()

Sends an HTTP request to the Acme API.

### Parameters

| Name             | Type   | Default | Required |
|------------------|--------|---------|----------|
| timeout          | int    | 30      | no       |
| retry_backoff_ms | int    | 500     | no       |
| max_retries      | int    | 3       | no       |

The `retry_backoff_ms` parameter specifies the delay in milliseconds between retry attempts.

The `max_retries` parameter specifies how many times the SDK retries a failed request.

### Example

```python
client.send(
    timeout=30,
    retry_backoff_ms=500,
    max_retries=3
)
```

## Client.close()

Closes the active SDK connection.

### Example

```python
client.close()
```