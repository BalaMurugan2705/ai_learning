# Responses API

The Responses API provides access to API response information.

## Response.parse()

Parses a raw API response.

### Parameters

| Name       | Type | Default | Required |
|------------|------|---------|----------|
| strict     | bool | true    | no       |
| max_size   | int  | 1048576 | no       |

The `strict` parameter controls whether malformed response data causes an error.

### Example

```python
response = Response.parse(
    raw_response,
    strict=True
)
```

## Response.status_code()

Returns the HTTP status code of the response.

### Example

```python
code = response.status_code()
```