### Messy LLM Response

Here's an explanation of gradient descent:


**Gradient descent** is an optimization algorithm.

The cost function is:

\[
J(\theta) = \frac{1}{2m} \sum_{i=1}^{m} (h_\theta(x^{(i)}) - y^{(i)})^2
\]

The update rule is \(w := w - \alpha \nabla J(w)\).

The learning rate $\alpha$ controls convergence.


* Step 1: Initialize weights
* Step 2: Compute predictions
* Step 3: Calculate error
  * Sub-step: Use backpropagation


~~~python
def gradient_step(w, lr, grad):
    return w - lr * grad
~~~

| Algorithm | Convergence | Memory |
|---|---|---|
| SGD | Slow | Low |
| Adam | Fast | Medium |
| L-BFGS | Fast | High |



> **Note:** Always normalize your features before training.

The price is $50 per epoch, and variables like $CUDA_VISIBLE_DEVICES matter.
