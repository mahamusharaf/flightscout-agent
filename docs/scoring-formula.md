# FlightScout Mathematical Utility Scoring Model 📐

FlightScout ranks flight offers using a deterministic Multi-Attribute Utility Theory (MAUT) model. Each flight offer $i$ receives a composite score $S_i \in [0, 100]$.

## Sub-Score Formulations

### 1. Price Score ($S_{price}$)
The price sub-score uses min-max inverse linear scaling against the current search result pool:
$$S_{price} = 100 \times \left(1 - \frac{P_i - P_{min}}{P_{max} - P_{min}}\right)$$
*Where $P_i$ is the flight's total price, $P_{min}$ is the minimum price found, and $P_{max}$ is the maximum price.*

### 2. Speed / Duration Score ($S_{duration}$)
Similarly, travel duration is scaled inversely:
$$S_{duration} = 100 \times \left(1 - \frac{D_i - D_{min}}{D_{max} - D_{min}}\right)$$
*Where $D_i$ is total flight duration in minutes.*

### 3. Layover Score ($S_{layover}$)
Direct non-stop flights are prioritized heavily:
- **0 Layovers (Nonstop)**: 100 points
- **1 Layover**: 70 points
- **2+ Layovers**: 35 points

### 4. Schedule Match Score ($S_{schedule}$)
Evaluates departure time against user time-of-day preferences (Morning: 06:00-12:00, Afternoon: 12:00-18:00, Evening: 18:00-24:00):
- **Exact Match**: 100 points
- **No Preference Specified / Adjacent**: 80 points
- **Mismatched**: 50 points

Comfort subscore is defined as:
$$S_{comfort} = 0.6 \times S_{layover} + 0.4 \times S_{schedule}$$

---

## Composite Utility Formula

Using user preference weights $w_{price}, w_{speed}, w_{comfort}$ (normalized such that $\sum w = 1.0$):

$$\text{Overall Score } S_i = w_{price} \cdot S_{price} + w_{speed} \cdot S_{duration} + w_{comfort} \cdot S_{comfort}$$

Offers are sorted descending by $S_i$, and top performers are granted badges (*Top Pick ⭐*, *Cheapest 💰*, *Fastest ⚡*, *Best Value 💎*).
