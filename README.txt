# Student job-board applications analysis (July-September 2026)

## Contents
- `analysis.py`: reproducible Python analysis.
- `job-board-applications.csv`: original supplied data.
- `cleaned_applications.csv`: one row per unique application ID.
- `source_hire_rates.csv`: source-level hires per 100 applications.
- `role_source_hire_rates.csv`: source results split by role.
- `step_completion_shortlisting.csv`: shortlisting by four-step completion.
- `paid_vs_unpaid_response.csv`: reply timing and no-reply share by stipend.
- `hire_rate_by_source.png`: chart for question 1.
- `manager_note.txt`: concise manager-ready findings.

## Run it again
Install dependencies: `pip install pandas matplotlib`
Then run: `python analysis.py job-board-applications.csv`

The script writes the cleaned data, result tables and chart beside the input file.
It checks that repeated application IDs are identical before removing duplicate rows.

## Definitions
- Hire rate = hires / applications * 100.
- Four-step group = `steps_done == 4`; comparison group = `steps_done < 4`.
- Paid = `stipend_inr_month > 0`; unpaid = stipend equals zero.
- Reply time statistics use only rows with a recorded `days_to_first_reply`.
- No-reply share = blank `days_to_first_reply` / all applications in that pay group.
- Missing source values are retained as unknown and excluded from source rankings.
