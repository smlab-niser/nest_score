# Exam Results Processor

Python application for processing competitive exam results with SMAS calculations, percentiles, and category-based ranking.

## Required Input Columns

**Basic Info**: Name, Gender, Participant ID, Application Seq No, Email, Mobile No  
**Location**: State, Exam City, Exam State  
**Category**: Category (GEN/OBC/SC/ST/EWS), JK-Status, PWD-Status  
**Exam**: Session_No  
**Marks**: Bio Marks, Chem Marks, Math Marks, Phy Marks  

## Generated Output

**Calculated**: Total Marks (best 3/4), Max Subject Mark, Percentile  
**Ranks**: Gen-rank, Cat-rank, JK-rank, PWD-rank, EWS-rank  
**Qualification**: SMAS Qualified Subjects count  

## SMAS & Qualification Rules

**SMAS** (Subject-wise Minimum Admissible Score):
- GEN: 20%, OBC: 18%, SC/ST: 10% of top 100 average per subject
- PWD: 50% reduction applied

**Qualification Requirements**:
- Must qualify in 3+ subjects (meet SMAS)
- Minimum percentiles: GEN/EWS (95th), OBC (90th), SC/ST/PWD (75th)

## Usage

```python
python nest_score.py
```

## Requirements
- Python 3.7+, pandas, numpy
- Input: CSV with required columns
- Output: Processed CSV + console statistics
