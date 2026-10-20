### The Foundational Concepts

* **Correlation Analysis:** Measures the **direction** and **strength** of a linear association between two continuous variables ($X$ and $Y$). It does not assume causation—neither variable is designated as "dependent" or "independent".


* **Linear Regression:** Models the **functional dependency** between an independent variable $X$ (predictor) and a continuous dependent variable $Y$ (response):



$$y = \beta_0 + \beta_1 x$$



It finds the "best-fitting line" to predict unknown future values of $Y$ given $X$.


* (Note: PCA is explicitly excluded from your syllabus per your notes: "PCA বাদ").



---

### Variation 1: Pearson’s Correlation Coefficient and Scatterplots

#### 1. How Pearson’s Correlation ($r$) Works

Pearson’s correlation coefficient ($r$) evaluates how two numeric variables change together relative to their individual variances:

$$r = \frac{\sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^n (x_i - \bar{x})^2} \sqrt{\sum_{i=1}^n (y_i - \bar{y})^2}} = \frac{\text{Cov}(X, Y)}{s_X s_Y}$$

* **Range:** Always bounded strictly between **$-1.0$ and $+1.0$**.


* **Interpretation of Values:**
* $r = +1.0$: Perfect positive linear correlation (as $X$ increases, $Y$ increases proportionally).


* $0.7 \le r < 1.0$: Strong positive correlation.


* $r = 0.0$: No linear relationship (the variables are linearly independent).


* $-1.0 < r \le -0.7$: Strong negative correlation.


* $r = -1.0$: Perfect negative linear correlation (as $X$ increases, $Y$ decreases proportionally).





---

#### 2. Scatterplot Patterns & The "Price vs. Demand" Scenario

Your handwritten notes highlight: *"Scatterplot (যত price বাড়ে demand বাড়ে)"*.

A **Scatterplot** plots individual observation pairs $(x_i, y_i)$ as points on a 2D Cartesian plane. It provides an immediate visual diagnostic of correlation before any mathematical equations are computed:

```text
       Positive (r > 0)             Negative (r < 0)               No Correlation (r ≈ 0)
    Y ^         * *              Y ^   *                         Y ^      *    *
      |       * *                  |     *   *                     |    *   *    *
      |     * *                    |       * *                     |      *    *
      |   * *                      |         * *                   |    *    *   *
      +-------------> X            +-------------> X               +-------------> X

```

* **Standard Economic Relationship (Negative Correlation):**
* Under normal market rules (Law of Demand), as **Price ($X$) increases, Quantity Demand ($Y$) decreases**.


* **Scatterplot slope:** Slopes downward from left to right.


* **Correlation:** $r < 0$ (negative).




* **The Scenario: "যত Price বাড়ে, Demand বাড়ে" (Positive Correlation):**

* If empirical data reveals that as **Price increases, Demand also increases**, points trend upward from left to right.


* **Correlation:** $r > 0$ (positive).


* **Evaluation / Justification:**
* In standard economics, this describes **Veblen Goods** (luxury/status items like high-end sports cars or designer watches where high price signals prestige) or **Giffen Goods** (inferior staple foods during severe scarcity).


* In data analysis, this signals a positive covariance $\text{Cov}(\text{Price}, \text{Demand}) > 0$, yielding a positive regression slope $\beta_1 > 0$.







---

### Variation 2: Simple Linear Regression

#### 1. What Will Be Given vs. What You Have to Solve

* **Given:** A paired data table with independent values $X$ (e.g., Year, Advertising, Price) and dependent values $Y$ (e.g., Population, Sales, Demand).


* **Task:**
1. Calculate means $\bar{x}$ and $\bar{y}$.


2. Compute slope $\beta_1$ and intercept $\beta_0$.


3. Form the regression line: $\hat{y} = \beta_0 + \beta_1 x$.


4. Predict the target value for a specific $x_{\text{test}}$.





#### 2. The Core Formulas (Ordinary Least Squares - OLS)

$$\beta_1 = \frac{\sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})}{\sum_{i=1}^n (x_i - \bar{x})^2} = \frac{n\sum (x_i y_i) - (\sum x_i)(\sum y_i)}{n\sum x_i^2 - (\sum x_i)^2}$$

$$\beta_0 = \bar{y} - \beta_1 \bar{x}$$

---

#### 3. Worked Exam Example: Year vs. Population Prediction

> **Exam Problem (Spring 2024 / Autumn 2023, Q3a):**
> 
> 
> Suppose you have the following one-dimensional dataset:
> | Year ($x$) | 1980 | 1985 | 1990 | 1995 | 2000 | 2005 |
> | --- | --- | --- | --- | --- | --- | --- |
> | **Population ($y$)** | 2.1 | 2.9 | 3.2 | 4.1 | 4.9 | 7.0 |
> 
> 
> Apply linear regression to develop a model and predict the population for a given target year.
> 
> 

**Step-by-step Solution:**

* **Tip for Exam Calculation:** Working with large numbers like $1980^2$ causes manual calculation mistakes. To simplify, code the base year:
Let $t_i = \frac{x_i - 1980}{5} \implies t \in \{0, 1, 2, 3, 4, 5\}$ (or center by the mean).
Alternatively, work with standard centered coordinates $(x_i - \bar{x})$:


* **Step 1: Compute Means**
* $n = 6$

* $\sum x_i = 1980 + 1985 + 1990 + 1995 + 2000 + 2005 = 11955$

$$\bar{x} = \frac{11955}{6} = 1992.5$$


* $\sum y_i = 2.1 + 2.9 + 3.2 + 4.1 + 4.9 + 7.0 = 24.2$

$$\bar{y} = \frac{24.2}{6} \approx 4.033$$




* **Step 2: Construct the Computation Table**

| Year ($x_i$) | Pop ($y_i$) | $(x_i - \bar{x})$ | $(x_i - \bar{x})^2$ | $(y_i - \bar{y})$ | $(x_i - \bar{x})(y_i - \bar{y})$ |
| --- | --- | --- | --- | --- | --- |
| 1980 | 2.1 | $-12.5$ | 156.25 | $-1.933$ | $+24.1625$ |
| 1985 | 2.9 | $-7.5$ | 56.25 | $-1.133$ | $+8.4975$ |
| 1990 | 3.2 | $-2.5$ | 6.25 | $-0.833$ | $+2.0825$ |
| 1995 | 4.1 | $+2.5$ | 6.25 | $+0.067$ | $+0.1675$ |
| 2000 | 4.9 | $+7.5$ | 56.25 | $+0.867$ | $+6.5025$ |
| 2005 | 7.0 | $+12.5$ | 156.25 | $+2.967$ | $+37.0875$ |
| **Sum** | **24.2** | **0** | **437.5** | **0** | **78.50** |

* **Step 3: Calculate Slope ($\beta_1$) and Intercept ($\beta_0$)**

$$\beta_1 = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2} = \frac{78.50}{437.5} \approx 0.1794$$


$$\beta_0 = \bar{y} - \beta_1 \bar{x} = 4.033 - (0.1794 \times 1992.5) = 4.033 - 357.4545 = -353.4215$$


* **Step 4: Form the Prediction Equation**

$$\hat{y} = -353.4215 + 0.1794 \cdot x$$


* **Step 5: Predict Target Value (e.g., Year 2010 or 2005)**

* For Year $x = 2010$:

$$\hat{y} = -353.4215 + 0.1794(2010) = -353.4215 + 360.594 \approx 7.17$$


* For Year $x = 2005$:

$$\hat{y} = -353.4215 + 0.1794(2005) = -353.4215 + 359.697 \approx 6.28$$





---

### Variation 3: How Error Is Calculated in Linear Regression

A recurring question in past papers asks: *"How is the error calculated in a Linear Regression model? Explain with an example."*

#### 1. Theoretical Explanation

The regression model predicts values $\hat{y}_i$, but the real observations are $y_i$. The difference between what actually occurred and what the line predicted is called the **Residual** or **Error** ($e_i$):

$$e_i = y_i - \hat{y}_i$$

Because some errors are positive (above the line) and some are negative (below the line), simply adding them yields zero: $\sum e_i = 0$. To evaluate the overall model accuracy, error is quantified using four primary metrics:

| Error Metric | Formula | What It Measures |
| --- | --- | --- |
| **Sum of Squared Errors (SSE)**<br> | $\text{SSE} = \sum_{i=1}^n (y_i - \hat{y}_i)^2$ | Total squared residual penalty (the objective minimized by OLS).

 |
| **Mean Squared Error (MSE)** | $\text{MSE} = \frac{1}{n}\sum_{i=1}^n (y_i - \hat{y}_i)^2 = \frac{\text{SSE}}{n}$ | Average squared penalty across all training samples. |
| **Root Mean Squared Error (RMSE)** | $\text{RMSE} = \sqrt{\text{MSE}}$ | Error expressed in the exact original units of $Y$ (penalizes large outlier mistakes heavily). |
| **Mean Absolute Error (MAE)** | $\text{MAE} = \frac{1}{n}\sum_{i=1}^n \Vert{}y_i - \hat{y}_i\Vert{}$ | Average absolute magnitude of errors (more robust against extreme outliers). |

---

#### 2. Illustrative Exam Example with Step-by-Step Table

To get full marks when asked to *"Explain with an example"*:

* Suppose we have a small fitted regression line $\hat{y} = 1.0 + 2.0 x$ and three observed data points:
* Point 1: $(x_1 = 1, y_1 = 3.5)$
* Point 2: $(x_2 = 2, y_2 = 4.8)$
* Point 3: $(x_3 = 3, y_3 = 7.2)$


* **Step 1: Compute Predicted Values ($\hat{y}_i$)**
* $\hat{y}_1 = 1.0 + 2.0(1) = 3.0$
* $\hat{y}_2 = 1.0 + 2.0(2) = 5.0$
* $\hat{y}_3 = 1.0 + 2.0(3) = 7.0$


* **Step 2: Construct the Error Evaluation Table**

| Point ($i$) | Actual ($y_i$) | Predicted ($\hat{y}_i$) | Residual ($e_i = y_i - \hat{y}_i$) | Squared Error ($e_i^2$) | Absolute Error ($\Vert{}e_i\Vert{}$) |
| --- | --- | --- | --- | --- | --- |
| 1 | 3.5 | 3.0 | $+0.5$ | 0.25 | 0.5 |
| 2 | 4.8 | 5.0 | $-0.2$ | 0.04 | 0.2 |
| 3 | 7.2 | 7.0 | $+0.2$ | 0.04 | 0.2 |
| **Total** |  |  | **Sum = 0.5** | **$\text{SSE} = 0.33$** | **$\sum \Vert{}e_i\Vert{} = 0.9$** |

* **Step 3: Calculate the Summary Metrics**
* **Sum of Squared Errors (SSE):**

$$\text{SSE} = 0.25 + 0.04 + 0.04 = 0.33$$


* **Mean Squared Error (MSE):**

$$\text{MSE} = \frac{\text{SSE}}{n} = \frac{0.33}{3} = 0.11$$


* **Root Mean Squared Error (RMSE):**

$$\text{RMSE} = \sqrt{0.11} \approx 0.332$$


* **Mean Absolute Error (MAE):**

$$\text{MAE} = \frac{0.9}{3} = 0.30$$





---

### Variation 4: Key Evaluation & Conceptual Questions

#### 1. Why Is Regression Analysis Used?



* **Prediction / Forecasting:** Predicting continuous target values for unseen instances (e.g., forecasting tomorrow's temperature, next quarter's revenue, or city population in 2030).


* **Trend & Impact Assessment:** Quantifying the strength and direction of influence that specific predictors have on the response (e.g., how much does each additional year of education increase starting salary?).



#### 2. Regression vs. Correlation (When to Use Which?)

| Dimension | Correlation Analysis | Regression Analysis |
| --- | --- | --- |
| **Primary Goal**<br> | Measure the strength of mutual association ($r$).

 | Fit a predictive equation to forecast $Y$ from $X$.

 |
| **Variables**<br> | Both variables are treated symmetrically ($r_{xy} = r_{yx}$).

 | Asymmetric: distinct Independent ($X$) and Dependent ($Y$).

 |
| **Output** | A single dimensionless coefficient between $-1$ and $+1$.

 | A mathematical line / equation: $y = \beta_0 + \beta_1 x$.

 |
| **Units** | Unit-free (dimensionless).

 | Measured in the specific physical units of the dependent variable.

 |