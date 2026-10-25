# TRUTHLENS Methodology & Investigation Protocol

## The Decoupling Principle

In visual misinformation research, the central trap is equating **image authenticity** with **claim accuracy**:

1. **Authentic Image, False Caption (Misattribution)**:
   A real news photograph taken in central Mumbai during July 2019 is circulated with the caption: *"This photograph shows flooding in Pune today."* An AI deepfake detector will correctly classify the photograph as authentic, but the overall claim is completely false.

2. **Synthetic Image, Factual Claim**:
   An AI-generated graphic illustrating global warming or storm clouds is shared alongside accurate meteorological statistics. The image is synthetic, but the underlying claim might be verified.

TRUTHLENS evaluates image provenance and claim assertions as separate forensic tasks before synthesizing them into an investigative dossier.

---

## 5-Factor Source Credibility Metric

Every retrieved document passage is evaluated across five transparent criteria:

| Factor | Weight | Evaluation Method |
|---|---|---|
| **Identifiable Publisher** | 25% | Checks domain presence against established wire services, civic registries, or verified fact-checking networks. |
| **Documented Timestamp** | 20% | Requires ISO-compatible publication date. Undated pages receive a transparency penalty. |
| **Primary Record Linkage** | 20% | Evaluates whether the report references direct civic or eyewitness dispatches. |
| **Passage Relevance** | 20% | Semantic cosine similarity and named entity overlap between claim and excerpt. |
| **Editorial Stance** | 15% | Measures direct confirmation or refutation vs speculative commentary. |

---

## Epistemic Abstention

The platform never assumes that missing evidence constitutes proof of falsehood:
- If a user uploads an image of a fallen tree in a residential neighborhood and enters a hyper-local claim, the platform will return **Insufficient Corroborating Evidence**.
- It highlights what is missing (e.g., municipal service records) rather than declaring the photo "fake".
