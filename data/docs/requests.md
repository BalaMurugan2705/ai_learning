# Requests API

The Requests API provides request configuration options.

## Request.create()

Creates a new API request.

### Parameters

| Name        | Type   | Default | Required |
|-------------|--------|---------|----------|
| method      | string | GET     | yes      |
| timeout     | int    | 30      | no       |
| compression | bool   | true    | no       |

The `compression` parameter enables response compression for the request.

### Example

```python
request = Request.create(
    method="GET",
    timeout=30,
    compression=True
)
```

## Request.cancel()

Cancels an active request.

### Example

```python
request.cancel()
```