# Exam Results Processor

A Python application for processing competitive exam results, calculating SMAS (Subject-wise Minimum Admissible Score), percentiles, and assigning ranks across different categories.

## Required Input Columns

The input CSV file must contain the following columns:

### Basic Information
- **Name**: Full name of the candidate
- **Gender**: Gender of the candidate
- **Participant ID**: Unique identifier for each participant
- **Application Seq No**: Application sequence number
- **Email**: Email address of the candidate
- **Mobile No**: Mobile number of the candidate

### Location Information
- **State**: State of the candidate
- **Exan City**: City where the exam was conducted
- **Exam State**: State where the exam was conducted

### Category Information
- **Category**: Category of the candidate (GEN, OBC, SC, ST, EWS)
- **JK-Status**: Jammu & Kashmir status (Yes/No)
- **PWD-Status**: Person with Disability status (Yes/No)

### Exam Information
- **Session_No**: Session number for the exam

### Subject Marks (Required for calculations)
- **Bio Marks**: Biology marks obtained
- **Chem Marks**: Chemistry marks obtained
- **Math Marks**: Mathematics marks obtained
- **Phy Marks**: Physics marks obtained

## Generated Output Columns

The processor adds the following calculated columns:

### Calculated Scores
- **Total Marks**: Sum of best 3 out of 4 subject marks
- **Max Subject Mark**: Highest mark among all subjects
- **Percentile**: Percentile score based on total marks

### Rank Categories
- **Gen-rank**: General rank (for all qualified candidates)
- **Cat-rank**: Category-specific rank (OBC-1, SC-2, ST-3, etc.)
- **JK-rank**: Jammu & Kashmir quota rank
- **PWD-rank**: Person with Disability quota rank
- **EWS-rank**: Economically Weaker Section rank

### Qualification Status
- **SMAS Qualified Subjects**: Number of subjects meeting SMAS criteria

## SMAS Calculation

Subject-wise Minimum Admissible Score (SMAS) is calculated as:
- **GEN**: 20% of average of top 100 scores in each subject
- **OBC**: 18% of average of top 100 scores in each subject
- **SC**: 10% of average of top 100 scores in each subject
- **ST**: 10% of average of top 100 scores in each subject

For PWD candidates, SMAS is reduced by 50%.

## Qualification Criteria

### General Rank Qualification
- Must qualify in at least 3 out of 4 subjects (meet SMAS criteria)
- Must achieve minimum percentile:
  - **GEN**: 95th percentile
  - **OBC**: 90th percentile
  - **SC**: 75th percentile
  - **ST**: 75th percentile
  - **PWD**: 75th percentile

### Category Rank Qualification
- **OBC**: 90th percentile + 3 subjects qualified
- **SC**: 75th percentile + 3 subjects qualified
- **ST**: 75th percentile + 3 subjects qualified

### Other Ranks
- **EWS**: 95th percentile + 3 subjects qualified
- **PWD**: 75th percentile + 3 subjects qualified
- **JK**: Must first qualify for General rank

## Usage

```python
from exam_processor import process_exam_results

# Process exam results
results = process_exam_results('provisional.csv', 'output_results.csv')
```

## Input File Format

The input CSV should be named `provisional.csv` (or specify custom path) and must contain all the required columns listed above. Missing values will be handled as follows:

- **Subject marks**: Filled with 0 and clipped to non-negative values
- **PWD-Status**: Filled with 'No'
- **JK-Status**: Filled with 'No'
- **Category**: Filled with 'GEN'

## Output

The processor generates:
1. **Console output**: SMAS scores, qualified candidates by category, and summary statistics
2. **CSV file**: Complete results with all calculated columns
3. **Statistics**: Number of ranks assigned in each category

## Example Console Output

```
=== SMAS SCORES ACROSS CATEGORIES ===
Bio Marks:
  GEN: 45.20
  OBC: 40.68
  SC: 22.60
  ST: 22.60

=== QUALIFIED CANDIDATES BY CATEGORY ===
OBC candidates who got ranks: 245
SC candidates who got ranks: 178
ST candidates who got ranks: 134
GEN/Other candidates who got ranks: 892
Total qualified candidates: 1449

=== FINAL SUMMARY ===
Total candidates processed: 6000
General ranks assigned: 1449
Category ranks assigned: 557
EWS ranks assigned: 89
PWD ranks assigned: 23
JK ranks assigned: 12
```

## Requirements

- Python 3.7+
- pandas
- numpy
