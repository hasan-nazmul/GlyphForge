---
title: Logistic Regression
author: Nazmul Hasan
subject: Machine Learning
tags:
  - machine-learning
  - statistics
  - classification
date: 2026-09-16
---

# Logistic Regression

Logistic regression predicts the probability of a binary outcome.

The sigmoid function is:

$$
\sigma(z)=\frac{1}{1+e^{-z}}
$$

For input vector $\mathbf{x}$:

$$
z=\mathbf{w}^{T}\mathbf{x}+b
$$

Therefore:

$$
\hat{y}
=
\sigma(\mathbf{w}^{T}\mathbf{x}+b)
$$

## Cost Function

The binary cross-entropy loss is:

$$
J(\theta)
=
-\frac{1}{m}
\sum_{i=1}^{m}
\left[
y_i\log(\hat{y}_i)
+
(1-y_i)\log(1-\hat{y}_i)
\right]
$$

## Gradient Descent

The gradient of the cost function with respect to each parameter is:

$$
\frac{\partial J}{\partial w_j}
=
\frac{1}{m}
\sum_{i=1}^{m}
(\hat{y}_i - y_i) x_{ij}
$$

The update rule is:

$$
w_j := w_j - \alpha \frac{\partial J}{\partial w_j}
$$

where $\alpha$ is the learning rate.

## Implementation

```python
import numpy as np

def sigmoid(z):
    """Compute the sigmoid function."""
    return 1 / (1 + np.exp(-z))

def compute_cost(X, y, w, b):
    """Compute binary cross-entropy cost."""
    m = len(y)
    z = np.dot(X, w) + b
    y_hat = sigmoid(z)
    cost = -(1/m) * np.sum(y * np.log(y_hat) + (1 - y) * np.log(1 - y_hat))
    return cost

def gradient_descent(X, y, w, b, alpha, iterations):
    """Run gradient descent to optimize parameters."""
    m = len(y)
    for _ in range(iterations):
        z = np.dot(X, w) + b
        y_hat = sigmoid(z)
        dw = (1/m) * np.dot(X.T, (y_hat - y))
        db = (1/m) * np.sum(y_hat - y)
        w = w - alpha * dw
        b = b - alpha * db
    return w, b
```

## Comparison

| Model | Output | Loss | Decision Boundary |
|---|---|---|---|
| Linear Regression | $\hat y \in \mathbb{R}$ | MSE | None |
| Logistic Regression | $\hat y \in [0,1]$ | Log Loss | $P(y=1) = 0.5$ |

## Key Properties

- Logistic regression is a **linear classifier**.
- The decision boundary is where $P(y=1|x) = 0.5$.
- It can be extended to multi-class via **softmax regression**.

1. Train the model on labeled data.
2. Compute the sigmoid of the linear combination.
3. Classify based on a threshold (typically 0.5).

> Logistic regression is a classification model even though the underlying mathematical function is continuous.

## Mathematical Notation Reference

The probability mass function is $P(X=x)$ for discrete random variables.

Set membership is denoted $\forall x \in X$.

The real numbers are $\mathbb{R}$.

A matrix example:

$$
\mathbf{W} = \begin{bmatrix}
w_{11} & w_{12} \\
w_{21} & w_{22}
\end{bmatrix}
$$

An integral:

$$
\int_0^1 f(x)\,dx
$$
