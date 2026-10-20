In the exam, multiplication tracing questions ask for either the **Final (Refined) Version** (most common) or the **First Version**. Below is the step-by-step method to fill out each table using $2_{10} \times 3_{10} = 6_{10}$ ($0010_2 \times 0011_2$).

---

### Method 1: The Final (Refined) Version

This version eliminates the separate multiplier register. The Multiplicand stays stationary (4 bits), and the Product register (8 bits) holds both the accumulating sum (left 4 bits) and the multiplier (right 4 bits).

#### Setup Rules

* **Multiplicand (4 bits):** $2_{10} = 0010_2$ (never shifts, never changes).


* **Product Register (8 bits):** Initialized to `[0000] [Multiplier]` $\rightarrow$ `0000 0011`.


* **Two Steps per Iteration:**
1. **Test LSB (`Product0`):** Look at the very last bit of the Product register.


* If **`1`**: Add Multiplicand to the **left 4 bits** of the Product register.


* If **`0`**: No operation (skip addition).




2. **Shift Right:** Shift the **entire 8-bit Product register right by 1 bit** (fill the leftmost bit with `0`).





---

#### The Tracing Table

| Iteration | Step | Multiplicand | Product Register | What Happens |
| --- | --- | --- | --- | --- |
| **0** | Initial values | `0010` | `0000 0011` | Left half = 0, Right half = Multiplier (`0011`).

 |
| **1** | 1a: $\text{LSB}=1 \implies \text{Add}$ | `0010` | `0010 0011` | Look at LSB (`1`): Add Mcand to left half (`0000 + 0010 = 0010`).

 |
|  | 2: Shift Right Product | `0010` | `0001 0001` | Shift whole 8 bits right by 1 bit (`0010 0011` $\rightarrow$ `0001 0001`).

 |
| **2** | 1a: $\text{LSB}=1 \implies \text{Add}$ | `0010` | `0011 0001` | Look at LSB (`1`): Add Mcand to left half (`0001 + 0010 = 0011`).

 |
|  | 2: Shift Right Product | `0010` | `0001 1000` | Shift whole 8 bits right by 1 bit (`0011 0001` $\rightarrow$ `0001 1000`).

 |
| **3** | 1: $\text{LSB}=0 \implies \text{No op}$ | `0010` | `0001 1000` | Look at LSB (`0`): Do nothing.

 |
|  | 2: Shift Right Product | `0010` | `0000 1100` | Shift whole 8 bits right by 1 bit (`0001 1000` $\rightarrow$ `0000 1100`).

 |
| **4** | 1: $\text{LSB}=0 \implies \text{No op}$ | `0010` | `0000 1100` | Look at LSB (`0`): Do nothing.

 |
|  | 2: Shift Right Product | `0010` | **`0000 0110`** | Shift whole 8 bits right by 1 bit (`0000 1100` $\rightarrow$ `0000 0110`).

 |

* **Final Result:** `0000 0110` $= 6_{10}$ (Correct: $2 \times 3 = 6$).



---

### Method 2: The First Version

In this version, all 3 registers exist separately.

#### Setup Rules

* **Multiplicand (8 bits):** Starts in the right half $\rightarrow$ `0000 0010` (shifts **Left** 1 bit each iteration).


* **Multiplier (4 bits):** `0011` (shifts **Right** 1 bit each iteration).


* **Product (8 bits):** Initialized to `0000 0000`.


* **Three Steps per Iteration:**
1. **Test `Multiplier0`:** If the LSB of Multiplier is `1`, do $\text{Product} = \text{Product} + \text{Multiplicand}$. If `0`, do nothing.


2. **Shift Multiplicand Left 1 bit**.


3. **Shift Multiplier Right 1 bit**.





---

#### The Tracing Table

| Iteration | Step | Multiplier | Multiplicand | Product | What Happens |
| --- | --- | --- | --- | --- | --- |
| **0** | Initial values | `0011` | `0000 0010` | `0000 0000` | Starting setup.

 |
| **1** | 1a: $\text{LSB}=1 \implies \text{Add}$ | `0011` | `0000 0010` | `0000 0010` | $\text{Prod} = 0000\ 0000 + 0000\ 0010 = 0000\ 0010$.

 |
|  | 2: Shift Left Mcand | `0011` | `0000 0100` | `0000 0010` | Multiplicand shifted left 1 bit.

 |
|  | 3: Shift Right Mplier | `0001` | `0000 0100` | `0000 0010` | Multiplier shifted right 1 bit.

 |
| **2** | 1a: $\text{LSB}=1 \implies \text{Add}$ | `0001` | `0000 0100` | `0000 0110` | $\text{Prod} = 0000\ 0010 + 0000\ 0100 = 0000\ 0110$.

 |
|  | 2: Shift Left Mcand | `0001` | `0000 1000` | `0000 0110` | Multiplicand shifted left 1 bit.

 |
|  | 3: Shift Right Mplier | `0000` | `0000 1000` | `0000 0110` | Multiplier shifted right 1 bit.

 |
| **3** | 1: $\text{LSB}=0 \implies \text{No op}$ | `0000` | `0000 1000` | `0000 0110` | LSB is 0, skip addition.

 |
|  | 2: Shift Left Mcand | `0000` | `0001 0000` | `0000 0110` | Multiplicand shifted left 1 bit.

 |
|  | 3: Shift Right Mplier | `0000` | `0001 0000` | `0000 0110` | Multiplier shifted right 1 bit.

 |
| **4** | 1: $\text{LSB}=0 \implies \text{No op}$ | `0000` | `0001 0000` | `0000 0110` | LSB is 0, skip addition.

 |
|  | 2: Shift Left Mcand | `0000` | `0010 0000` | `0000 0110` | Multiplicand shifted left 1 bit.

 |
|  | 3: Shift Right Mplier | `0000` | `0010 0000` | **`0000 0110`** | Multiplier shifted right 1 bit.

 |

* **Final Result:** `0000 0110` $= 6_{10}$.



---

### Key Takeaways for the Exam

1. **How many iterations?** If the numbers are 4-bit, trace exactly **4 iterations**.


2. **Direction check:**
* In the **1st Version**: Multiplicand shifts **LEFT**, Multiplier shifts **RIGHT**.


* In the **Final Version**: Only the Product register shifts, and it shifts **RIGHT**.




3. **Addition check:** In the Final Version, when adding, add only to the **left 4 bits** of the Product register. Never touch the right 4 bits during addition—those bits hold the remaining multiplier bits.