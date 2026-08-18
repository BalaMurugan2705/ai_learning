# Errors API

The Acme SDK defines standard errors for failed operations.

## ErrorHandler.configure()

Configures error handling behavior.

### Parameters

| Name          | Type   | Default | Required |
|---------------|--------|---------|----------|
| retry_enabled | bool   | true    | no       |
| log_level     | string | error   | no       |

The `retry_enabled` parameter controls whether retry handling is enabled.

### Example

```python
ErrorHandler.configure(
    retry_enabled=True,
    log_level="error"
)
```

## ErrorHandler.reset()

Resets the current error handling configuration.

### Example

```python
ErrorHandler.reset()
```