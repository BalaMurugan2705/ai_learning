# Pagination API

The Pagination API helps applications retrieve large result sets.

## Pagination.configure()

Configures pagination behavior.

### Parameters

| Name      | Type | Default | Required |
|-----------|------|---------|----------|
| page_size | int  | 50      | no       |
| max_pages | int  | 10      | no       |

The `page_size` parameter controls the number of records requested per page.

### Example

```python
pagination.configure(
    page_size=50,
    max_pages=10
)
```

## Pagination.next()

Retrieves the next page of results.

### Example

```python
next_page = pagination.next()
```