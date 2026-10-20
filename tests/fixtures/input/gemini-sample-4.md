**Yes**, there are a few evaluation/tracing topics that appear in the **MAS PPTX (Segment 3)** and your syllabus, plus a few contextual evaluation formats that appeared in recent midterm exams.

Here is the complete breakdown of every remaining evaluation and tracing type you should be prepared for.

---

### 1. Longest Common Subsequence (LCS) DP Matrix Tracing (MAS PPTX Slide 61)

Even though LCS is an algorithms topic, it is explicitly listed in **Segment 3 of the syllabus** and has a full tracing slide in the MAS PPTX.

#### The Rules

Given two sequences $X$ of length $m$ and $Y$ of length $n$:

1. Initialize a grid of size $(m+1) \times (n+1)$ with zeros in the first row and column.


2. For each cell $(i, j)$:
* If characters match ($X[i] == Y[j]$):

$$C[i, j] = C[i-1, j-1] + 1 \quad (\text{arrow points diagonally: } \nwarrow)$$


* If characters do not match ($X[i] \neq Y[j]$):

$$C[i, j] = \max(C[i-1, j], C[i, j-1]) \quad (\text{arrow points from the larger neighbor: } \uparrow \text{ or } \leftarrow)$$





#### Exact Example from Slide 61: $X = \text{BACDB}$, $Y = \text{BDCB}$

|  |  | **$\emptyset$** | **B** | **D** | **C** | **B** |
| --- | --- | --- | --- | --- | --- | --- |
|  |  | $j=0$ | $j=1$ | $j=2$ | $j=3$ | $j=4$ |
| **$\emptyset$** | $i=0$ | **0** | **0** | **0** | **0** | **0** |
| **B** | $i=1$ | **0** | **$1 \ (\nwarrow)$** | $1 \ (\leftarrow)$ | $1 \ (\leftarrow)$ | $1 \ (\nwarrow)$ |
| **A** | $i=2$ | **0** | $1 \ (\uparrow)$ | $1 \ (\uparrow)$ | $1 \ (\uparrow)$ | $1 \ (\uparrow)$ |
| **C** | $i=3$ | **0** | $1 \ (\uparrow)$ | $1 \ (\uparrow)$ | **$2 \ (\nwarrow)$** | $2 \ (\leftarrow)$ |
| **D** | $i=4$ | **0** | $1 \ (\uparrow)$ | $2 \ (\nwarrow)$ | $2 \ (\uparrow)$ | $2 \ (\uparrow)$ |
| **B** | $i=5$ | **0** | $1 \ (\nwarrow)$ | $2 \ (\uparrow)$ | $2 \ (\uparrow)$ | **$3 \ (\nwarrow)$** |

* **Backtracking for the Subsequence:**
* Start at $C[5, 4] = 3$ ($X[5]=\text{B}, Y[4]=\text{B} \implies$ match: **B**, move to $C[4, 3]$).


* At $C[4, 3] = 2$, move up to $C[3, 3]$.


* At $C[3, 3] = 2$ ($X[3]=\text{C}, Y[3]=\text{C} \implies$ match: **C**, move to $C[2, 2]$).


* At $C[2, 2] = 1$, move up to $C[1, 2]$.


* At $C[1, 1] = 1$ ($X[1]=\text{B}, Y[1]=\text{B} \implies$ match: **B**).




* **Length of LCS:** **3**

* **LCS Result:** **`BCB`**


---

### 2. Matrix-Chain Multiplication Evaluation (MAS PPTX Slides 46–47)

This topic tests two specific calculations:

#### Evaluation A: Multiplication Cost

If matrix $A$ has dimension $p \times q$ and matrix $B$ has dimension $q \times r$:

* They can be multiplied because columns of $A$ equal rows of $B$ ($q = q$).


* Result matrix $C$ has dimension $p \times r$.


* **Total scalar multiplications required:**

$$\text{Cost} = p \times q \times r$$




**Slide 46 Example:** Matrix $A$ is $5 \times 4$, Matrix $B$ is $4 \times 3$.


$$\text{Cost} = 5 \times 4 \times 3 = 60\text{ multiplications}$$

#### Evaluation B: Number of Parenthesization Ways (Catalan Numbers)

The number of ways to parenthesize a chain of $n$ matrices (or the number of full binary trees with $n$ leaf nodes) is given by Catalan numbers:


$$T(n) = \frac{1}{n+1} \binom{2n}{n} = \frac{(2n)!}{(n+1)! \, n!}$$

* For $n = 3$ matrices:

$$T(3) = \frac{1}{4} \binom{6}{3} = \frac{20}{4} = 5\text{ ways}$$


* For $n = 4$ matrices:

$$T(4) = \frac{1}{5} \binom{8}{4} = \frac{70}{5} = 14\text{ ways}$$



---

### 3. Scenario-Based Multiplication Word Problems (Autumn 2025, Q3.a)

In Autumn 2025, the exam disguised standard multiplication tracing inside real-world scenarios:

* **Scenario A:** *"A cloud storage provider charges 12 taka per GB of storage. A company wants to buy 25 GB of storage space. Using the flow diagram of the final method of multiplication, calculate the total cost."*

* **What it is asking:** Multiply $12_{10} \times 25_{10}$ ($0000\ 1100_2 \times 0001\ 1001_2$) using the **Final Version Multiplication Algorithm** (tracing table and flowchart steps) to find the total: $300\text{ taka}$.




* **Scenario B:** *"An old AMD AI handles 4 requests/second. How many requests will it handle in 5 seconds? By showing the flowchart of the first method of multiplication, describe the steps."*

* **What it is asking:** Compute $4 \times 5 = 20$ using the **First Version Multiplication Algorithm** with its 64-bit shifting multiplicand and 32-bit shifting multiplier.





---

### 4. Memory Read / Fetch Cycle Register Sequence (Spring 2022, Q3.a)

**Question:** *"Mention the registers used in a read operation from memory (RAM) and how?"*

#### The Registers Involved



* **PC (Program Counter):** Holds the address of the next instruction.


* **MAR (Memory Address Register):** Holds the memory address that the CPU wants to read from or write to.


* **MDR (Memory Data Register):** Holds data fetched from (or being sent to) memory.


* **IR / CIR (Current Instruction Register):** Holds the fetched instruction while it is being decoded.



#### The Step-by-Step Read Sequence

1. **Address Setup:** The address to read (from the PC or an address calculation) is copied into the **MAR**:

$$\text{MAR} \leftarrow \text{Address}$$


2. **Control Bus Signal:** The Control Unit asserts the **Read** control signal on the control bus.


3. **Data Transfer:** Memory retrieves the contents at the address specified by the MAR and places the data on the data bus, which latches into the **MDR**:

$$\text{MDR} \leftarrow \text{Memory}[\text{MAR}]$$


4. **Placement:** The data in the MDR is copied to the destination register (for a load word instruction) or into the **IR/CIR** (if fetching an instruction).



---

### 5. Summary Checklist of All Exam Math/Evaluation Types

* **Cluster 1:**
* Multi-class instruction mix CPI, execution time, and compiler speedup.


* The MIPS vs. runtime contradiction.


* Target clock frequency scaling ($T = \frac{I \times \text{CPI}}{f}$).


* Amdahl's Law speedups and physical limits.


* UNIX `time` command CPU utilization percentages.




* **Cluster 2:**
* Assembly to 32-bit binary and hex machine code translation (`add`, `sw`, `lw`, `beq`, `bne`, `sll`, `j`).


* Reverse decoding 32-bit machine code back to assembly.


* PC-relative branch offsets and pseudodirect jump target calculations.


* Variable aliasing fault analysis.


* Loading 32-bit constants via `lui` and `ori`.




* **Cluster 3:**
* IEEE 754 Single & Double precision representation (positive, negative, pure fraction, mixed integer-fraction).


* Step-by-step Multiplication trace table (1st version and Final version).


* Step-by-step Division trace table (1st version restoring division and Final version).


* Two's complement subtraction with overflow verification.




* **Remaining Slide Topics:**
* LCS DP table tracing.


* Matrix-chain scalar multiplication cost and Catalan parenthesization.





With these covered, you have addressed **100% of all potential mathematical and evaluation questions** across the midterm syllabus and previous exam papers.