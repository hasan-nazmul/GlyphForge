# Code Block Test

## Python

```python
import numpy as np

def sigmoid(z):
    return 1 / (1 + np.exp(-z))
```

## JavaScript

```javascript
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}
```

## SQL

```sql
SELECT users.name, COUNT(orders.id) as order_count
FROM users
LEFT JOIN orders ON users.id = orders.user_id
GROUP BY users.name
HAVING order_count > 5;
```

## No Language

```
This is a code block without a language specifier.
It should be preserved as-is.
```

## Bash

```bash
#!/bin/bash
echo "Hello, $USER!"
for i in {1..10}; do
    echo "Count: $i"
done
```
