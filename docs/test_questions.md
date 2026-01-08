# Test Questions and Expected Answers

This document provides sample test questions and expected answers for validating the Document Q&A Assistant.

## Test Document: "Attention Is All You Need" (Transformer Paper)

*Note: These questions are based on the famous Transformer paper. Upload this paper to test the system.*

### Test Case 1: Direct Factual Question

**Question:** What is the main architecture proposed in the paper?

**Expected Answer:** The paper proposes the Transformer architecture, which is based entirely on attention mechanisms and dispenses with recurrence and convolutions entirely.

**Expected Citation:** [Document: attention_paper.pdf, Page: 1-2]

---

### Test Case 2: Technical Detail Question

**Question:** What are the key components of the Transformer model?

**Expected Answer:** The key components include:
- Multi-Head Attention mechanism
- Position-wise Feed-Forward Networks
- Positional Encoding
- Encoder-Decoder structure with 6 layers each

**Expected Citation:** [Document: attention_paper.pdf, Page: 2-3]

---

### Test Case 3: Numerical Information

**Question:** How many attention heads are used in the base model?

**Expected Answer:** The base model uses 8 parallel attention heads (h = 8).

**Expected Citation:** [Document: attention_paper.pdf, Section: Model Architecture]

---

### Test Case 4: Comparison Question

**Question:** How does the Transformer compare to RNN-based models in training time?

**Expected Answer:** The Transformer significantly reduces training time compared to RNN-based models due to parallelization. While RNNs process sequences sequentially, the Transformer can process all positions simultaneously during training.

**Expected Citation:** [Document: attention_paper.pdf, Section: Training / Results]

---

### Test Case 5: Not Found Response

**Question:** What is the stock price of Google mentioned in the paper?

**Expected Answer:** I couldn't find this information in the uploaded document.

**Expected Citation:** None (no sources should be shown)

---

## Test Document: Sample Business Report (DOCX)

*Create a sample business report for these tests.*

### Test Case 6: Section-Based Question

**Question:** What were the Q3 revenue figures?

**Expected Answer:** [Answer depends on your test document content]

**Expected Citation:** [Document: report.docx, Section: Financial Results]

---

### Test Case 7: Multi-Document Question

*Upload multiple documents for this test.*

**Question:** What are the common themes across both documents?

**Expected Answer:** [Should synthesize information from multiple documents with citations to each]

---

## Test Document: Markdown File

*Create a simple markdown file with technical documentation.*

### Test Case 8: Markdown Headers

**Question:** What are the installation steps?

**Expected Answer:** [Should extract content from the Installation section of the markdown]

**Expected Citation:** [Document: readme.md, Section: 'Installation']

---

## Edge Cases

### Test Case 9: Empty Knowledge Base

**Condition:** No documents uploaded

**Question:** Any question

**Expected Answer:** No documents have been uploaded yet. Please upload a document first.

---

### Test Case 10: Ambiguous Question

**Question:** What?

**Expected Answer:** Could provide a general summary or ask for clarification. Should still be grounded in document content if available.

---

### Test Case 11: Very Long Question

**Question:** [250+ word question with multiple sub-questions]

**Expected Behavior:** Should still process and provide a relevant answer, focusing on the main question.

---

## Validation Checklist

| Test | Description | Pass Criteria |
|------|-------------|---------------|
| Upload PDF | Upload and index PDF | Shows success, appears in document list |
| Upload DOCX | Upload and index DOCX | Shows success, appears in document list |
| Upload TXT | Upload and index TXT | Shows success, appears in document list |
| Upload MD | Upload and index Markdown | Shows success, appears in document list |
| Basic Q&A | Ask question about content | Accurate answer with citations |
| Citation Display | Check source panel | Shows document name, page/section |
| Not Found | Ask unrelated question | Shows "couldn't find" message |
| Clear Chat | Click Clear Chat | Empties chat history |
| Reset KB | Click Reset KB | Removes all documents |
| Top-K Slider | Change slider value | Different number of sources shown |
| Delete Document | Click delete button | Document removed from list |

## Performance Benchmarks

| Metric | Target |
|--------|--------|
| Document Processing | < 30 seconds for 10-page PDF |
| Query Response | < 5 seconds |
| Accuracy | > 80% correct answers for in-document questions |
| Citation Precision | 100% citations reference correct documents |
