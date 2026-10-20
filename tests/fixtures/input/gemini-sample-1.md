## Module 1: Introduction to Data Mining & Foundational Concepts

### 1. Data Mining Definition & Essence

* **Core Definition:** Data mining is the non-trivial extraction of implicit, previously unknown, and potentially useful patterns, rules, and knowledge from massive volumes of data stored in databases, data warehouses, or other information repositories.


* **Interdisciplinary Nature:** It is not a simple database query (SQL) or basic data manipulation. It is an applied confluence of multiple disciplines: **Databases** (scalable storage & retrieval), **Statistics** (mathematical modeling of distributions and error), **Machine Learning** (predictive algorithms and adaptive models), and **Pattern Recognition** (structural and visual pattern discovery).


* **"We are drowning in data, but starving for knowledge!":**

* **Agreement:** This statement captures the modern digital reality. Automated transactions, IoT sensors, social media, and web logs generate exabytes of raw data daily, creating a data-rich environment.


* **The Problem:** Raw, unstructured data possesses little direct operational value. Without automated discovery tools, human analysts cannot process or extract actionable insights, strategic competitive advantages, or predictive patterns from this volume. Data mining bridges this gap by transforming raw data into structured knowledge.





---

### 2. Scenario Classification: Is It a Data Mining Task or Not?

(High-yield question appearing across all past midterms; must include a clear, one-sentence justification)

| Activity / Scenario | Data Mining Task? | One-Sentence Justification |
| --- | --- | --- |
| **Dividing the customers of a company according to their profitability**<br> | **YES** | It discovers hidden behavioral spending patterns and multi-attribute profitability clusters that are not predetermined by a simple attribute filter.

 |
| **Dividing the customers of a company according to their gender**<br> | **NO** | It is a trivial database query / filtering operation based on an explicitly declared categorical attribute without discovering new patterns.

 |
| **Monitoring seismic waves for earthquake activities**<br> | **YES** | It involves real-time anomaly detection, complex pattern recognition, and trend analysis over continuous sensor time-series data to detect anomalous earthquake signatures.

 |
| **Monitoring the heart rate of a patient for abnormalities**<br> | **YES** | It applies outlier and anomaly detection algorithms to dynamic medical time-series signals to classify abnormal cardiac waveforms.

 |
| **Sorting a student database based on student identification numbers**<br> | **NO** | It is a standard deterministic algorithmic sorting operation ($O(N \log N)$) that uncovers no hidden knowledge or behavioral patterns.

 |
| **Predicting the outcomes of tossing a (fair) pair of dice / fair coin**<br> | **NO** | Fair coin or dice tosses are purely random, independent Bernoulli events governed by fixed, memoryless theoretical probability ($P = 1/6$ or $1/2$), meaning past historical data contains zero predictable underlying patterns.

 |
| **Predicting future stock prices using historical records**<br> | **YES** | It builds predictive regression and temporal models by analyzing historical multivariate trends, market patterns, and financial signals.

 |
| **Recommending videos for YouTube users / field of study for students**<br> | **YES** | It uses collaborative and content-based recommendation algorithms to discover latent user preferences from implicit historical interaction patterns.

 |
| **Extracting the frequencies of a sound wave**<br> | **NO** | It is a deterministic digital signal processing calculation (e.g., Fast Fourier Transform) that does not discover behavioral patterns or infer knowledge.

 |

---

### 3. When Can You Say a Machine is Learning?

A computer program is said to **learn** from experience $E$ with respect to some class of tasks $T$ and performance measure $P$, if its performance at tasks in $T$, as measured by $P$, improves with experience $E$ (Tom Mitchell’s formal definition).

#### Machine Learning Categorization



* **Supervised Learning:** The model is trained on labeled data $(X, y)$, learning an input-to-output mapping function.


* *Categories:* **Classification** (discrete labels; e.g., predicting spam vs. non-spam), **Regression** (continuous numbers; e.g., predicting house prices).




* **Unsupervised Learning:** The model finds latent structure, patterns, or groupings directly from unlabeled data $X$ without teacher feedback.


* *Categories:* **Clustering** (e.g., customer market segmentation using k-Means), **Association Rule Mining** (e.g., market basket analysis via Apriori).




* **Semi-Supervised Learning:** Combines a small volume of labeled data with a large volume of unlabeled data to improve learning accuracy without prohibitive manual labeling costs.
* **Reinforcement Learning:** An autonomous agent learns optimal policies through trial-and-error interaction with a dynamic environment via **rewards** and **penalties** (e.g., AlphaGo, self-driving vehicle navigation).



---

### 4. Data Mining Functionalities (Tasks)



* **Data Characterization:** Summarizing the general characteristics or features of a target class of data (e.g., summarizing the demographic traits of high-spending software purchasers).


* **Data Discrimination:** Comparing the general features of the target class with comparative classes (e.g., contrasting the GPA and attendance profiles of graduating students versus dropouts).


* **Association and Correlation Analysis:** Discovering frequent co-occurring itemsets and rules showing how attribute values correlate within transactions (e.g., "Customers who buy bread also buy butter $75\%$ of the time").


* **Classification:** Building a predictive model to map data instances into discrete class labels (e.g., classifying loan applicants as "High Risk" or "Low Risk").


* **Regression Analysis:** Modeling continuous-valued functions to forecast numerical trends (e.g., predicting a patient's blood pressure given age, weight, and dosage).


* **Clustering:** Partitioning data into groups (clusters) where intra-cluster similarity is maximized and inter-cluster similarity is minimized, without predefined labels.


* **Outlier Analysis:** Detecting data objects that deviate significantly from general distribution trends, treating them as noise, fraud, or exceptional events (e.g., credit card fraud detection).



---

## Module 2: Knowledge Discovery in Databases (KDD) Process

The KDD process is an iterative sequence of steps that transforms raw, heterogeneous data into validated, operational knowledge.

```text
[Raw Data] ---> 1. Data Cleaning ---> 2. Data Integration ---> 3. Data Selection 
              ---> 4. Data Transformation ---> 5. Data Mining 
              ---> 6. Pattern Evaluation ---> 7. Knowledge Presentation ---> [Knowledge]

```

### 1. General Stages of KDD



1. **Data Cleaning:** Removes noise, eliminates inconsistent records, and handles missing attribute values.


2. **Data Integration:** Combines heterogeneous data sources (e.g., multiple relational databases, CSV spreadsheets, flat logs) into a unified repository.


3. **Data Selection:** Retrieves only the subset of data relevant to the specific business analysis or prediction task.


4. **Data Transformation:** Converts data into states suitable for mining through **normalization**, **aggregation**, **discretization/binning**, and feature engineering.


5. **Data Mining:** Applies intelligent machine learning algorithms to extract recurring patterns, decision boundaries, or statistical clusters.


6. **Pattern Evaluation:** Identifies truly interesting, statistically valid, novel, and actionable patterns using evaluation metrics (e.g., Confidence, Lift, ROC-AUC, F1-Score).


7. **Knowledge Presentation:** Visualizes extracted patterns (via dashboards, decision trees, scatter plots) to support end-user decision-making.



---

### 2. Scenario-Based Application: "Predicting Student Academic Performance"

(Exam Question Spring 2026, Q1b & Handwritten Notes)

| Stage | Concrete Action for Student Performance Prediction

 |
| --- | --- |
| **1. Data Selection**<br> | Extract student records from university databases, targeting demographics, semester GPA history, mid-term scores, course attendance, and LMS interaction logs.

 |
| **2. Data Cleaning**<br> | Remove duplicate student entries; impute missing test marks using department mean; identify and rectify data entry errors (e.g., negative attendance days or GPA $> 4.0$).

 |
| **3. Data Integration**<br> | Merge the Registrar's academic records, LMS portal login logs, and faculty assignment spreadsheets using `Student_ID` as the primary key.

 |
| **4. Data Transformation**<br> | Convert continuous marks into discretized grades; apply min-max or z-score normalization on `Number_of_absent_days` and `LMS_hours`; encode categorical attributes (e.g., Department, Gender).

 |
| **5. Data Mining**<br> | Train classification models (Decision Trees, Random Forests, or Logistic Regression) where input features predict final academic standing (`Good`, `Average`, `At Risk`).

 |
| **6. Pattern Evaluation**<br> | Evaluate accuracy, precision, and recall using test data; filter rules (e.g., "IF Attendance $< 75\%$ AND Quiz Average $< 40\%$, THEN Academic Risk $= 92\%$").

 |
| **7. Knowledge Presentation**<br> | Deliver an early-warning dashboard to department heads and academic advisors with visual risk indicators to identify students needing intervention before final examinations.

 |

---

## Module 3: Data Types, Attribute Scales & Distance Metric Selection

### 1. Attribute Types & Measurement Scales



* **Nominal Attributes:** Categorical values representing names, categories, or states without any meaningful intrinsic mathematical order.


* *Operations:* Only equality ($==, \neq$); Mode can be computed; Mean/Median cannot.


* *Examples:* Gender, Department, Marital Status, Eye Color.




* **Ordinal Attributes:** Categorical values that possess a meaningful ranking or sequence, but the mathematical distances between successive ranks cannot be quantified.


* *Operations:* Order comparisons ($<, >$); Median and Mode can be computed; differences cannot be computed directly without ranking.


* *Examples:* Performance Level (`Poor`, `Average`, `Good`, `Excellent`), Academic Grades (`A`, `B`, `C`), Army Ranks.




* **Binary Attributes:** A nominal attribute possessing exactly two distinct categories (0 and 1).


* **Symmetric Binary:** Both states are equally valuable and carry identical conceptual weight (e.g., Gender: `Male` vs. `Female`).


* **Asymmetric Binary:** The presence of the positive state ($1$) is significant and rare, while mutual absence ($0$) carries no informational similarity (e.g., Medical tests for rare diseases: positive vs. negative; Fraudulent vs. Legitimate transactions).




* **Numeric (Quantitative) Attributes:** Quantities represented as integers or real numbers.


* **Interval-Scaled Numeric:** Values measured on a scale of equal-sized units, but **without a true, meaningful absolute zero point** (the zero point is arbitrary). Ratios are meaningless.


* *Examples:* Temperature in Celsius/Fahrenheit ($0^\circ\text{C}$ does not indicate total absence of heat; $40^\circ\text{C}$ is not "twice as hot" as $20^\circ\text{C}$), Calendar dates.




* **Ratio-Scaled Numeric:** Measured on a scale with an **absolute, non-arbitrary zero point** (where zero represents complete absence of the property). Ratios are mathematically meaningful.


* *Examples:* CGPA, Salary, Age, Distance, Number of absent days ($0$ absent days means no absence; $\$100,000$ is twice as much as $\$50,000$).







---

### 2. Real-Life Attribute Classification with Justification

(Exam Problem Spring 2026, Q1c)

* **Student ID:** **Categorical (Nominal / Identifier)**. Justification: Numbers are arbitrary codes used solely for unique record identification; arithmetic operations ($ID_1 + ID_2$) are meaningless.


* **CGPA:** **Numerical (Ratio-Scaled, Continuous)**. Justification: Values lie along a continuous mathematical continuum from $0.0$ to $4.0$ with a true zero representing no grade points earned, where proportional comparisons are valid.


* **Department:** **Categorical (Nominal)**. Justification: Distinct faculty names (CSE, EEE, BBA) with no inherent hierarchy, mathematical magnitude, or ranking.


* **Performance Level (Poor, Average, Good, Excellent):** **Categorical (Ordinal)**. Justification: Values exhibit an explicit qualitative rank order ($\text{Poor} < \text{Average} < \text{Good} < \text{Excellent}$), but the distance between consecutive steps cannot be quantified numerically.


* **Number of Absent Days:** **Numerical (Ratio-Scaled, Discrete)**. Justification: Countable non-negative integers with a true zero (zero absences) where ratios hold (4 days absent is twice as many as 2 days).



---

### 3. Scenario-Based Proximity Metric Selection

(Exam Problem Spring 2025, Q2b OR & Handwritten Notes: "কখন কোনটা use করবো")

* **Application 1: Calculate driving distance between two locations in a city.**

* **Metric to Use:** **Manhattan Distance ($L_1$ Norm)**.


* **Justification:** Urban city road infrastructure is arranged in street grid blocks. Vehicles cannot travel diagonally through physical buildings (as measured by straight-line Euclidean distance); they must travel along orthogonal east-west and north-south streets, which matches the Manhattan formula ($d = \vert{}x_1 - x_2\vert{} + \vert{}y_1 - y_2\vert{}$).




* **Application 2: Compare similar diseases with a set of medical test results recorded as positive or negative.**

* **Metric to Use:** **Jaccard Distance / Asymmetric Binary Dissimilarity**.


* **Justification:** Medical test results are asymmetric binary variables. A patient testing positive for a symptom or disease marker is clinically informative, whereas two healthy patients both testing negative ($0-0$ match) provides no diagnostic evidence that they share a specific disease. Jaccard distance excludes mutual negative matches ($0-0$) from both the numerator and denominator.




* **Application 3: Find similar web documents to a keyword query.**

* **Metric to Use:** **Cosine Similarity**.


* **Justification:** Web documents are represented as high-dimensional, sparse term-frequency vectors. Document length varies significantly (a 5,000-word article vs. a 50-word abstract on the same topic). Euclidean distance is distorted by document length, whereas Cosine similarity evaluates the angle between the vectors, measuring conceptual topical similarity independent of length.





---

## Module 4: Data Preprocessing, Data Cleaning & Sampling

### 1. Why Data Preprocessing is Essential



Raw real-world industrial data is typically:

* **Incomplete:** Missing attributes, values, or class labels.


* **Noisy:** Containing errors, outliers, or random fluctuations.


* **Inconsistent:** Containing discrepancies in codes, naming conventions, or duplicate identifiers.



---

### 2. Missing Value Strategies: The Evaluation Decisions

(Handwritten Notes: "Drop করবে নাকি না, 0 দিয়ে replace করা যায় নাকি না")

#### A. When to Drop Rows vs. When to Impute Values



* **Decision: DROP the Row (Ignore Tuple)**

* When the class label itself is missing in a supervised learning task (imputing labels introduces artificial bias).


* When a data tuple has severe missingness across most attributes ($> 40\%-50\%$ missing).


* When the dataset has thousands of samples and the missing rows constitute a small, random fraction ($< 2\%$).




* **Decision: IMPUTE (Fill In) the Value**

* When the dataset size is small; dropping rows discards valid feature measurements in remaining columns.


* When missingness is systematic rather than random; dropping records would introduce selection bias.





#### B. Can We Replace Missing Values with 0? Is It a Good Decision?



* **Definitive Answer:** **No. Replacing missing values with 0 is generally a poor preprocessing decision and should be avoided.**

* **Justification:**

1. **Zero Represents a Measured Magnitude:** For continuous variables like `Age`, `Income`, `Blood_Pressure`, or `Humidity`, zero is an actual numerical state. A missing income represents an unrecorded response, whereas $\$0$ represents extreme poverty.


2. **Statistical Distortion:** Inserting zeros shifts the sample mean downward, inflates the sample variance, and skews normal distribution curves.


3. **Distance Corruption:** In distance-based models (k-Means, k-NN), a coordinate of $0$ places the record in an arbitrary coordinate region, distorting neighborhood calculations.




* **Exception:** 0 is valid only if the column represents a cumulative counter of discrete occurrences (e.g., `Number_of_Previous_Accidents`, `Loyalty_Points_Used`) where missingness indicates that the event never occurred.



#### C. Comparison of Missing Value Imputation Techniques



| Imputation Technique | When to Use | Advantages | Drawbacks |
| --- | --- | --- | --- |
| **Attribute Mean**<br> | Symmetric, continuous numerical attributes without extreme outliers.

 | Preserves the global arithmetic mean of the feature.

 | Artificially reduces sample variance; sensitive to outliers.

 |
| **Attribute Median**<br> | Skewed continuous distributions or numeric attributes with outliers.

 | **Robust against outliers**; reflects typical central value.

 | Does not capture multi-attribute correlations. |
| **Attribute Mode**<br> | Categorical or discrete nominal/ordinal attributes.

 | Fills missing values with the most probable discrete category.

 | Can bias distributions toward the majority category. |
| **Class-Conditional Mean/Median**<br> | When labeled subgroups exist (e.g., impute missing `Income` using the mean of the corresponding `Gender` or `Job_Title`).

 | Preserves subgroup variance and class separation boundaries.

 | Requires sufficient sample sizes within each subgroup. |

---

### 3. Sampling Strategies & Scenario Justifications

(Exam Problem Spring 2026 Q2b, Autumn 2025 Q3a, and Handwritten Notes)

* **Why Use Sampling?** Sampling is a **numerosity reduction** technique. Processing an entire enterprise dataset can be computationally expensive; a representative sample preserves the statistical properties of the population while enabling faster model training.



#### Core Sampling Methods & Exam Scenarios



* **1. Simple Random Sampling without Replacement (SRSWOR):**

* *Definition:* Every individual object in population size $N$ has an equal, non-zero probability of selection, and selected items are not returned to the pool.


* *Scenario:* "A class has 50 students, and a researcher selects 10 students, where every student has an equal chance of being selected."


* *Why Useful:* Unbiased, mathematically simple, and eliminates selection favoritism when the population is homogeneous.




* **2. Systematic Sampling:**

* *Definition:* Selecting elements from an ordered population list at regular intervals defined by sampling interval $k = N/n$, starting from a randomly chosen initial index.


* *Scenario:* "A researcher plans to study customer satisfaction in a busy supermarket by interviewing every 10th customer entering the store."


* *Justification:* Efficient in real-time continuous streams where total population count is not known in advance, ensuring uniform coverage across peak and off-peak hours.




* **3. Stratified Sampling:**

* *Definition:* The population is divided into mutually exclusive, non-overlapping subgroups (strata) based on a key characteristic, and random samples are drawn independently from each stratum.


* *Scenario:* "A university surveys student satisfaction across five faculties (Engineering, Business, Science, Arts, Law) by selecting exactly 50 students from each faculty to guarantee equal representation."


* *Justification:* Prevents smaller minority sub-populations from being under-represented or missed entirely, ensuring balanced statistical validity across all sub-groups.




* **4. Cluster Sampling:**
* *Definition:* The population is divided into natural clusters (e.g., city neighborhoods, university dormitories); a random sample of whole clusters is selected, and all elements within those chosen clusters are surveyed.



---

## Module 5: Evaluation Insights & Strategic Justifications

### 1. Mean vs. Median vs. Mode (Outlier Robustness)



* **Why is Median Often Preferred Over Mean in the Presence of Outliers?**

1. **Algebraic Dependency of Mean:** The arithmetic mean calculates $\bar{x} = \frac{1}{n} \sum x_i$. Because it sums the magnitudes of every single observation, a single extreme outlier shifts the overall sum and pulls the mean away from the center of the distribution.


2. **Positional Character of Median:** The median depends strictly on the positional rank of sorted elements ($\frac{n+1}{2}$th item). Changing the value of an extreme point does not alter the center rank or the median value.


3. **Breakdown Point:** The median has a breakdown point of $50\%$, whereas the mean has a breakdown point of $0\%$ (meaning a single outlier can corrupt the statistic).




* **When to Use Which Metric:**

* **Mean:** Symmetric continuous data with no outliers (e.g., student heights, temperature sensor measurements).


* **Median:** Skewed data or distributions with extreme outliers (e.g., household incomes, property values, website page load latencies).


* **Mode:** Qualitative categorical/nominal data where numerical calculations are impossible (e.g., most popular car brand, blood type distribution).





---

### 2. Cosine Similarity vs. Euclidean Distance



(Exam Question Spring 2026, Q2c & Spring 2023, Q1b)

* **Mathematical Nature:**
* **Euclidean Distance ($L_2$):** Measures the absolute geometric distance between two coordinate points in Euclidean space: $d(x,y) = \sqrt{\sum (x_k - y_k)^2}$.


* **Cosine Similarity:** Measures the cosine of the angle $\theta$ between two vectors, normalizing for their magnitudes: $\cos(x, y) = \frac{x \cdot y}{\Vert{}x\Vert{} \Vert{}y\Vert{}}$.




* **Why They Lead to Different Interpretations:**

* Take vectors $D_1 = (1, 1)$ and $D_2 = (10, 10)$.


* **Cosine Similarity $= 1.0$ (Maximum Similarity):** Both vectors point in the identical directional ray ($\theta = 0^\circ$). In text mining, this indicates both documents discuss the same topics in the exact same proportion.


* **Euclidean Distance $= 12.73$ (Large Distance):** $D_2$ is ten times longer than $D_1$. Euclidean distance reflects raw length/frequency differences rather than conceptual overlap.





---

### 3. Outlier Analysis & Why It Is Important



* **What is Outlier Analysis?** It is the identification of data objects whose characteristics diverge significantly from the general statistical distribution or patterns governing the remainder of the dataset.


* **Why It Is Important:**

* **Data Quality Assurance:** Identifies measurement anomalies, faulty sensor hardware, or data transcription errors that need to be cleaned before model training.


* **Valuable Rare Event Detection:** In many domains, outliers represent the primary signal of interest rather than noise, including **credit card transaction fraud**, **network intrusion detection (cyberattacks)**, **industrial machinery failure warnings**, and **malignant medical tumors**.





---

### 4. Correlation vs. Regression & The "Price vs. Demand" Anomaly



* **Correlation vs. Regression Distinction:**

* **Correlation ($r$):** Symmetrically evaluates the strength and direction of linear association between two continuous variables ($X$ and $Y$) without assuming cause and effect.


* **Linear Regression:** Asymmetrically models the functional predictive dependency of a continuous response variable $Y$ based on changes in predictor variable $X$ ($y = \beta_0 + \beta_1 x$).




* **Scatterplot Scenario: "যত Price বাড়ে, Demand বাড়ে" (As Price Increases, Demand Increases):**

* **Economic Baseline:** Under typical market conditions, the Law of Demand yields a downward-sloping scatterplot and a negative correlation ($r < 0$): as prices increase, demand decreases.


* **Positive Trend Interpretation:** When data points produce an upward-sloping scatterplot from bottom-left to top-right ($r > 0$, $\beta_1 > 0$):


* **Veblen Goods:** Luxury or status items (e.g., exotic cars, luxury jewelry) where higher prices increase prestige and drive higher demand.


* **Speculative Markets:** Financial assets or real estate bubbles where price growth attracts speculative buyer demand.


* **Giffen Goods:** Non-luxury staples where rising prices and income constraints force consumers to substitute away from expensive foods toward the staple.







---

### 5. Retail Strategy from Association Rules



Given rule $B \rightarrow C$ with high confidence:

1. **Adjacency / Proximity:** Place product $C$ immediately adjacent to product $B$ on retail shelves to facilitate cross-purchases.


2. **Anchor Separation:** Position staple item $B$ at the back of the store and place high-margin item $C$ along the main pathway to increase exposure.


3. **Product Bundling:** Bundle $B$ and $C$ together at a slight discount to increase inventory turnover of $C$.


4. **Conditional Coupons:** Issue discount vouchers for product $C$ at checkout when a customer purchases item $B$.